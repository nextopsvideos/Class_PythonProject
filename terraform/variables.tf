variable "name" {
  type        = string
  description = "Base name for all resources"
}

variable "location" {
  type        = string
  description = "Azure location for all resources"
}

variable "database_password" {
  type        = string
  description = "Administrator password for the PostgreSQL server"
  sensitive   = true
}

variable "secret_key" {
  type        = string
  description = "Application secret key"
  sensitive   = true
}
