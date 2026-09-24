resource "google_project_service" "container" {
  count   = var.manage_gke ? 1 : 0
  project = var.gcp_project_id
  service = "container.googleapis.com"

  disable_on_destroy = false
}

resource "google_project_service" "compute" {
  count   = var.manage_gke ? 1 : 0
  project = var.gcp_project_id
  service = "compute.googleapis.com"

  disable_on_destroy = false
}

resource "google_compute_network" "gke" {
  count                   = var.manage_gke ? 1 : 0
  project                 = var.gcp_project_id
  name                    = "${var.gke_cluster_name}-vpc"
  auto_create_subnetworks = false

  depends_on = [google_project_service.compute]
}

resource "google_compute_subnetwork" "gke" {
  count         = var.manage_gke ? 1 : 0
  project       = var.gcp_project_id
  name          = "${var.gke_cluster_name}-subnet"
  region        = var.gcp_region
  network       = google_compute_network.gke[0].id
  ip_cidr_range = "10.20.0.0/16"

  secondary_ip_range {
    range_name    = "gke-pods"
    ip_cidr_range = "10.24.0.0/14"
  }

  secondary_ip_range {
    range_name    = "gke-services"
    ip_cidr_range = "10.28.0.0/20"
  }
}

resource "google_container_cluster" "primary" {
  count    = var.manage_gke ? 1 : 0
  project  = var.gcp_project_id
  name     = var.gke_cluster_name
  location = var.gke_location

  remove_default_node_pool = true
  initial_node_count       = 1
  deletion_protection      = false
  networking_mode          = "VPC_NATIVE"

  network    = google_compute_network.gke[0].name
  subnetwork = google_compute_subnetwork.gke[0].name

  ip_allocation_policy {
    cluster_secondary_range_name  = "gke-pods"
    services_secondary_range_name = "gke-services"
  }

  release_channel {
    channel = "REGULAR"
  }

  workload_identity_config {
    workload_pool = "${var.gcp_project_id}.svc.id.goog"
  }

  depends_on = [google_project_service.container]
}

resource "google_container_node_pool" "primary" {
  count      = var.manage_gke ? 1 : 0
  project    = var.gcp_project_id
  name       = "${var.gke_cluster_name}-nodes"
  location   = var.gke_location
  cluster    = google_container_cluster.primary[0].name
  node_count = var.gke_node_count

  node_config {
    machine_type = var.gke_machine_type
    disk_type    = "pd-balanced"
    disk_size_gb = var.gke_disk_size_gb
    image_type   = "COS_CONTAINERD"

    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    labels = {
      environment = "p8"
      managed-by  = "terraform"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}
