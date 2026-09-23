variable "namespace" {
  description = "Namespace aislado para la plataforma de P9."
  type        = string
  default     = "sa-p9"
}

variable "gitops_app_of_apps_url" {
  description = "Manifiesto público de entrada del app-of-apps de P9."
  type        = string
  default     = "https://raw.githubusercontent.com/Izabel05/GItOps_202300582/main/argocd/app-of-apps.yaml"
}

variable "manage_gke" {
  type    = bool
  default = false
}

variable "gcp_project_id" {
  description = "ID del proyecto Google Cloud donde se creará GKE."
  type        = string
  default     = null
  nullable    = true
}

variable "velero_bucket_name" {
  description = "Bucket GCS externo al clúster para los respaldos de Velero."
  type        = string
  default     = "p9-velero-backups-202300582"
}

variable "velero_bucket_location" {
  description = "Ubicación del bucket GCS de Velero."
  type        = string
  default     = "US-CENTRAL1"
}

variable "velero_retention_days" {
  description = "Retención adicional de objetos de respaldo en GCS."
  type        = number
  default     = 30
}

variable "velero_service_account_id" {
  description = "ID de la cuenta de servicio usada por Velero mediante Workload Identity."
  type        = string
  default     = "p9-velero"
}

variable "gcp_region" {
  description = "Región de la red y de los recursos regionales de GKE."
  type        = string
  default     = "us-central1"
}

variable "gke_location" {
  description = "Zona del clúster zonal GKE y de su node pool."
  type        = string
  default     = "us-central1-a"
}

variable "gke_cluster_name" {
  description = "Nombre del clúster GKE de P9."
  type        = string
  default     = "p9-202300582"
}

variable "gke_network_name" {
  description = "Nombre de la VPC usada por el clúster."
  type        = string
  default     = "p8-202300582-vpc"
}

variable "gke_subnetwork_name" {
  description = "Nombre de la subred usada por el clúster."
  type        = string
  default     = "p8-202300582-subnet"
}

variable "gke_machine_type" {
  description = "Tipo de máquina para el node pool de prueba."
  type        = string
  default     = "e2-standard-2"
}

variable "gke_node_count" {
  description = "Cantidad de nodos por defecto para el node pool."
  type        = number
  default     = 2
}

variable "gke_disk_size_gb" {
  description = "Tamaño de disco de cada nodo GKE."
  type        = number
  default     = 30
}
