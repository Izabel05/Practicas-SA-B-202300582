resource "google_service_account" "external_secrets" {
  account_id   = "p9-external-secrets"
  display_name = "P9 External Secrets workload identity"
  project      = var.gcp_project_id
}

resource "google_project_iam_member" "external_secrets_secret_accessor" {
  project = var.gcp_project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.external_secrets.email}"
}

resource "google_service_account_iam_member" "external_secrets_workload_identity" {
  service_account_id = google_service_account.external_secrets.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.gcp_project_id}.svc.id.goog[external-secrets/p9-external-secrets]"
}
