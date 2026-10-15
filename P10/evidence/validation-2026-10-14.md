# Validación final — 2026-10-14

## Entorno

- Google Cloud: proyecto `p8202300582`.
- GKE: clúster `p9-202300582`, zona `us-central1-a`.
- Aplicación: namespace `sa-p9`; observabilidad: namespace `observability`.
- Versión validada: imágenes `v1.2.5`, construidas, analizadas, firmadas y publicadas por [GitHub Actions](https://github.com/Izabel05/Practicas-SA-B-202300582/actions/runs/38654115431).
- Estado final del Rollout `api-gateway`: `Healthy`, `2/2`, hash `6b8d4465cf`.

## Telemetría correlacionada

La traza `477f050345123797d0336e160cd657b` fue consultada en Tempo y contiene la cadena `api-gateway` (SERVER) → petición HTTP cliente → `catalogo-ms` (SERVER), conservando el mismo contexto W3C. Loki devolvió logs JSON de `sa-p9` con `trace_id` y `span_id`; un identificador observado fue `6f99688a07335aa7f1e57a00eb17fae7`. Prometheus reportó `up=1` para `api-gateway`, `prestamos-ms`, `catalogo-ms` y `multas-ms`.

El dashboard provisionado por sidecar fue verificado mediante la API de Grafana: UID `sa-p10-golden-signals`, `provisioned=true`, archivo externo `sa-p10-golden-signals.json` y ocho paneles. La captura de evidencia de configuración y estado está en [grafana-dashboard-api-evidence.png](grafana-dashboard-api-evidence.png); las consultas fuente están en [el JSON del dashboard](../dashboards/sa-p10-golden-signals.json).

## Canario, falla y reversión automática

| Etapa | Hash candidato | AnalysisRun | Resultado |
|---|---|---|---|
| Línea base sana | `66f69df695` | `api-gateway-66f69df695-5-2`, `-5`, `-8` | `Successful` |
| Falla inducida | `79f85c79fb` | `api-gateway-79f85c79fb-7-5` | `Failed`; p95 `2.411 s` > `0.750 s` |
| Recuperación GitOps | `6b8d4465cf` | `api-gateway-6b8d4465cf-8-2`, `-5`, `-8` | `Successful`; Rollout `Healthy 2/2` |

La falla se declaró en GitOps con `INJECT_LATENCY_MS=1200` (commit `3d914b7`) y no mediante cambios manuales al clúster. El AnalysisRun de la segunda etapa comenzó a las `23:43:23Z` y falló a las `23:43:33Z`: Prometheus midió p95 `2.411 s`, mientras la tasa de error permaneció en `0`. Argo Rollouts retiró el ReplicaSet candidato y conservó la versión estable. La detección ocurrió en aproximadamente 10 segundos desde el inicio de ese análisis. La recuperación también fue declarativa (`cf30d6c`) y superó los tres análisis 20/50/80.

Síntoma → causa → tiempo: **p95 por encima de 750 ms** → **latencia candidata de 1200 ms declarada en Git** → **detección y aborto en ~10 s durante el análisis fallido**.

## Estado GitOps final

- Commit GitOps funcional de recuperación: `cf30d6c`.
- Exclusión de selectores administrados por Rollouts: `be5dd08`.
- Retiro del acceso anónimo temporal usado para inspección: `1616a6a`.
- Aplicaciones de observabilidad: Prometheus/Grafana, Loki, Tempo y OpenTelemetry Collector administradas por Argo CD.
- `sa-platform-p9`: `Synced/Healthy`; recursos de aplicación en ejecución y generador de tráfico P10 activo.

La única evidencia externa que no puede producirse automáticamente es el video narrado de 5–8 minutos y su URL pública.
