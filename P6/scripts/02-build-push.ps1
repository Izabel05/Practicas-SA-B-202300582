param(
  [Parameter(Mandatory = $true)][string]$ProjectId,
  [string]$Region = "us-central1",
  [string]$Repository = "sa-p6"
)
$ErrorActionPreference = "Stop"
$backend = Resolve-Path (Join-Path $PSScriptRoot "..\..\P4\Backend")
$worker = Resolve-Path (Join-Path $PSScriptRoot "..\cronjobs\cronjob2")
$registry = "$Region-docker.pkg.dev/$ProjectId/$Repository"

$images = @(
  @{Name="api-gateway"; Tag="0.1.1"; Context=(Join-Path $backend "api-gateway"); File=(Join-Path $backend "api-gateway\Dockerfile.prod")},
  @{Name="autenticacion-ms"; Tag="0.1.0"; Context=(Join-Path $backend "autenticacion-ms"); File=(Join-Path $backend "autenticacion-ms\Dockerfile.prod")},
  @{Name="catalogo-ms"; Tag="0.1.0"; Context=(Join-Path $backend "catalogo-ms"); File=(Join-Path $backend "catalogo-ms\Dockerfile.prod")},
  @{Name="prestamos-ms"; Tag="0.2.2"; Context=(Join-Path $backend "prestamos-ms"); File=(Join-Path $backend "prestamos-ms\Dockerfile.prod")},
  @{Name="multas-ms"; Tag="0.1.3"; Context=(Join-Path $backend "multas-ms"); File=(Join-Path $backend "multas-ms\Dockerfile.prod")},
  @{Name="cronjobs-worker"; Tag="0.1.0"; Context=$worker; File=(Join-Path $worker "Dockerfile.prod")}
)

foreach ($image in $images) {
  $target = "$registry/$($image.Name):$($image.Tag)"
  docker build --file $image.File --tag $target $image.Context
  docker push $target
}
