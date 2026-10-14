import json
import logging
import os
import time
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, make_asgi_app
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


HTTP_REQUESTS = Counter(
    "library_http_requests_total",
    "Peticiones HTTP procesadas por los microservicios de la biblioteca.",
    ["service", "method", "route", "status_code", "version"],
)
HTTP_DURATION = Histogram(
    "library_http_request_duration_seconds",
    "Latencia HTTP observada por los microservicios de la biblioteca.",
    ["service", "method", "route", "version"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
FINES_CREATED = Counter(
    "library_fines_created_total",
    "Multas creadas, metrica de negocio.",
    ["service"],
)


class TraceJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        span_context = trace.get_current_span().get_span_context()
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": record.levelname,
            "service": os.getenv("OTEL_SERVICE_NAME", "multas-ms"),
            "message": record.getMessage(),
            "trace_id": format(span_context.trace_id, "032x") if span_context.is_valid else "",
            "span_id": format(span_context.span_id, "016x") if span_context.is_valid else "",
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_observability(app: FastAPI, service_name: str, version: str = "stable") -> None:
    os.environ.setdefault("OTEL_SERVICE_NAME", service_name)
    _configure_logging()
    _configure_tracing(service_name)

    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next):
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            route = request.scope.get("route")
            route_path = getattr(route, "path", request.url.path)
            HTTP_REQUESTS.labels(service_name, request.method, route_path, str(status_code), version).inc()
            HTTP_DURATION.labels(service_name, request.method, route_path, version).observe(
                time.perf_counter() - started
            )

    app.mount("/metrics", make_asgi_app())
    FastAPIInstrumentor.instrument_app(app, excluded_urls="health,metrics")


def _configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(TraceJSONFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())


def _configure_tracing(service_name: str) -> None:
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", "").strip()
    if not endpoint or isinstance(trace.get_tracer_provider(), TracerProvider):
        return
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(provider)
