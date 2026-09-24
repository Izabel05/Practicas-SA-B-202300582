terraform {
  required_version = ">= 1.6.0"

  # La configuración concreta del bucket se entrega mediante
  # -backend-config para no guardar nombres de infraestructura ni credenciales
  # en el repositorio.
  backend "gcs" {}

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}
