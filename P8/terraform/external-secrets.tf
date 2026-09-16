resource "google_service_account" "external_secrets" {
  account_id   = "p8-external-secrets"
  display_name = "P8 External Secrets workload identity"
  project      = var.gcp_project_id
}

resource "google_project_iam_member" "external_secrets_secret_accessor" {
  project = var.gcp_project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.external_secrets.email}"
}

resource "kubernetes_service_account_v1" "external_secrets" {
  metadata {
    name      = "external-secrets"
    namespace = "external-secrets"
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.external_secrets.email
    }
  }

  automount_service_account_token = true
  depends_on                      = [google_project_iam_member.external_secrets_secret_accessor]
}

resource "kubernetes_manifest" "cluster_secret_store" {
  manifest = {
    apiVersion = "external-secrets.io/v1"
    kind       = "ClusterSecretStore"
    metadata = {
      name = "cluster-secret-store"
    }
    spec = {
      provider = {
        gcpsm = {
          projectID = var.gcp_project_id
          auth = {
            workloadIdentity = {
              serviceAccountRef = {
                name      = kubernetes_service_account_v1.external_secrets.metadata[0].name
                namespace = kubernetes_service_account_v1.external_secrets.metadata[0].namespace
              }
            }
          }
        }
      }
    }
  }

  depends_on = [kubernetes_service_account_v1.external_secrets]
}
