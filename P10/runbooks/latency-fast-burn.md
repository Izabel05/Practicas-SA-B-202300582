# Runbook: consumo rápido del SLO de latencia

**Alerta:** `LatencyErrorBudgetFastBurn`  
**SLO:** 95 % de solicitudes con latencia menor a 750 ms en 30 días.

1. Comparar p50, p95 y p99 por `service`, `route` y `revision`.
2. Consultar trazas lentas en Tempo y localizar el span que explica la mayor duración.
3. Correlacionar el `trace_id` con Loki y revisar saturación de CPU/memoria y conexiones de base de datos.
4. Si afecta solo a la candidata, abortar el Rollout; si afecta a ambas revisiones, escalar como incidente de plataforma.
5. Verificar p95 menor a 750 ms durante 15 minutos y registrar causa, mitigación y tiempo de recuperación.
