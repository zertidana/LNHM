variable AWS_ACCESS_KEY_ID {
    type = string
}

variable AWS_SECRET_ACCESS_KEY {
    type = string
}

variable AWS_REGION {
    type = string
}

variable VPC_ID {
    type = string
}

variable "BASE_URL" {
    type = string
}

variable DB_DRIVER {
    type = string
}

variable "DB_HOST" {
    type = string
}

variable "DB_PORT" {
    type = string
}

variable "DB_USER" {
    type = string
}

variable "DB_PASSWORD" {
    type = string
}

variable "DB_NAME" {
    type = string
}

variable "DB_SCHEMA" {
    type = string
}

variable "S3_BUCKET" {
    type = string
}

variable "SES_SOURCE_EMAIL" {
    type = string
}

variable "SES_RECIPIENT_EMAIL" {
    type = string
}

variable "subnet_ids" {
    description = "List of subnet IDs where Lambda should run"
    type        = list(string)
    default = ["subnet-02fed49230af8b602", "subnet-00c8d9ab175e125f9", "subnet-08d9dabb018bb400b"]
}