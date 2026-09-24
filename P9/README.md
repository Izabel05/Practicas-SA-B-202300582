# Práctica 9 - Continuidad operativa y recuperación ante desastres

## Objetivo

P9 conserva el backend funcional de P8 y agrega continuidad operativa para la
plataforma desplegada en GKE. Terraform crea la infraestructura, ArgoCD realiza
el bootstrap GitOps y Velero respalda y restaura los datos persistentes.

La prueba demuestra que el clúster puede reconstruirse mediante Terraform y que
los datos reales pueden recuperarse desde un respaldo almacenado fuera del
clúster.

## Componentes

| Componente | Función |
|---|---|
| Terraform | Crea red, clúster, node pool, cuentas de servicio y buckets. |
| Bootstrap | Instala ArgoCD, External Secrets y Velero, y aplica el app-of-apps. |
| ArgoCD | Sincroniza el repositorio GitOps con el namespace <code>sa-p9</code>. |
| PostgreSQL | Conserva datos reales en un PVC. |
| RabbitMQ | Conserva su cola en un PVC. |
| Velero | Realiza backups y restores de Kubernetes y de los PVC. |
| GCS | Almacena el estado remoto de Terraform y los backups de Velero. |

## Repositorios y configuración

| Elemento | Valor |
|---|---|
| Repositorio principal | https://github.com/Izabel05/Practicas-SA-B-202300582 |
| Repositorio GitOps | https://github.com/Izabel05/GItOps_202300582 |
| Proyecto GCP | <code>p8202300582</code> |
| Clúster | <code>p9-202300582</code> |
| Zona | <code>us-central1-a</code> |
| Namespace de aplicación | <code>sa-p9</code> |
| Namespace de Velero | <code>velero</code> |
| Bucket de Velero | <code>p9-velero-backups-202300582</code> |
| Aplicación raíz de ArgoCD | <code>sa-platform-p9-root</code> |
| Aplicación de plataforma | <code>sa-platform-p9</code> |

## Terraform y node pools

El estado remoto de Terraform se configura mediante el archivo local
<code>terraform/backend.hcl</code>, que no debe subirse al repositorio.

El archivo <code>terraform/gke.tf</code> declara
<code>remove_default_node_pool = true</code> y el node pool
<code>p9-202300582-nodes</code>. El recurso
<code>terraform_data.remove_default_node_pool</code> elimina de forma
idempotente un <code>default-pool</code> residual después de una interrupción.

    terraform plan -var-file=cloud.tfvars
    terraform apply -var-file=cloud.tfvars
    gcloud container clusters get-credentials p9-202300582 \
      --zone us-central1-a --project p8202300582

El resultado esperado del plan estable es:

    No changes. Your infrastructure matches the configuration.

## Bootstrap automático

El flujo de bootstrap es:

    Terraform -> GKE -> ArgoCD -> External Secrets -> Velero
             -> app-of-apps -> sa-platform-p9

Después de ejecutar Terraform no se aplican manualmente los manifiestos de la
aplicación. ArgoCD es quien sincroniza el repositorio GitOps.

## Velero: servidor del clúster y cliente CLI

Velero tiene dos partes diferentes:

1. Los componentes dentro del clúster: <code>velero-server</code>,
   <code>node-agent</code>, CRDs, BackupStorageLocation, Backup y Restore.
2. El ejecutable local <code>velero</code> instalado en Fedora.

Por eso, el error de <code>velero version</code> en Fedora no demuestra que
Velero falte en Kubernetes. La captura <code>image-10.png</code> demuestra que
el servidor sí estaba instalado: muestra el pod de Velero, dos node-agents y
los jobs de mantenimiento.

Para comprobar Velero dentro del clúster:

    kubectl get pods -n velero
    kubectl get crd | grep velero
    kubectl get backupstoragelocation -n velero

Para comprobar el cliente local:

    velero version --client-only
    velero backup get
    velero restore get

Si Fedora responde <code>command not found: velero</code>, únicamente falta
instalar el CLI y agregarlo al <code>PATH</code>. El bootstrap instala el
servidor mediante Helm:

    helm upgrade --install velero vmware-tanzu/velero \
      --namespace velero --create-namespace \
      --values /tmp/p9-velero-values.yaml --wait

## Backup y restore comprobados

Backup real utilizado:

    p9-real-data-20260923115216

    Phase: Completed
    Errors: 0
    Warnings: 6

Restore posterior a la reconstrucción:

    p9-restore-rebuild-20260924012106

    Phase: Completed
    Errors: 0
    Warnings: 0

El restore se realizó en un namespace temporal para no sobrescribir la
aplicación activa. Los cinco PodVolumeRestore terminaron correctamente y los
PVC restaurados quedaron en estado Bound.

La consulta se realizó en <code>auth_db</code>, tabla <code>usuarios</code>:

    SELECT id_usuario, nombre, apellido, correo, activo
    FROM usuarios;

Registro verificado:

    11111111-1111-1111-1111-111111111111 | Paula | Bibliotecaria
    | paula.p9.202300582@biblioteca.local | t

## Explicación de las capturas y comandos

### image.png - Rollout saludable

Comando: <code>kubectl describe rollout api-gateway -n sa-p9</code>.
Demuestra que el Rollout terminó en fase Healthy y tiene sus réplicas
disponibles.

### image-1.png - Rollout desplegado

Comandos: <code>kubectl get rollout -A</code> y
<code>kubectl describe rollout api-gateway -n sa-p9</code>.
Demuestra que el Rollout existe en <code>sa-p9</code> y tiene sus réplicas
listas. El texto <code>unknown command argo for kubectl</code> corresponde a
un plugin opcional; conviene recortarlo o repetir la captura sin ese error.

### image-2.png - AnalysisTemplate

Comando: <code>kubectl get analysistemplate -n sa-p9</code>.
Demuestra que <code>gateway-integration</code> está creado.

### image-3.png - Configuración del análisis

Comando: <code>kubectl describe analysistemplate gateway-integration -n sa-p9</code>.
Demuestra tres métricas, límite de fallo uno y consultas a los endpoints de
autenticación, catálogo, préstamos y multas.

### image-4.png - ReplicaSets

Comando: <code>kubectl get rs -n sa-p9</code>.
Demuestra las réplicas deseadas, actuales y listas de cada servicio.

### image-5.png - Imágenes desplegadas

Comando: <code>kubectl get rs -n sa-p9 -o wide</code>.
Muestra las imágenes utilizadas y los selectores de cada ReplicaSet.

### image-6.png - Pods de la plataforma

Comando: <code>kubectl get pods -n sa-p9</code>.
Demuestra que los microservicios, PostgreSQL y RabbitMQ están Running y que los
CronJobs terminan en Completed.

### image-7.png - PVC

Comando: <code>kubectl get pvc -n sa-p9</code>.
Demuestra que los PVC de PostgreSQL y RabbitMQ están Bound, con 2 GiB y la
clase <code>standard-rwo</code>.

### image-8.png - PostgreSQL

Comando: <code>kubectl get pods -n sa-p9 | grep auth</code>.
Confirma que <code>auth-postgresql-0</code> está Running. Una captura más limpia
puede usar <code>kubectl get pod auth-postgresql-0 -n sa-p9</code>.

### image-9.png - StatefulSets

Comando: <code>kubectl get statefulset -n sa-p9</code>.
Demuestra que PostgreSQL y RabbitMQ tienen una réplica lista.

### image-10.png - Velero

Comando: <code>kubectl get pods -n velero</code>.
Es la evidencia principal de que Velero está instalado dentro del clúster:
aparecen el servidor, los node-agents y los jobs de mantenimiento.

## Comandos finales para evidencias

    gcloud container node-pools list \
      --cluster p9-202300582 \
      --zone us-central1-a \
      --project p8202300582

    kubectl get nodes -L cloud.google.com/gke-nodepool

    kubectl get applications -n argocd \
      -o custom-columns=NAME:.metadata.name,SYNC:.status.sync.status,HEALTH:.status.health.status

    velero backup-location get
    velero backup get
    velero backup describe p9-real-data-20260923115216 --details
    velero restore get
    velero restore describe p9-restore-rebuild-20260924012106 --details

## Reconstrucción cronometrada

La reconstrucción fue ejecutada con Terraform. La primera ejecución incluyó
una pausa intencional porque el servidor fue apagado durante el procedimiento;
esa pausa debe declararse en el informe y no presentarse como tiempo continuo
de recuperación.

    Inicio de destrucción:    2026-09-23T18:22:30Z
    Finalización del clúster: 2026-09-23T18:44:27Z
    Bootstrap completado:     2026-09-24T00:29:17Z

Después de la reconstrucción, ArgoCD volvió a Synced/Healthy, el
BackupStorageLocation quedó Available y el backup histórico pudo restaurarse.

## Conclusión

Terraform reconstruye la infraestructura, ArgoCD recupera el estado declarativo
y Velero restaura los datos persistentes desde un bucket GCS externo al clúster.
