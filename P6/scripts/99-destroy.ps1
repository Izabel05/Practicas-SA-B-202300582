param(
  [Parameter(Mandatory = $true)][string]$ProjectId,
  [string]$Zone = "us-central1-a",
  [string]$Cluster = "sa-p6-cluster",
  [string]$Region = "us-central1",
  [string]$Repository = "sa-p6",
  [switch]$DeleteArtifactRepository
)
$ErrorActionPreference = "Stop"
gcloud container clusters delete $Cluster --zone $Zone --project $ProjectId --quiet
if ($DeleteArtifactRepository) {
  gcloud artifacts repositories delete $Repository --location $Region --project $ProjectId --quiet
}
