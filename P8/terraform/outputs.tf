output "namespace" {
  value = kubernetes_namespace_v1.platform.metadata[0].name
}

output "quota_name" {
  value = kubernetes_resource_quota_v1.platform.metadata[0].name
}

output "gke_cluster_name" {
  value       = var.manage_gke ? google_container_cluster.primary[0].name : null
  description = "Nombre del clúster GKE creado por Terraform, cuando manage_gke=true."
}

output "gke_location" {
  value       = var.manage_gke ? google_container_cluster.primary[0].location : null
  description = "Zona o región del clúster GKE creado por Terraform."
}
