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
