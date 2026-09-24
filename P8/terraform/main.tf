resource "terraform_data" "minikube" {
  count = var.manage_minikube ? 1 : 0

  input = {
    profile = var.cluster_profile
    driver  = var.minikube_driver
    cpus    = var.minikube_cpus
    memory  = var.minikube_memory
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command = join(" ", [
      "set -euo pipefail;",
      "minikube delete --profile '${var.cluster_profile}' >/dev/null 2>&1 || true;",
      "minikube start --profile '${var.cluster_profile}' --driver='${var.minikube_driver}' --cpus='${var.minikube_cpus}' --memory='${var.minikube_memory}' --wait=all"
    ])
  }

  provisioner "local-exec" {
    when        = destroy
    interpreter = ["/bin/bash", "-c"]
    command     = "minikube delete --profile '${self.input.profile}'"
  }
}

resource "kubernetes_namespace_v1" "platform" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/part-of"    = "sa-platform"
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  depends_on = [terraform_data.minikube, google_container_node_pool.primary]
}

resource "kubernetes_resource_quota_v1" "platform" {
  metadata {
    name      = "sa-p8-quota"
    namespace = kubernetes_namespace_v1.platform.metadata[0].name
  }

  spec {
    hard = var.resource_quota
  }
}

resource "kubernetes_limit_range_v1" "platform" {
  metadata {
    name      = "sa-p8-limits"
    namespace = kubernetes_namespace_v1.platform.metadata[0].name
  }

  spec {
    limit {
      type = "Container"

      default = {
        cpu    = "500m"
        memory = "512Mi"
      }

      default_request = {
        cpu    = "50m"
        memory = "64Mi"
      }

      min = {
        cpu    = "10m"
        memory = "32Mi"
      }

      max = {
        cpu    = "2"
        memory = "2Gi"
      }
    }
  }
}

resource "kubernetes_service_account_v1" "rollouts" {
  metadata {
    name      = "p8-rollouts"
    namespace = kubernetes_namespace_v1.platform.metadata[0].name
  }
  automount_service_account_token = false
}

locals {
  application_service_accounts = toset([
    "api-gateway",
    "autenticacion-ms",
    "catalogo-ms",
    "prestamos-ms",
    "multas-ms",
    "cronjob1",
    "cronjob2",
    "summary-consumer",
  ])
}

resource "kubernetes_service_account_v1" "application" {
  for_each = local.application_service_accounts

  metadata {
    name      = each.value
    namespace = kubernetes_namespace_v1.platform.metadata[0].name
    labels = {
      "app.kubernetes.io/part-of"    = "sa-platform"
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  automount_service_account_token = false
}

resource "kubernetes_role_v1" "application" {
  for_each = local.application_service_accounts

  metadata {
    name      = "${each.value}-role"
    namespace = kubernetes_namespace_v1.platform.metadata[0].name
    labels = {
      "app.kubernetes.io/part-of"    = "sa-platform"
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "services", "configmaps"]
    verbs      = ["get", "list", "watch"]
  }
}

resource "kubernetes_role_binding_v1" "application" {
  for_each = local.application_service_accounts

  metadata {
    name      = "${each.value}-binding"
    namespace = kubernetes_namespace_v1.platform.metadata[0].name
    labels = {
      "app.kubernetes.io/part-of"    = "sa-platform"
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role_v1.application[each.value].metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account_v1.application[each.value].metadata[0].name
    namespace = kubernetes_namespace_v1.platform.metadata[0].name
  }
}

resource "kubernetes_role_v1" "readonly" {
  metadata {
    name      = "p8-readonly"
    namespace = kubernetes_namespace_v1.platform.metadata[0].name
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "services", "configmaps"]
    verbs      = ["get", "list", "watch"]
  }
}

resource "kubernetes_role_binding_v1" "readonly" {
  metadata {
    name      = "p8-readonly"
    namespace = kubernetes_namespace_v1.platform.metadata[0].name
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role_v1.readonly.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account_v1.rollouts.metadata[0].name
    namespace = kubernetes_namespace_v1.platform.metadata[0].name
  }
}
