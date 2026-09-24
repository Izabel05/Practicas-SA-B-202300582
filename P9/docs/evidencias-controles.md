# Evidencias de controles heredados de P8 para P9

P9 conserva los controles de seguridad y despliegue progresivo de P8. Este
documento mantiene sus evidencias históricas; las evidencias específicas de
continuidad, Velero y restauración están descritas en `P9/README.md`.

## Rechazo de política Kyverno

El 17 de septiembre de 2026 se envió un Pod únicamente con
`--dry-run=server`; ningún recurso quedó persistido. Kyverno rechazó
`nginx:latest` por `p8-disallow-latest` y la ausencia de
`runAsNonRoot: true` por `p8-require-nonroot`.

```text
resource Pod/sa-p8/p8-policy-rejection-evidence was blocked
p8-disallow-latest: latest esta prohibido
p8-require-nonroot: runAsNonRoot=true es obligatorio
```

## Bloqueo de vulnerabilidad crítica

El PR de evidencia [#4](https://github.com/Izabel05/Practicas-SA-B-202300582/pull/4)
usó deliberadamente una base obsoleta y se cerró sin fusionar. En la
[ejecución #80](https://github.com/Izabel05/Practicas-SA-B-202300582/actions/runs/35186897878),
el job `api-gateway` falló exactamente en
`Bloquear vulnerabilidades criticas con Trivy`; las otras cinco imágenes
terminaron correctamente y el job de promoción GitOps fue omitido.

## Rollback automático

El fallo controlado está trazado en los PR GitOps
[#20](https://github.com/Izabel05/GItOps_202300582/pull/20) y
[#21](https://github.com/Izabel05/GItOps_202300582/pull/21). El AnalysisRun
`api-gateway-865bd5d457-11-2` terminó `Failed`; Argo Rollouts reportó
`RolloutAborted`, mantuvo estable `7fd7f76d74` y no promovió el canary.

No se ejecutaron pruebas de humo ni pruebas de carga.
