output "namespace" {
  value = var.namespace
}

output "quota_name" {
  value = "${var.namespace}-quota"
}

output "gke_cluster_name" {
  value       = var.manage_gke ? google_container_cluster.primary[0].name : null
  description = "Nombre del clúster GKE creado por Terraform, cuando manage_gke=true."
}

output "gke_location" {
  value       = var.manage_gke ? google_container_cluster.primary[0].location : null
  description = "Zona o región del clúster GKE creado por Terraform."
}

output "velero_bucket_name" {
  value       = google_storage_bucket.velero.name
  description = "Bucket GCS externo usado por Velero para respaldos de P9."
}

output "velero_schedule" {
  value       = "p9-daily"
  description = "Schedule diario de Velero instalado por el bootstrap de P9."
}
