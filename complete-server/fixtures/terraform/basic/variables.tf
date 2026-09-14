variable "service_name" {
  description = "Name of the simulated service."
  type        = string


  validation {
    condition     = trimspace(var.service_name) != ""
    error_message = "service_name must not be empty."
  }
}


variable "environment" {
  description = "Target environment"
  type        = string


  validation {
    condition = contains(
      ["development", "staging", "production"],
      var.environment
    )

    error_message = "environment must be development, staging, or production."
  }
}


variable "replicas" {
  description = "Simulated number of replicas."
  type        = number
  default     = 1


  validation {
    condition     = var.replicas >= 1
    error_message = "replicas must be greater than or equal to 1."
  }
}
