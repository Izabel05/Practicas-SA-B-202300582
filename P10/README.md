# Práctica 10 — Observabilidad, SLO y entrega progresiva

Proyecto GCP: `p8202300582` · clúster: `p9-202300582` · zona: `us-central1-a`  
Aplicación: namespace `sa-p9` · observabilidad: namespace `observability`

## Entregables

| Evidencia requerida | Recurso público |
|---|---|
| Repositorio de aplicación | [Practicas-SA-B-202300582](https://github.com/Izabel05/Practicas-SA-B-202300582) |
| Repositorio GitOps | [GItOps_202300582](https://github.com/Izabel05/GItOps_202300582) |
| Servicios instrumentados | `api-gateway`, `prestamos-ms`, `catalogo-ms`, `multas-ms` en `sa-p9` |
| Instrumentación | [P4/Backend](../P4/Backend) |
| OpenTelemetry Collector | [observability-otel-collector.yaml](https://github.com/Izabel05/GItOps_202300582/blob/main/argocd/applications/observability-otel-collector.yaml) |
| AnalysisTemplate | `gateway-slo-prometheus` en [analysis-template.yaml](https://github.com/Izabel05/GItOps_202300582/blob/main/charts/sa-platform/templates/analysis-template.yaml) |
| PromQL de canario | tasa 5xx `< 5 %`; p95 `< 750 ms`, filtrados por `rollouts-pod-template-hash` |
| SLO y PrometheusRule | [observability.yaml](https://github.com/Izabel05/GItOps_202300582/blob/main/charts/sa-platform/templates/observability.yaml) |
| Runbooks | [disponibilidad](runbooks/availability-fast-burn.md) · [latencia](runbooks/latency-fast-burn.md) |
| Dashboard JSON | [sa-p10-golden-signals.json](dashboards/sa-p10-golden-signals.json) |
| Flujo de telemetría | [telemetry-flow.md](diagrams/telemetry-flow.md) |
| Informe operativo | [informe-operativo.md](docs/informe-operativo.md) |
| Evidencia de GKE y rollback | [evidence](evidence/) |
| Video 5–8 minutos | Pendiente de grabación y URL pública por el estudiante |

## Diseño verificable

La cadena `api-gateway → prestamos-ms → catalogo-ms → RabbitMQ → multas-ms` propaga contexto W3C. Los servicios emiten métricas técnicas de tráfico, errores y latencia; métricas de negocio de préstamos, multas y cambios de estado; trazas OTLP; y logs JSON con `trace_id`/`span_id`.

Prometheus recolecta `/metrics` mediante `ServiceMonitor`. El Collector recoge logs de contenedores y trazas OTLP, enviándolos a Loki y Tempo. El dashboard Grafana reúne las cuatro señales doradas, consumo de presupuesto y métricas de negocio.

## SLO

1. **Disponibilidad:** 99.5 % de solicitudes sin 5xx en 30 días; presupuesto de error 0.5 %.
2. **Latencia:** 95 % de solicitudes por debajo de 750 ms en 30 días; presupuesto de error 5 %.

El burn rate se registra como consumo del presupuesto. Las alertas rápidas usan umbral `14.4` durante dos minutos y enlazan a los runbooks.

## Demostración de reversión

La falla de P10 introduce latencia en la revisión candidata con `INJECT_LATENCY_MS`. El generador continuo llama al Service canario, Prometheus observa p95 por hash de revisión y Argo Rollouts aborta sin promoverla cuando supera 750 ms. La recuperación se realiza revirtiendo el valor en Git y dejando que Argo CD sincronice el estado sano.

## Guion de video (5–8 min)

- 00:00–00:45: arquitectura, repositorios y namespaces.
- 00:45–02:00: instrumentación, propagación y Collector.
- 02:00–03:15: dashboard, SLO, error budget y alertas.
- 03:15–05:30: Rollout, AnalysisRun fallido y rollback automático.
- 05:30–06:30: correlación métrica → traza → log y causa.
- 06:30–07:00: recuperación por GitOps y estado final.
