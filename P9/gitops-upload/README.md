# GitOps P9

Este directorio contiene la versión P9 del repositorio GitOps de la plataforma.

## Estructura

- `argocd/app-of-apps.yaml`: aplicación raíz que observa las aplicaciones hijas.
- `argocd/applications/argo-rollouts.yaml`: instala Argo Rollouts para el despliegue progresivo.
- `argocd/applications/sa-platform-p9.yaml`: despliega el chart de la plataforma con `values-p9.yaml`.
- `charts/sa-platform`: chart Helm con microservicios, PostgreSQL persistente, secretos externos, políticas, PDB y anti-affinity.

## Flujo de bootstrap

1. Terraform crea el clúster, instala ArgoCD, External Secrets y Velero.
2. Se aplica `argocd/app-of-apps.yaml` una sola vez.
3. ArgoCD instala Argo Rollouts y sincroniza `sa-platform-p9`.
4. El chart crea el namespace `sa-p9`, las cuentas de servicio y los workloads.

El `repoURL` configurado es `https://github.com/Izabel05/GItOps_202300582.git` y el `targetRevision` es `main`. Antes de crear el clúster, estos archivos deben estar publicados en esa rama; mientras tanto se mantienen únicamente como cambios locales para evitar ejecuciones innecesarias de GitHub Actions.

Los secretos se leen desde Secret Manager mediante External Secrets usando el prefijo `p9-`. La base `auth-postgresql` usa un PVC y queda incluida en el backup programado de Velero del namespace `sa-p9`.
