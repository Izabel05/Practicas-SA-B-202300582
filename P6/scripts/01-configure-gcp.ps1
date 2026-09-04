param(
  [Parameter(Mandatory = $true)][string]$ProjectId,
  [string]$Region = "us-central1",
  [string]$Zone = "us-central1-a",
  [string]$Cluster = "sa-p6-cluster",
  [string]$Repository = "sa-p6"
)
$ErrorActionPreference = "Stop"

gcloud config set project $ProjectId
gcloud services enable container.googleapis.com artifactregistry.googleapis.com

$existingRepository = gcloud artifacts repositories describe $Repository --location $Region --format "value(name)" 2>$null
if (-not $existingRepository) {
  gcloud artifacts repositories create $Repository --repository-format docker --location $Region --description "Imágenes de la Práctica 6"
}

$existingCluster = gcloud container clusters describe $Cluster --zone $Zone --format "value(name)" 2>$null
if (-not $existingCluster) {
  gcloud container clusters create $Cluster --zone $Zone --num-nodes 1 --machine-type e2-standard-2 --disk-type pd-balanced --disk-size 30 --release-channel regular --enable-ip-alias
}

gcloud container clusters get-credentials $Cluster --zone $Zone --project $ProjectId
gcloud auth configure-docker "$Region-docker.pkg.dev"
kubectl get nodes
