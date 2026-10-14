# Runbook: consumo rápido del SLO de disponibilidad

**Alerta:** `AvailabilityErrorBudgetFastBurn`  
**SLO:** 99.5 % de solicitudes sin respuestas 5xx en 30 días.

1. Confirmar el alcance con `sa:slo_availability:error_ratio_5m` por `service`, `route` y `revision`.
2. Revisar el Rollout y el AnalysisRun. Si la revisión candidata concentra los 5xx, abortar el Rollout.
3. Abrir en Grafana los logs del servicio usando el `trace_id` de una petición fallida y saltar a Tempo.
4. Validar dependencias, base de datos y RabbitMQ; no promover mientras el burn rate sea mayor a 1.
5. Declarar recuperación cuando la tasa permanezca bajo 0.5 % durante 15 minutos y documentar causa y tiempo.

Comandos:

```bash
kubectl argo rollouts get rollout api-gateway -n sa-p9
kubectl get analysisrun -n sa-p9
kubectl argo rollouts abort api-gateway -n sa-p9
```
