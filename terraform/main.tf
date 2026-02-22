provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "kong" {
  metadata {
    name = "kong"
  }
}

resource "kubernetes_namespace" "user_service" {
  metadata {
    name = "user-service"
  }
}

resource "kubernetes_secret" "jwt_secret" {
  metadata {
    name      = "jwt-secret"
    namespace = kubernetes_namespace.kong.metadata[0].name
  }

  data = {
    "secret" = "super-secret-key"
  }

  type = "Opaque"
}
