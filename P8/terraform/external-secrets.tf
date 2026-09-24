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

resource "google_service_account_iam_member" "external_secrets_workload_identity" {
  service_account_id = google_service_account.external_secrets.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.gcp_project_id}.svc.id.goog[external-secrets/p8-external-secrets]"
}

resource "kubernetes_service_account_v1" "external_secrets_identity" {
  metadata {
    name      = "p8-external-secrets"
    namespace = "external-secrets"
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.external_secrets.email
    }
  }

  automount_service_account_token = true
  depends_on = [
    google_project_iam_member.external_secrets_secret_accessor,
    google_service_account_iam_member.external_secrets_workload_identity,
  ]
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
                    name             = kubernetes_service_account_v1.external_secrets_identity.metadata[0].name
                    namespace        = kubernetes_service_account_v1.external_secrets_identity.metadata[0].namespace
                  }
                  clusterLocation  = var.gke_location
                  clusterName      = var.gke_cluster_name
                  clusterProjectID = var.gcp_project_id
                }
              }
            }
      }
    }
  }

  depends_on = [kubernetes_service_account_v1.external_secrets_identity]
}
