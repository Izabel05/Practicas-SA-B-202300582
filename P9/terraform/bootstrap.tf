resource "terraform_data" "p9_bootstrap" {
  count = var.manage_gke ? 1 : 0

  input = {
    cluster = var.gke_cluster_name
    bucket  = google_storage_bucket.velero.name
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command = templatefile("${path.module}/bootstrap-gke.sh.tftpl", {
      cluster_name                           = var.gke_cluster_name
      cluster_location                       = var.gke_location
      project_id                             = var.gcp_project_id
      velero_bucket_name                     = google_storage_bucket.velero.name
      velero_service_account_email           = google_service_account.velero.email
      external_secrets_service_account_email = google_service_account.external_secrets.email
      gitops_app_of_apps_url                 = var.gitops_app_of_apps_url
    })
  }

  depends_on = [
    google_container_node_pool.primary,
    google_storage_bucket_iam_member.velero_object_admin,
    google_service_account_iam_member.velero_workload_identity,
    google_project_iam_member.external_secrets_secret_accessor,
    google_service_account_iam_member.external_secrets_workload_identity,
  ]
}
