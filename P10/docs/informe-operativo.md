# Informe operativo — Práctica 10

## 1. Objetivo y alcance

Se instrumentaron `api-gateway`, `prestamos-ms`, `catalogo-ms` y `multas-ms` en `sa-p9`. La plataforma de observabilidad corre en GKE, namespace `observability`, y se administra desde GitOps.

## 2. Arquitectura

OpenTelemetry propaga trazas W3C; Prometheus obtiene métricas desde `ServiceMonitor`; el Collector envía logs JSON a Loki y trazas OTLP a Tempo. Grafana consulta los tres backends. Argo Rollouts consulta Prometheus para decidir la promoción.

## 3. SLO y presupuesto de error

- Disponibilidad: 99.5 % sin 5xx en una ventana de 30 días; presupuesto 0.5 %.
- Latencia: 95 % de solicitudes por debajo de 750 ms en 30 días; presupuesto 5 %.

Las reglas `sa:slo_*:error_budget_consumed` expresan el consumo relativo. Las alertas se activan al superar un burn rate de 14.4 durante dos minutos y enlazan runbooks accionables.

## 4. Entrega progresiva

`gateway-slo-prometheus` evalúa cada revisión candidata por su `rollouts-pod-template-hash`. Exige tasa 5xx menor a 5 % y p95 menor a 750 ms. Un generador continuo produce tráfico sobre el Service canario; no se utiliza un Job de éxito binario.

## 5. Experimento de falla

La falla elegida es degradación de latencia mediante `INJECT_LATENCY_MS`, diferente al experimento de P8. El síntoma esperado es p95 mayor a 750 ms; la causa se confirma en el span del gateway y en su log correlacionado. Argo Rollouts debe marcar el AnalysisRun como fallido y mantener la revisión estable.

## 6. Operación y recuperación

El operador inicia en el dashboard de señales doradas, reduce por revisión/servicio, navega a la traza y luego a logs. La recuperación consiste en revertir el valor declarativo en Git, sincronizar Argo CD y verificar que p95 y burn rate vuelvan al objetivo.
