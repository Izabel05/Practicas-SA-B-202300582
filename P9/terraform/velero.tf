resource "google_storage_bucket" "velero" {
  name                        = var.velero_bucket_name
  project                     = var.gcp_project_id
  location                    = var.velero_bucket_location
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy               = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = var.velero_retention_days
    }
  }

  labels = {
    environment = "p9"
    purpose     = "velero-backups"
    managed-by  = "terraform"
  }
}

resource "google_service_account" "velero" {
  account_id   = var.velero_service_account_id
  display_name = "P9 Velero backup workload identity"
  project      = var.gcp_project_id
}

resource "google_storage_bucket_iam_member" "velero_object_admin" {
  bucket = google_storage_bucket.velero.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.velero.email}"
}

resource "google_service_account_iam_member" "velero_workload_identity" {
  service_account_id = google_service_account.velero.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.gcp_project_id}.svc.id.goog[velero/velero-server]"
}
