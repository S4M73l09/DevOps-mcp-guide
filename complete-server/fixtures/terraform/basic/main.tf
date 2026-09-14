terraform {
  required_version = ">= 1.4.0"
}

resource "terraform_data" "service" {
  input = {
    service_name = var.service_name
    environment  = var.environment
    replicas     = var.replicas
  }
}