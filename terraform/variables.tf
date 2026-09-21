variable "project_name" {
  description = "Short, globally unique prefix supplied by the consuming application."
  type        = string
  default     = "devsecops-demo-example"
}

variable "aws_region" {
  description = "AWS region used by the sample provider configuration."
  type        = string
  default     = "us-east-1"
}
