# Informe de incidente - fallo inducido

Incidente controlado ejecutado el 17 de septiembre de 2026. El documento se
mantiene dentro del límite de una página.

## Qué falló

El PR GitOps [#20](https://github.com/Izabel05/GItOps_202300582/pull/20)
publicó la revisión 11 con un upstream DNS inexistente para catálogo
(`catalogo-ms-invalid`). El defecto afectaba únicamente al nuevo ReplicaSet
canary `865bd5d457`; el estable continuó siendo `7fd7f76d74`.

## Cómo se detectó

El `AnalysisTemplate` `gateway-integration` comprobó los endpoints de salud de
autenticación, catálogo, préstamos y multas. El AnalysisRun
`api-gateway-865bd5d457-11-2` falló cuando la métrica
`gateway-downstream-integration` acumuló 2 fallos, superando `failureLimit: 1`.

## Cómo se contuvo

Argo Rollouts abortó automáticamente la revisión 11 durante el escalón de 20 %
y conservó `7fd7f76d74` como ReplicaSet estable. No fue necesario ejecutar
`kubectl set image`, `kubectl apply` ni `helm upgrade`. El PR GitOps
[#21](https://github.com/Izabel05/GItOps_202300582/pull/21) restauró después el
estado deseado correcto.

## Tiempo de recuperación

Aproximadamente 4 minutos: el cambio se fusionó a las 05:38 UTC y el Rollout
reportó `RolloutAborted` a las 05:42 UTC. La versión estable no dejó de atender.

## Cómo prevenirlo

Validar resolución DNS y conectividad de upstreams en un entorno efímero antes
de promover el PR GitOps. El análisis canary permanece como control de
contención cuando una dependencia falla solamente dentro del clúster.
