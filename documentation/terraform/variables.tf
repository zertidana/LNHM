variable AWS_ACCESS_KEY_ID {
    type = string
}

variable AWS_SECRET_ACCESS_KEY {
    type = string
}

variable EXECUTION_ROLE_ARN {
    type = string
}

variable AWS_REGION {
    type = string
}

variable VPC_ID {
    type = string
}

variable "LOG_GROUP" {
    type = string
}

variable CONTAINER_ENV_VARS {
    description = "Environment variables for the container"
  type        = list(object({
    name  = string
    value = string
  }))
}