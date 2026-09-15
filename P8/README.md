# Practica 8 - GitOps, entrega progresiva y seguridad

Esta carpeta contiene la implementación de P8 sobre los microservicios de P5,
P6 y P7. El repositorio de código es la fuente de los workflows y charts; el
repositorio GitOps independiente contiene los valores/manifiestos que ArgoCD
sincroniza con Kubernetes.

## Repositorios

| Elemento | URL o ubicación |
|---|---|
| Código y workflows | https://github.com/Izabel05/Practicas-SA-B-202300582 |
| Repositorio GitOps | https://github.com/Izabel05/GItOps_202300582 |
| Aplicación ArgoCD | `sa-platform-p8` / namespace `sa-p8` (pendiente de registrar) |

## Tabla de enlaces obligatoria

| Ítem | Enlace o dato requerido |
|---|---|
| Repositorio GitOps | https://github.com/Izabel05/GItOps_202300582 |
| Aplicación en ArgoCD | `sa-platform-p8`, namespace `sa-p8` |
| Ejecución exitosa del pipeline | Pendiente de ejecutar tag P8 |
| Reversión automática | Pendiente de ejecutar fallo inducido |
| Despliegue rechazado por política | Pendiente de evidencia Kyverno |
| Bloqueo por vulnerabilidad crítica | Pendiente de ejecutar Trivy con CVE crítica |
| Imagen firmada | `ghcr.io/izabel05/sa-<servicio>:vX.Y.Z` |
| Reporte de prueba de carga | No aplica: excluida del alcance actualizado |
| Video demostrativo | Pendiente de grabar; agregar URL y minutaje |

## Flujo implementado

```text
tag vX.Y.Z
  -> compilación y pruebas P7
  -> helm lint
  -> build de imágenes sin latest
  -> Trivy bloquea CRITICAL
  -> SBOM + firma Cosign
  -> PR automático al repositorio GitOps
  -> ArgoCD sincroniza
  -> Argo Rollouts: 20% -> 50% -> 80% -> 100%
  -> AnalysisTemplate valida disponibilidad mínima del canary
  -> promoción o rollback automático
```

## Componentes

- `charts/sa-platform`: chart Helm basado en P6, únicamente para la aplicación:
  Rollout/Deployments, Services, ConfigMaps, HPA, ExternalSecrets y políticas
  de ejecución. El canary y la versión estable conviven en `sa-p8`.
- `terraform`: reconstrucción del perfil Minikube de prueba y recursos de
  infraestructura Kubernetes: namespace, ResourceQuota, LimitRange, cuentas,
  Roles y RoleBindings.
- `policies/kyverno-policies.yaml`: las tres políticas obligatorias de P8.
- `.github/workflows/p8-gitops.yml`: pipeline sin kubeconfig ni despliegue
  directo; únicamente genera un PR de promoción al repositorio GitOps.

## Secretos

Los charts no generan secretos con valores en el repositorio. Se esperan siete
`ExternalSecret` respaldados por un `ClusterSecretStore` llamado
`cluster-secret-store`. Las claves remotas son `p8/<secret>/<key>` y deben
configurarse en el proveedor de secretos antes de sincronizar ArgoCD.

El pipeline requiere el secreto de GitHub Actions `GITOPS_TOKEN`, limitado al
repositorio `Izabel05/GItOps_202300582`, para abrir el PR automático.

## Validación local

```bash
helm dependency build P8/charts/sa-platform
helm lint P8/charts/sa-platform -f P8/charts/sa-platform/values-p8.yaml
terraform -chdir=P8/terraform init
terraform -chdir=P8/terraform validate
python P7/scripts/validate-test-distribution.py
```

## Evidencia pendiente

La ejecución real de Trivy/Cosign, el estado `Synced`/`Healthy` de ArgoCD y el
rollback inducido dependen de un clúster con ArgoCD, Argo Rollouts, Kyverno y
External Secrets instalados. En esta versión no se ejecutan pruebas de carga ni
pruebas de humo. El `AnalysisTemplate` solo actúa como compuerta mínima de
disponibilidad del canary para permitir promoción o rollback.

## Informe de incidente

Debe completarse en una página con exactamente cinco campos. La plantilla está
en `docs/informe-incidente.md`.
