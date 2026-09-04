param([string]$Namespace = "sa-p6")
$ErrorActionPreference = "Stop"
$evidence = Join-Path $PSScriptRoot "..\evidencias\texto"
New-Item -ItemType Directory -Force -Path $evidence | Out-Null

kubectl config current-context | Out-File (Join-Path $evidence "contexto.txt") -Encoding utf8
kubectl get nodes -o wide | Out-File (Join-Path $evidence "nodos.txt") -Encoding utf8
kubectl -n $Namespace get pods -o wide | Out-File (Join-Path $evidence "pods.txt") -Encoding utf8
kubectl -n $Namespace get services | Out-File (Join-Path $evidence "servicios.txt") -Encoding utf8
kubectl -n $Namespace get pvc | Out-File (Join-Path $evidence "almacenamiento.txt") -Encoding utf8

$publicIp = kubectl -n $Namespace get service api-gateway -o jsonpath="{.status.loadBalancer.ingress[0].ip}"
if (-not $publicIp) { throw "El LoadBalancer aún no tiene IP pública. Espere unos minutos y vuelva a ejecutar." }
Invoke-WebRequest -Uri "http://$publicIp/health" -UseBasicParsing | Select-Object StatusCode, Content | Out-File (Join-Path $evidence "peticion-publica.txt") -Encoding utf8
Write-Output "IP pública: $publicIp"
