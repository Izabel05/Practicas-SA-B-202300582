param([string]$Namespace = "sa-p6")
$ErrorActionPreference = "Stop"

$required = @("AUTH_DATABASE_URL", "CATALOG_DATABASE_URL", "LOANS_DATABASE_URL", "FINES_DATABASE_URL", "CRONJOBS_DATABASE_URL", "JWT_SECRET")
foreach ($name in $required) {
  if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name))) {
    throw "Falta la variable de entorno $name. Cárguela desde sus datos de Neon; no la escriba en Git."
  }
}
if ($env:JWT_SECRET.Length -lt 32) { throw "JWT_SECRET debe tener al menos 32 caracteres." }

kubectl create namespace $Namespace --dry-run=client -o yaml | kubectl apply -f -
$secrets = @(
  @{Name="auth-postgresql-credentials"; Value=$env:AUTH_DATABASE_URL},
  @{Name="catalog-postgresql-credentials"; Value=$env:CATALOG_DATABASE_URL},
  @{Name="loans-postgresql-credentials"; Value=$env:LOANS_DATABASE_URL},
  @{Name="fines-postgresql-credentials"; Value=$env:FINES_DATABASE_URL},
  @{Name="cronjobs-postgresql-credentials"; Value=$env:CRONJOBS_DATABASE_URL}
)
foreach ($secret in $secrets) {
  kubectl -n $Namespace create secret generic $secret.Name --from-literal="database-url=$($secret.Value)" --dry-run=client -o yaml | kubectl apply -f -
}
kubectl -n $Namespace create secret generic jwt-credentials --from-literal="JWT_SECRET=$env:JWT_SECRET" --dry-run=client -o yaml | kubectl apply -f -
