# Practica 7 - Integracion y despliegue continuo

Esta carpeta documenta el pipeline CI/CD de la plataforma de microservicios desarrollado en las practicas anteriores. El workflow principal se encuentra en `.github/workflows/p7-ci-cd.yml` porque GitHub Actions solamente reconoce workflows ubicados en ese directorio.

## Flujo implementado

1. Prepara una version basada en el tag o en el SHA del commit y valida la distribucion minima de 70 % de pruebas unitarias y 20 % de integracion.
2. Compila en paralelo los servicios Go y los servicios/worker Python.
3. Ejecuta en paralelo las pruebas unitarias y de integracion de Go y Python.
4. Construye y publica las seis imagenes mediante una matriz Docker.
5. Cuando se crea un tag `v*`, se autentica con Google Cloud mediante Workload Identity Federation y despliega el chart de Helm en GKE.
6. Comprueba los rollouts y ejecuta smoke tests contra los cinco endpoints de salud del API Gateway.

El diagrama detallado se encuentra en [DIAGRAMA_PIPELINE.md](DIAGRAMA_PIPELINE.md).

## Disparadores

| Evento | Pruebas | Build | Push a GHCR | Deploy a GKE |
|---|---:|---:|---:|---:|
| Pull request | Si | Si | No | No |
| Push a `main` | Si | Si | Si | No |
| Tag `v*` | Si | Si | Si | Si |
| Ejecucion manual con `deploy=false` | Si | Si | Si | No |
| Ejecucion manual con `deploy=true` | Si | Si | Si | Si |

## Imagenes publicadas

Las imagenes se publican con una etiqueta inmutable igual al SHA completo del commit. Los pushes a `main` tambien generan `latest` y los tags `v*` generan una etiqueta con el nombre de la version.

- `ghcr.io/izabel05/sa-api-gateway`
- `ghcr.io/izabel05/sa-autenticacion-ms`
- `ghcr.io/izabel05/sa-catalogo-ms`
- `ghcr.io/izabel05/sa-prestamos-ms`
- `ghcr.io/izabel05/sa-multas-ms`
- `ghcr.io/izabel05/sa-cronjobs-worker`

Despues de la primera publicacion, configure cada paquete como **Public** desde GitHub: perfil, Packages, paquete, Package settings, Change visibility. Esto permite que los nodos de GKE descarguen las imagenes sin un `imagePullSecret`.

## Configuracion inicial de GitHub y Google Cloud

El pipeline utiliza credenciales temporales OIDC. No se debe crear ni guardar una llave JSON de una cuenta de servicio.

Desde Google Cloud Shell ejecute:

```bash
chmod +x P7/scripts/01-configure-workload-identity.sh
P7/scripts/01-configure-workload-identity.sh
```

El script muestra los valores que deben crearse en `Settings > Secrets and variables > Actions` del repositorio:

- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`

Estos identificadores no contienen contrasenas, pero se almacenan como Secrets para coincidir con la configuracion del workflow.

## Preparacion del cluster

La eliminacion del cluster de la Practica 6 tambien elimino el namespace y los Secrets de Kubernetes. Despues de recrear el cluster y configurar `kubectl`, ejecute desde Google Cloud Shell:

```bash
chmod +x P7/scripts/02-bootstrap-cluster.sh
P7/scripts/02-bootstrap-cluster.sh
```

El script solicita las cinco URL de Neon sin mostrarlas, genera un JWT aleatorio y crea el namespace con los metadatos que necesita Helm. Los valores sensibles solamente existen durante la ejecucion y se guardan directamente como Secrets de Kubernetes.

El pipeline comprueba que los siguientes Secrets existan antes del deploy:

- `auth-postgresql-credentials`
- `catalog-postgresql-credentials`
- `loans-postgresql-credentials`
- `fines-postgresql-credentials`
- `cronjobs-postgresql-credentials`
- `jwt-credentials`

## Primera ejecucion

1. Subir la estructura de P7 y el workflow a una rama.
2. Crear un pull request para obtener evidencia de las pruebas y builds.
3. Integrar el cambio en `main`; esto publica las seis imagenes.
4. Hacer publicos los paquetes de GHCR.
5. Recrear el cluster GKE siguiendo la guia de P6.
6. Ejecutar `02-bootstrap-cluster.sh` para recuperar namespace y Secrets.
7. Configurar Workload Identity Federation y los dos Secrets de Actions.
8. Crear y subir un tag, por ejemplo:

```bash
git tag -a v0.1.0 -m "Entrega Practica 7"
git push origin v0.1.0
```

El tag ejecuta el pipeline completo y despliega exactamente las imagenes construidas para ese commit.

## Evidencias de entrega

Guarde las capturas indicadas en `evidencias/README.md`. Nunca incluya valores de conexiones, tokens, contenido de Secrets ni credenciales en las capturas.

## Archivos principales

```text
P7/
|-- README.md
|-- DIAGRAMA_PIPELINE.md
|-- PREGUNTAS.md
|-- evidencias/
|   `-- README.md
`-- scripts/
    |-- 01-configure-workload-identity.sh
    |-- 02-bootstrap-cluster.sh
    `-- validate-test-distribution.py

.github/
`-- workflows/
    `-- p7-ci-cd.yml
```
