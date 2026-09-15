output "namespace" {
  value = kubernetes_namespace_v1.platform.metadata[0].name
}

output "quota_name" {
  value = kubernetes_resource_quota_v1.platform.metadata[0].name
}
