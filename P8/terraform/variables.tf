variable "namespace" {
  description = "Namespace aislado para la plataforma de P8."
  type        = string
  default     = "sa-p8"
}

variable "manage_minikube" {
  description = "Reconstruye el perfil Minikube de prueba desde Terraform."
  type        = bool
  default     = true
}

variable "manage_gke" {
  description = "Crea y administra el clúster GKE de nube. No se combina con manage_minikube."
  type        = bool
  default     = false
}

variable "gcp_project_id" {
  description = "ID del proyecto Google Cloud donde se creará GKE."
  type        = string
  default     = null
  nullable    = true
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
  description = "Nombre del clúster GKE."
  type        = string
  default     = "p8-202300582"
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

variable "cluster_profile" {
  description = "Perfil Minikube objetivo; se verifica antes de ejecutar la prueba destructiva."
  type        = string
  default     = "minikube"
}

variable "minikube_driver" {
  description = "Driver del perfil Minikube de prueba."
  type        = string
  default     = "docker"
}

variable "minikube_cpus" {
  description = "CPU asignada al clúster Minikube de prueba."
  type        = number
  default     = 4
}

variable "minikube_memory" {
  description = "Memoria asignada al clúster Minikube de prueba."
  type        = string
  default     = "6144mb"
}

variable "kubeconfig_path" {
  description = "Ruta local al kubeconfig; nunca se guarda en GitHub Actions."
  type        = string
  default     = null
  nullable    = true
  sensitive   = true
}

variable "kube_context" {
  description = "Contexto Kubernetes utilizado por Terraform en la prueba local."
  type        = string
  default     = "minikube"
}

variable "resource_quota" {
  description = "Limites agregados del namespace."
  type        = map(string)
  default = {
    "requests.cpu"    = "4"
    "requests.memory" = "6Gi"
    "limits.cpu"      = "12"
    "limits.memory"   = "12Gi"
    pods              = "40"
    services          = "20"
    secrets           = "30"
  }
}
