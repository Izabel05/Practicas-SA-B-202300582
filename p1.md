# Guion del video - Práctica 9

Duración objetivo: entre 5 y 8 minutos.

Este archivo es una guía para saber qué mostrar y qué explicar. No sustituye
el video ni debe contener contraseñas, tokens o valores de secretos.

## 00:00 - 00:40 | Presentación

Decir:

    Esta es la Práctica 9 de continuidad operativa y recuperación ante
    desastres. El sistema utiliza Terraform para reconstruir GKE, ArgoCD para
    recuperar la aplicación y Velero para respaldar y restaurar los datos
    persistentes.

Mostrar:

- Proyecto GCP <code>p8202300582</code>.
- Clúster <code>p9-202300582</code>.
- Namespace <code>sa-p9</code>.

## 00:40 - 01:25 | Arquitectura y bootstrap

Decir:

    El punto de entrada es Terraform. Terraform crea la infraestructura,
    instala ArgoCD, External Secrets y Velero. Después ArgoCD aplica el
    app-of-apps y levanta la plataforma declarativa.

Mostrar:

- Archivo <code>P9/terraform/bootstrap-gke.sh.tftpl</code>.
- Diagrama de reconstrucción en <code>P9/README.md</code>.
- Comando:

      kubectl get applications -n argocd

Explicar que las aplicaciones deben aparecer como <code>Synced</code> y
<code>Healthy</code>.

## 01:25 - 02:05 | Terraform y estado remoto

Decir:

    Terraform utiliza un backend remoto GCS con prefijo terraform/p9. El
    estado no se conserva en la máquina ni se sube al repositorio.

Mostrar:

    terraform init -backend-config=backend.hcl
    terraform plan -var-file=cloud.tfvars

Mencionar que el resultado esperado es <code>No changes</code> después de una
ejecución estable.

## 02:05 - 02:50 | Aplicación y persistencia

Decir:

    La aplicación conserva PostgreSQL y RabbitMQ mediante PVC. Los
    microservicios stateless tienen réplicas, probes, políticas de interrupción
    y anti-afinidad.

Mostrar:

    kubectl get pods -n sa-p9
    kubectl get pvc -n sa-p9
    kubectl get statefulset -n sa-p9

## 02:50 - 03:35 | Velero y respaldo programado

Decir:

    Velero está instalado dentro del clúster y utiliza el bucket GCS
    p9-velero-backups-202300582. El schedule p9-daily se ejecuta a las 02:00,
    conserva los backups durante 720 horas e incluye los volúmenes mediante
    File System Backup.

Mostrar:

    velero version
    velero backup-location get
    velero schedule get
    velero backup get

Explicar que cliente y servidor muestran la versión <code>v1.18.2</code>.

## 03:35 - 04:20 | Reconstrucción y pérdida de nodo

Decir:

    La reconstrucción fue ejecutada con Terraform. También se probó el drenaje
    controlado de un nodo para verificar que los pods stateless se reubican y
    el servicio conserva disponibilidad.

Mostrar:

    kubectl get nodes
    kubectl get pods -n sa-p9 -o wide
    kubectl cordon NOMBRE_REAL_DEL_NODO
    kubectl drain NOMBRE_REAL_DEL_NODO --ignore-daemonsets --delete-emptydir-data

Mostrar después:

    kubectl get pods -n sa-p9 -o wide
    kubectl get rollout -n sa-p9
    kubectl uncordon NOMBRE_REAL_DEL_NODO

No es necesario provocar un error artificial de la aplicación; el drenaje del
nodo es la falla controlada exigida por la práctica.

## 04:20 - 05:25 | Restauración y datos reales

Decir:

    El backup p9-real-data-20260923115216 se restauró en un namespace temporal
    para no sobrescribir la aplicación activa. El restore terminó Completed y
    se verificó el contenido real de PostgreSQL.

Mostrar:

    velero restore get
    velero restore describe p9-restore-rebuild-20260924012106 --details

Luego mostrar la consulta:

    kubectl exec -n NAMESPACE_RESTAURADO auth-postgresql-0 -- sh -c \
      'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
      -c "SELECT id_usuario, nombre, apellido, correo, activo FROM usuarios;"'

Señalar el registro recuperado de Paula y explicar que esto prueba que el
volumen no estaba vacío.

## 05:25 - 06:05 | Continuidad de secretos

Decir:

    Los secretos no dependen de una llave almacenada únicamente dentro del
    clúster. External Secrets los obtiene desde Secret Manager y los vuelve a
    sincronizar después de la reconstrucción.

Mostrar:

    kubectl get clustersecretstore
    kubectl get externalsecret -n sa-p9
    kubectl get secret -n sa-p9

No mostrar valores codificados, contraseñas ni tokens.

## 06:05 - 07:00 | RTO, RPO y cierre

Decir:

    El RTO objetivo declarado fue de 60 minutos y el RPO objetivo de 24 horas.
    La medición total de pared fue de 6 horas, 6 minutos y 47 segundos porque
    el servidor fue apagado durante la primera ejecución. Por honestidad
    técnica, esa medición no se presenta como un RTO continuo. El backup más
    reciente tenía aproximadamente 30 minutos de antigüedad al comenzar la
    destrucción y el registro real fue recuperado correctamente.

Cerrar diciendo:

    La infraestructura se reconstruye con Terraform, la aplicación se
    recupera mediante ArgoCD, los secretos se sincronizan desde el proveedor
    externo y los datos persistentes se restauran mediante Velero.

## Checklist antes de grabar

- El clúster está encendido y accesible desde Cloud Shell.
- <code>velero version</code> muestra cliente y servidor.
- ArgoCD aparece <code>Synced/Healthy</code>.
- Existe un backup <code>Completed</code>.
- La restauración y la consulta SQL están preparadas.
- Las capturas están en <code>P9/</code>.
- No aparecen credenciales ni valores de secretos.
- El video dura entre 5 y 8 minutos.
