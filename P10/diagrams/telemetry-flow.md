# Flujo de telemetría

```mermaid
flowchart LR
  U[Cliente] --> G[api-gateway canary/stable]
  G --> P[prestamos-ms]
  P --> C[catalogo-ms]
  P --> R[(RabbitMQ)] --> M[multas-ms]
  G & P & C & M -- OTLP trazas --> O[OpenTelemetry Collector]
  G & P & C & M -- /metrics --> PR[Prometheus]
  G & P & C & M -- JSON stdout --> O
  O --> T[Tempo]
  O --> L[Loki]
  PR & T & L --> GF[Grafana]
  PR --> AR[Argo Rollouts AnalysisRun]
  AR -->|error < 5% y p95 < 750 ms| PROM[Promover]
  AR -->|umbral incumplido| RB[Rollback automático]
```

La propagación W3C `traceparent` conserva un único contexto desde el gateway hasta catálogo y, mediante headers AMQP, hasta multas. Los logs JSON incluyen `trace_id` y `span_id` para navegar en ambos sentidos entre Loki y Tempo.
