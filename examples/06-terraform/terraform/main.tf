terraform {
  required_version = ">= 1.6.0"
}

variable "service_name" {
  type        = string
  description = "Name of the service."
  default     = "api"
}

output "service_name" {
  value = var.service_name
}