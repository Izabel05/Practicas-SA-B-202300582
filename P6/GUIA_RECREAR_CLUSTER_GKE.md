# Guía para eliminar y recrear el clúster de GKE

Esta guía permite eliminar y volver a crear el clúster `sa-p6-cluster` desde Google Cloud Shell. Conserva las imágenes de Artifact Registry y las bases de Neon, pero reconstruye todos los recursos que viven dentro de Kubernetes.

## Datos utilizados

| Recurso | Valor |
|---|---|
| Proyecto de GCP | `p6202300582` |
| Clúster | `sa-p6-cluster` |
| Zona | `us-central1-a` |
| Región de Artifact Registry | `us-central1` |
| Repositorio de imágenes | `sa-p6` |
| Namespace | `sa-p6` |
| Release de Helm | `sa-platform` |

## Qué se conserva y qué se elimina

Al eliminar el clúster se pierden:

- Deployments, Pods, Services, CronJobs y Jobs.
- Secrets de Kubernetes.
- Namespace `sa-p6`.
- Release de Helm almacenado dentro del clúster.
- RabbitMQ y sus mensajes pendientes.

No se eliminan automáticamente:

- Imágenes de Artifact Registry.
- Repositorio `sa-p6` de Artifact Registry.
- Bases, tablas y registros almacenados en Neon.
- Cuentas de servicio y permisos IAM del proyecto.
- Código fuente guardado en Cloud Shell o GitHub.

## 1. Definir las variables de trabajo

Ejecute lo siguiente en Google Cloud Shell:

```bash
PROJECT_ID="p6202300582"
CLUSTER_NAME="sa-p6-cluster"
ZONE="us-central1-a"
REGION="us-central1"
NAMESPACE="sa-p6"
RELEASE="sa-platform"
REPOSITORY="sa-p6"

gcloud config set project "$PROJECT_ID"
gcloud config set compute/zone "$ZONE"
```

Verifique el proyecto activo:

```bash
gcloud config get-value project
```

## 2. Guardar evidencia antes de eliminar

Si el clúster todavía existe, guarde las salidas necesarias para la entrega:

```bash
kubectl get nodes -o wide
kubectl -n "$NAMESPACE" get pods
kubectl -n "$NAMESPACE" get cronjobs
kubectl -n "$NAMESPACE" get jobs
kubectl -n "$NAMESPACE" get services
kubectl -n "$NAMESPACE" get pvc
```

Guarde también capturas de GKE, Artifact Registry, la IP pública, las peticiones exitosas y el costo aproximado mostrado en Billing.

## 3. Eliminar limpiamente el despliegue y el clúster

Desinstalar Helm primero permite que Kubernetes solicite la eliminación del balanceador y del volumen persistente antes de destruir el clúster:

```bash
helm uninstall "$RELEASE" \
  --namespace "$NAMESPACE" \
  --ignore-not-found

kubectl delete namespace "$NAMESPACE" \
  --ignore-not-found \
  --wait=true
```

Elimine el clúster:

```bash
gcloud container clusters delete "$CLUSTER_NAME" \
  --zone="$ZONE" \
  --project="$PROJECT_ID" \
  --quiet
```

Confirme que ya no aparece:

```bash
gcloud container clusters list \
  --project="$PROJECT_ID"
```

Revise que no hayan quedado discos o reglas de reenvío asociados. Estos comandos solamente consultan; no eliminan recursos:

```bash
gcloud compute disks list \
  --project="$PROJECT_ID"

gcloud compute forwarding-rules list \
  --project="$PROJECT_ID"
```

No elimine el repositorio de Artifact Registry si reutilizará las imágenes.

## 4. Habilitar las API necesarias

```bash
gcloud services enable \
  container.googleapis.com \
  compute.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  --project="$PROJECT_ID"
```

## 5. Preparar el permiso para descargar imágenes privadas

El error `403 Forbidden` al descargar imágenes ocurrió porque la cuenta usada por los nodos no tenía permiso de lectura en Artifact Registry. Obtenga la cuenta predeterminada de Compute Engine y aplique el rol de lectura:

```bash
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
NODE_SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "Cuenta de los nodos: $NODE_SERVICE_ACCOUNT"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$NODE_SERVICE_ACCOUNT" \
  --role="roles/artifactregistry.reader" \
  --condition=None
```

El permiso es persistente; repetir el comando no crea otra cuenta de servicio.

## 6. Crear nuevamente el clúster

El siguiente comando crea un clúster Standard, zonal y de un nodo, según la autorización del auxiliar para reducir costos:

```bash
gcloud container clusters create "$CLUSTER_NAME" \
  --project="$PROJECT_ID" \
  --zone="$ZONE" \
  --release-channel=regular \
  --num-nodes=1 \
  --machine-type=e2-standard-2 \
  --disk-type=pd-balanced \
  --disk-size=30 \
  --image-type=COS_CONTAINERD \
  --service-account="$NODE_SERVICE_ACCOUNT" \
  --scopes=cloud-platform \
  --enable-ip-alias \
  --enable-network-policy \
  --metadata=disable-legacy-endpoints=true
```

Espere a que el comando finalice. Después conecte `kubectl`:

```bash
gcloud container clusters get-credentials "$CLUSTER_NAME" \
  --zone="$ZONE" \
  --project="$PROJECT_ID"

kubectl get nodes -o wide
```

Debe aparecer exactamente un nodo en estado `Ready`.

## 7. Confirmar las imágenes existentes

No es necesario volver a construir las imágenes si todavía aparecen en Artifact Registry:

```bash
gcloud artifacts docker images list \
  "$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY" \
  --include-tags
```

Se esperan estas seis imágenes:

- `api-gateway`
- `autenticacion-ms`
- `catalogo-ms`
- `prestamos-ms`
- `multas-ms`
- `cronjobs-worker`

## 8. Preparar el chart y el namespace

Entre al chart almacenado en Cloud Shell:

```bash
cd ~/sa-p6-source/P6/charts/sa-platform
```

El namespace debe tener un único propietario. Como los Secrets tienen que existir antes del despliegue, se crea manualmente y se deshabilita el manifiesto de namespace incluido en el chart:

```bash
if [ -f templates/namespace.yaml ]; then
  mv templates/namespace.yaml namespace.yaml.disabled
fi

kubectl create namespace "$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -
```

Esto evita el error de Helm `invalid ownership metadata`.

## 9. Crear correctamente los Secrets

La siguiente función valida que cada valor comience con `postgresql://`. Cuando aparezca cada solicitud, pegue solamente la URL de Neon, sin escribir `$env:`, el nombre de la variable ni comillas.

```bash
create_database_secret() {
  SECRET_NAME="$1"
  PROMPT_TEXT="$2"
  DATABASE_VALUE=""

  while [[ "$DATABASE_VALUE" != postgresql://* ]]; do
    read -r -s -p "$PROMPT_TEXT: " DATABASE_VALUE
    echo

    if [[ "$DATABASE_VALUE" != postgresql://* ]]; then
      echo "Valor inválido. Debe comenzar con postgresql://"
    fi
  done

  kubectl -n "$NAMESPACE" create secret generic "$SECRET_NAME" \
    --from-literal=database-url="$DATABASE_VALUE" \
    --dry-run=client -o yaml | kubectl apply -f -

  unset DATABASE_VALUE
}

create_database_secret auth-postgresql-credentials "URL de auth_db"
create_database_secret catalog-postgresql-credentials "URL de catalogo_db"
create_database_secret loans-postgresql-credentials "URL de prestamos_db"
create_database_secret fines-postgresql-credentials "URL de multas_db"
create_database_secret cronjobs-postgresql-credentials "URL de cronjob_db"
```

Genere el JWT Secret automáticamente:

```bash
JWT_SECRET="$(openssl rand -hex 32)"

kubectl -n "$NAMESPACE" create secret generic jwt-credentials \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  --dry-run=client -o yaml | kubectl apply -f -

unset JWT_SECRET
```

Verifique el resultado:

```bash
kubectl -n "$NAMESPACE" get secrets
```

Los seis Secrets de la aplicación deben mostrar `DATA 1`. Si alguno muestra `DATA 0`, no continúe con Helm; vuelva a crear únicamente ese Secret.

## 10. Verificar la configuración DNS conocida

Obtenga la IP del servicio DNS del nuevo clúster:

```bash
DNS_IP="$(kubectl -n kube-system get service kube-dns -o jsonpath='{.spec.clusterIP}')"
echo "DNS de GKE: $DNS_IP"
```

La versión corregida del archivo `templates/network-policies/allow-dns.yaml` debe permitir salida UDP y TCP al servicio DNS, incluyendo un `ipBlock` con esa IP en formato `/32`. Verifique la corrección incluida en el ZIP:

```bash
grep -n -A8 -B4 "${DNS_IP}/32" \
  templates/network-policies/allow-dns.yaml
```

Si el comando no muestra el `ipBlock`, detenga el procedimiento y corrija el archivo antes de ejecutar Helm. No aplique un parche manual al recurso después del despliegue, porque eso vuelve a producir conflictos de propiedad entre `kubectl-patch` y Helm.

## 11. Desplegar con Helm

```bash
REGISTRY="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY"

helm dependency build

helm upgrade --install "$RELEASE" . \
  --namespace "$NAMESPACE" \
  --create-namespace \
  -f values-gke.yaml \
  --set-string "api-gateway.image.repository=$REGISTRY/api-gateway" \
  --set-string "autenticacion-ms.image.repository=$REGISTRY/autenticacion-ms" \
  --set-string "catalogo-ms.image.repository=$REGISTRY/catalogo-ms" \
  --set-string "prestamos-ms.image.repository=$REGISTRY/prestamos-ms" \
  --set-string "multas-ms.image.repository=$REGISTRY/multas-ms" \
  --set-string "cronjob2.image.repository=$REGISTRY/cronjobs-worker" \
  --set-string "summaryConsumer.image.repository=$REGISTRY/cronjobs-worker" \
  --set-string "api-gateway.upstreams.resolver=$DNS_IP" \
  --wait \
  --timeout 10m
```

Los mensajes que indican que una dependencia no declaró repositorio son informativos para estos subcharts locales.

## 12. Verificación final

```bash
helm status "$RELEASE" --namespace "$NAMESPACE"

kubectl -n "$NAMESPACE" get pods
kubectl -n "$NAMESPACE" get services
kubectl -n "$NAMESPACE" get cronjobs
kubectl -n "$NAMESPACE" get pvc
```

Todos los Deployments deben mostrar sus réplicas disponibles, RabbitMQ debe estar `Running`, el PVC debe estar `Bound` y los Jobs periódicos deben terminar como `Completed`.

Obtenga la IP pública:

```bash
kubectl -n "$NAMESPACE" get service api-gateway
```

## 13. Consultar los resultados de los CronJobs

Consulta de `cronjob1`:

```bash
QUERY1="query-cronjob1-$(date +%s)"

kubectl -n "$NAMESPACE" create job "$QUERY1" \
  --from=cronjob/cronjob1 \
  --dry-run=client -o json \
  | jq '.spec.template.spec.containers[0].command=["psql"]
        | .spec.template.spec.containers[0].args=["$(DATABASE_URL)","-c","SELECT id, fecha_ejecucion, carne FROM ejecuciones_cronjob ORDER BY id DESC LIMIT 10;"]' \
  | kubectl apply -f -

kubectl -n "$NAMESPACE" wait --for=condition=complete "job/$QUERY1" --timeout=180s
kubectl -n "$NAMESPACE" logs "job/$QUERY1"
kubectl -n "$NAMESPACE" delete job "$QUERY1"
```

Consulta de los resúmenes de `cronjob2`:

```bash
QUERY2="query-cronjob2-$(date +%s)"

kubectl -n "$NAMESPACE" create job "$QUERY2" \
  --from=cronjob/cronjob1 \
  --dry-run=client -o json \
  | jq '.spec.template.spec.containers[0].command=["psql"]
        | .spec.template.spec.containers[0].args=["$(DATABASE_URL)","-c","SELECT id, evento_id, generado_en, resumen, recibido_en FROM resumenes_ejecuciones ORDER BY id DESC LIMIT 10;"]' \
  | kubectl apply -f -

kubectl -n "$NAMESPACE" wait --for=condition=complete "job/$QUERY2" --timeout=180s
kubectl -n "$NAMESPACE" logs "job/$QUERY2"
kubectl -n "$NAMESPACE" delete job "$QUERY2"
```

## 14. Diagnóstico de errores conocidos

### `ImagePullBackOff` o `403 Forbidden`

Confirme la cuenta de los nodos y vuelva a aplicar el rol de lectura:

```bash
gcloud container clusters describe "$CLUSTER_NAME" \
  --zone="$ZONE" \
  --format='value(nodePools[0].config.serviceAccount)'

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$NODE_SERVICE_ACCOUNT" \
  --role="roles/artifactregistry.reader" \
  --condition=None
```

Después reinicie los Deployments afectados:

```bash
kubectl -n "$NAMESPACE" rollout restart deployment
```

### Helm informa `context deadline exceeded`

No elimine inmediatamente el release. El mensaje significa que algún recurso no quedó listo dentro del tiempo establecido. Consulte:

```bash
kubectl -n "$NAMESPACE" get pods -o wide
kubectl -n "$NAMESPACE" get events --sort-by='.lastTimestamp' | tail -40
```

Para un servicio específico:

```bash
kubectl -n "$NAMESPACE" logs deployment/catalogo-ms --all-containers=true --tail=100
kubectl -n "$NAMESPACE" logs deployment/prestamos-ms --all-containers=true --tail=100
```

### `DATABASE_URL es obligatoria`

El Secret está vacío. Confirme que tenga una entrada:

```bash
kubectl -n "$NAMESPACE" get secrets
```

Debe mostrar `DATA 1`. Vuelva a ejecutar la función `create_database_secret` para el Secret afectado y reinicie su Deployment.

### `missing "=" after "...DATABASE_URL:"`

Se pegó el nombre de una variable en lugar de la URL. Vuelva a crear el Secret pegando solamente el valor que comienza con `postgresql://`.

### `host not found in resolver` o DNS sin respuesta

Confirme el servicio DNS y la política de red:

```bash
kubectl -n kube-system get service kube-dns -o wide
kubectl -n kube-system get endpoints kube-dns -o wide
kubectl -n "$NAMESPACE" get networkpolicy allow-dns-egress -o yaml
kubectl -n "$NAMESPACE" exec rabbitmq-0 -- nslookup kubernetes.default.svc.cluster.local
```

La IP usada por Nginx y el `ipBlock` de la NetworkPolicy deben coincidir con `DNS_IP`.

### Conflicto de propiedad de `allow-dns-egress`

No combine un parche manual permanente con el recurso administrado por Helm. La corrección debe quedar en `templates/network-policies/allow-dns.yaml`; después se ejecuta nuevamente el comando completo de `helm upgrade --install`.

## 15. Recomendaciones de costo

- Mantenga el clúster activo solamente durante desarrollo, pruebas y calificación.
- Conserve un solo nodo mientras siga vigente la autorización del auxiliar.
- Elimine primero el release de Helm y después el clúster.
- Revise discos, balanceadores e IP públicas después de eliminarlo.
- Artifact Registry y Neon permanecen separados del ciclo de vida del clúster.

