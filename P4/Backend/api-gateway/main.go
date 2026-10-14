package main

import (
	"context"
	"encoding/json"
	"log/slog"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.37.0"
	"go.opentelemetry.io/otel/trace"
)

var requests = prometheus.NewCounterVec(prometheus.CounterOpts{Name: "library_http_requests_total", Help: "Peticiones HTTP de la biblioteca."}, []string{"service", "method", "route", "status_code", "version", "revision"})
var duration = prometheus.NewHistogramVec(prometheus.HistogramOpts{Name: "library_http_request_duration_seconds", Help: "Latencia HTTP de la biblioteca.", Buckets: []float64{.01, .025, .05, .1, .25, .5, .75, 1, 2.5, 5}}, []string{"service", "method", "route", "version", "revision"})

type statusWriter struct {
	http.ResponseWriter
	status int
}

func (w *statusWriter) WriteHeader(code int) { w.status = code; w.ResponseWriter.WriteHeader(code) }

func main() {
	shutdown, err := tracing(context.Background())
	if err != nil {
		panic(err)
	}
	defer shutdown(context.Background())
	prometheus.MustRegister(requests, duration)
	mux := http.NewServeMux()
	mux.Handle("GET /metrics", promhttp.Handler())
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, _ *http.Request) {
		json.NewEncoder(w).Encode(map[string]string{"status": "ok", "servicio": "api-gateway"})
	})
	proxy(mux, "/health/auth", "AUTENTICACION_URL", "http://autenticacion-ms:8081", "/health")
	proxy(mux, "/health/catalogo", "CATALOGO_URL", "http://catalogo-ms:8082", "/health")
	proxy(mux, "/health/prestamos", "PRESTAMOS_URL", "http://prestamos-ms:8083", "/health")
	proxy(mux, "/health/multas", "MULTAS_URL", "http://multas-ms:8084", "/health")
	proxyPrefix(mux, "/api/v1/auth/", "AUTENTICACION_URL", "http://autenticacion-ms:8081")
	proxyPrefix(mux, "/api/v1/ejemplares/", "CATALOGO_URL", "http://catalogo-ms:8082")
	proxyPrefix(mux, "/api/v1/prestamos/", "PRESTAMOS_URL", "http://prestamos-ms:8083")
	proxyPrefix(mux, "/api/v1/multas", "MULTAS_URL", "http://multas-ms:8084")
	mux.HandleFunc("/api/v1/usuarios/", func(w http.ResponseWriter, r *http.Request) {
		if strings.HasSuffix(r.URL.Path, "/multas") {
			newProxy("MULTAS_URL", "http://multas-ms:8084").ServeHTTP(w, r)
			return
		}
		http.NotFound(w, r)
	})
	proxy(mux, "/catalogo/graphql", "CATALOGO_URL", "http://catalogo-ms:8082", "/graphql")
	proxy(mux, "/prestamos/graphql", "PRESTAMOS_URL", "http://prestamos-ms:8083", "/graphql")
	slog.Info("gateway_started", "port", 8080)
	if err := http.ListenAndServe(":8080", otelhttp.NewHandler(observe(mux), "api-gateway.http")); err != nil {
		panic(err)
	}
}

func proxy(mux *http.ServeMux, route, envName, fallback, targetPath string) {
	mux.Handle(route, rewrite(newProxy(envName, fallback), targetPath))
}
func proxyPrefix(mux *http.ServeMux, route, envName, fallback string) {
	mux.Handle(route, newProxy(envName, fallback))
}
func newProxy(envName, fallback string) *httputil.ReverseProxy {
	p := httputil.NewSingleHostReverseProxy(upstream(envName, fallback))
	p.Transport = otelhttp.NewTransport(http.DefaultTransport)
	return p
}
func upstream(envName, fallback string) *url.URL {
	raw := os.Getenv(envName)
	if raw == "" {
		raw = fallback
	}
	u, err := url.Parse(raw)
	if err != nil {
		panic(err)
	}
	return u
}
func rewrite(next http.Handler, path string) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { r.URL.Path = path; next.ServeHTTP(w, r) })
}

func observe(next http.Handler) http.Handler {
	version, revision := env("SERVICE_VERSION", "stable"), env("POD_TEMPLATE_HASH", "unknown")
	failureMS, _ := strconv.Atoi(env("INJECT_LATENCY_MS", "0"))
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		started := time.Now()
		sw := &statusWriter{ResponseWriter: w, status: 200}
		if failureMS > 0 && !strings.HasPrefix(r.URL.Path, "/metrics") {
			time.Sleep(time.Duration(failureMS) * time.Millisecond)
		}
		next.ServeHTTP(sw, r)
		route := r.Pattern
		if route == "" {
			route = r.URL.Path
		}
		elapsed := time.Since(started).Seconds()
		requests.WithLabelValues("api-gateway", r.Method, route, strconv.Itoa(sw.status), version, revision).Inc()
		duration.WithLabelValues("api-gateway", r.Method, route, version, revision).Observe(elapsed)
		slog.InfoContext(r.Context(), "http_request", "method", r.Method, "route", route, "status", sw.status, "duration_seconds", elapsed, "trace_id", trace.SpanFromContext(r.Context()).SpanContext().TraceID().String())
	})
}

func env(name, fallback string) string {
	if value := os.Getenv(name); value != "" {
		return value
	}
	return fallback
}
func tracing(ctx context.Context) (func(context.Context) error, error) {
	endpoint := os.Getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
	if endpoint == "" {
		return func(context.Context) error { return nil }, nil
	}
	exporter, err := otlptracehttp.New(ctx, otlptracehttp.WithEndpointURL(endpoint))
	if err != nil {
		return nil, err
	}
	res, err := resource.New(ctx, resource.WithAttributes(semconv.ServiceName("api-gateway")), resource.WithFromEnv())
	if err != nil {
		return nil, err
	}
	provider := sdktrace.NewTracerProvider(sdktrace.WithBatcher(exporter), sdktrace.WithResource(res))
	otel.SetTracerProvider(provider)
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(propagation.TraceContext{}, propagation.Baggage{}))
	return provider.Shutdown, nil
}
