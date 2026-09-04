param(
  [Parameter(Mandatory = $true)][string]$ProjectId,
  [string]$Region = "us-central1",
  [string]$Namespace = "sa-p6",
  [string]$Repository = "sa-p6"
)
$ErrorActionPreference = "Stop"
$chart = Resolve-Path (Join-Path $PSScriptRoot "..\charts\sa-platform")
$values = Join-Path $chart "values-gke.yaml"
$registry = "$Region-docker.pkg.dev/$ProjectId/$Repository"

helm dependency build $chart
helm upgrade --install sa-platform $chart --namespace $Namespace --create-namespace -f $values `
  --set-string "api-gateway.image.repository=$registry/api-gateway" `
  --set-string "autenticacion-ms.image.repository=$registry/autenticacion-ms" `
  --set-string "catalogo-ms.image.repository=$registry/catalogo-ms" `
  --set-string "prestamos-ms.image.repository=$registry/prestamos-ms" `
  --set-string "multas-ms.image.repository=$registry/multas-ms" `
  --set-string "cronjob2.image.repository=$registry/cronjobs-worker" `
  --set-string "summaryConsumer.image.repository=$registry/cronjobs-worker" `
  --wait --timeout 10m

kubectl -n $Namespace get pods
kubectl -n $Namespace get service api-gateway
