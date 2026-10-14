package observability

import (
	"context"
	"net/http"
	"os"
	"strconv"
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
)

var (
	httpRequests = prometheus.NewCounterVec(prometheus.CounterOpts{
		Name: "library_http_requests_total",
		Help: "Peticiones HTTP procesadas por los microservicios de la biblioteca.",
	}, []string{"service", "method", "route", "status_code", "version"})
	httpDuration = prometheus.NewHistogramVec(prometheus.HistogramOpts{
		Name:    "library_http_request_duration_seconds",
		Help:    "Latencia HTTP observada por los microservicios de la biblioteca.",
		Buckets: []float64{0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5},
	}, []string{"service", "method", "route", "version"})
	CopyStatusChanges = prometheus.NewCounterVec(prometheus.CounterOpts{
		Name: "library_copy_status_changes_total",
		Help: "Cambios de estado de ejemplares, metrica de negocio.",
	}, []string{"service", "status"})
)

func init() {
	prometheus.MustRegister(httpRequests, httpDuration, CopyStatusChanges)
}

func InitTracing(ctx context.Context, serviceName string) (func(context.Context) error, error) {
	endpoint := os.Getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
	if endpoint == "" {
		return func(context.Context) error { return nil }, nil
	}
	exporter, err := otlptracehttp.New(ctx, otlptracehttp.WithEndpointURL(endpoint))
	if err != nil {
		return nil, err
	}
	res, err := resource.New(ctx,
		resource.WithAttributes(semconv.ServiceName(serviceName)),
		resource.WithFromEnv(),
	)
	if err != nil {
		return nil, err
	}
	provider := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exporter),
		sdktrace.WithResource(res),
	)
	otel.SetTracerProvider(provider)
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
		propagation.TraceContext{}, propagation.Baggage{},
	))
	return provider.Shutdown, nil
}

func Handler(serviceName, version string, next http.Handler) http.Handler {
	metrics := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		started := time.Now()
		writer := &statusWriter{ResponseWriter: w, status: http.StatusOK}
		next.ServeHTTP(writer, r)
		route := r.Pattern
		if route == "" {
			route = r.URL.Path
		}
		httpRequests.WithLabelValues(serviceName, r.Method, route, strconv.Itoa(writer.status), version).Inc()
		httpDuration.WithLabelValues(serviceName, r.Method, route, version).Observe(time.Since(started).Seconds())
	})
	mux := http.NewServeMux()
	mux.Handle("GET /metrics", promhttp.Handler())
	mux.Handle("/", otelhttp.NewHandler(metrics, serviceName+".http"))
	return mux
}

type statusWriter struct {
	http.ResponseWriter
	status int
}

func (w *statusWriter) WriteHeader(status int) {
	w.status = status
	w.ResponseWriter.WriteHeader(status)
}
