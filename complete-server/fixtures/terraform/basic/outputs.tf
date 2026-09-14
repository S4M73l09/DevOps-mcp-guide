output "service_configuration" {
  description = "Simulated service configuration."
  value = {
    service_name = terraform_data.service.input.service_name
    environment  = terraform_data.service.input.environment
    replicas     = terraform_data.service.input.replicas
  }
}