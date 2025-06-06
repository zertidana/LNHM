######################### 
### Cloud Provisions
#########################
provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY_ID
    secret_key = var.AWS_SECRET_ACCESS_KEY
}

data "aws_vpc" "c17-vpc" {
    id = var.VPC_ID
}


#########################
### ECR 
#########################
data "aws_ecr_repository" "etl_lambda_image_repo" {
    name = "c17-raffles-etl-lambda"
}

data "aws_ecr_image" "etl_lambda_image" {
    repository_name = data.aws_ecr_repository.etl_lambda_image_repo.name
    image_tag       = "latest"
}

data "aws_ecr_repository" "archiver_lambda_image_repo" {
    name = "c17-raffles-archiver-lambda"
}

data "aws_ecr_image" "archive_lambda_image" {
  repository_name = data.aws_ecr_repository.archiver_lambda_image_repo.name
  image_tag       = "latest"
}

# data "aws_ecr_repository" "health_check_image_repo" {
#     name = "c17-raffles-plant-health-lambda"
# }

# data "aws_ecr_image" "health_check_image" {
#     repository_name = data.aws_ecr_repository.health_check_image_repo.name
#     image_tag       = "latest"
# }

#########################
### Lambda 
#########################
data "aws_iam_policy_document" "lambda_role_trust_policy_doc" {
    statement {
      effect = "Allow"
      principals {
        type = "Service"
        identifiers = [ "lambda.amazonaws.com" ]
      }
      actions = [
        "sts:AssumeRole"
      ]
    }
}

data "aws_iam_policy_document" "etl_lambda_role_permissions_policy_doc" {
    statement {
      effect = "Allow"
      actions = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
      ]
      resources = [ "arn:aws:logs:eu-west-2:129033205317:*" ]
    }

    statement {
      effect = "Allow"
      actions = [
        "rds-db:connect",
        "rds:*"
      ]
      resources = [ "*" ]
    }

    statement {
      effect = "Allow"
      actions = [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface",
        "ec2:AssignPrivateIpAddresses",
        "ec2:UnassignPrivateIpAddresses"
      ]
      resources = ["*"]
    }
}

data "aws_iam_policy_document" "archiver_lambda_role_permissions_policy_doc" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]
    resources = ["arn:aws:s3:::c17-raffles-lnhm-bucket/*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "rds-db:connect"
    ]
    resources = [
      "arn:aws:rds-db:eu-west-2:129033205317:dbuser:c17-plants-db/beta"
    ]
  }
}

resource "aws_iam_role" "etl_lambda_role" {
    name = "c17-raffles-etl-lambda-role"
    assume_role_policy = data.aws_iam_policy_document.lambda_role_trust_policy_doc.json
}

resource "aws_iam_role" "archiver_lambda_role" {
  name = "c17-raffles-archiver-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_role_trust_policy_doc.json
}

resource "aws_iam_policy" "etl_lambda_role_permissions_policy" {
    name = "c17-raffles-etl-lambda-permissions-policy"
    policy = data.aws_iam_policy_document.etl_lambda_role_permissions_policy_doc.json
}

resource "aws_iam_policy" "archiver_lambda_role_permissions_policy" {
    name = "c17-raffles-archiver-lambda-permissions-policy"
    policy = data.aws_iam_policy_document.archiver_lambda_role_permissions_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "etl_lambda_role_policy_connection" {
    role = aws_iam_role.etl_lambda_role.name
    policy_arn = aws_iam_policy.etl_lambda_role_permissions_policy.arn
}
 
resource "aws_iam_role_policy_attachment" "archiver_lambda_role_policy_connection" {
  role       = aws_iam_role.archiver_lambda_role.name
  policy_arn = aws_iam_policy.archiver_lambda_role_permissions_policy.arn
}

resource "aws_lambda_function" "etl_lambda" {
    function_name = "c17-raffles-etl-lambda"
    role = aws_iam_role.etl_lambda_role.arn
    package_type = "Image"
    image_uri = data.aws_ecr_image.etl_lambda_image.image_uri
    timeout = 120
    environment {
        variables = {
            BASE_URL = var.BASE_URL
            DB_DRIVER = var.DB_DRIVER
            DB_HOST = var.DB_HOST
            DB_PORT = var.DB_PORT
            DB_USER = var.DB_USER
            DB_PASSWORD = var.DB_PASSWORD
            DB_NAME = var.DB_NAME
            DB_SCHEMA = var.DB_SCHEMA
        }
    }
}

resource "aws_lambda_function" "archiver_lambda" {
    function_name = "c17-raffles-archiver-lambda"
    role = aws_iam_role.archiver_lambda_role.arn
    package_type = "Image"
    image_uri = data.aws_ecr_image.archive_lambda_image.image_uri
    timeout = 120
    environment {
        variables = {
            S3_BUCKET = var.S3_BUCKET
            DB_DRIVER = var.DB_DRIVER
            DB_HOST = var.DB_HOST
            DB_PORT = var.DB_PORT
            DB_USER = var.DB_USER
            DB_PASSWORD = var.DB_PASSWORD
            DB_NAME = var.DB_NAME
            DB_SCHEMA = var.DB_SCHEMA
        }
    }
}


# resource "aws_lambda_function" "health_check_lambda" {
#     function_name = "c17-raffles-plant-health-check-lambda"
#     role = aws_iam_role.lambda_role.arn
#     package_type = "Image"
#     image_uri = data.aws_ecr_image.health_check_image.image_uri
#     timeout = 30
#     environment {
#         variables = {
#             DB_DRIVER = var.DB_DRIVER
#             DB_HOST = var.DB_HOST
#             DB_PORT = var.DB_PORT
#             DB_USER = var.DB_USER
#             DB_PASSWORD = var.DB_PASSWORD
#             DB_NAME = var.DB_NAME
#             DB_SCHEMA = var.DB_SCHEMA
#             SES_REGION = var.AWS_REGION
#         }
#     }
# }

resource "aws_security_group" "lambda_sg" {
    name        = "c17-lambda-sg"
    description = "Security group for Lambda functions"
    vpc_id      = data.aws_vpc.c17-vpc.id

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

data "aws_cloudwatch_log_group" "etl_lambda_logs" {
    name              = "/aws/lambda/${aws_lambda_function.etl_lambda.function_name}"
}

resource "aws_cloudwatch_log_group" "archiver_lambda_logs" {
    name              = "/aws/lambda/${aws_lambda_function.archiver_lambda.function_name}"
    retention_in_days = 14
}

# resource "aws_cloudwatch_log_group" "health_check_lambda_logs" {
#     name              = "/aws/lambda/${aws_lambda_function.health_check_lambda.function_name}"
#     retention_in_days = 14
# }

#########################
### S3 
#########################
resource "aws_s3_bucket" "archive_data_bucket" {
    bucket = "c17-raffles-lnhm-bucket"
    force_destroy = true
}

resource "aws_s3_object" "input" {
    bucket  = aws_s3_bucket.archive_data_bucket.id
    key     = "input/"
}

resource "aws_s3_object" "output_directory" {
    bucket  = aws_s3_bucket.archive_data_bucket.id
    key     = "output/"
}

######################### 
### EventBridge Scheduler
#########################

# Roles
resource "aws_iam_role" "scheduler_role" {
    name = "c17-raffles-scheduler-role"

    assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
        {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
            Service = "scheduler.amazonaws.com"
        }
        }
    ]
    })
}

resource "aws_iam_role_policy" "scheduler_lambda_policy" {
    name = "scheduler-lambda-invoke"
    role = aws_iam_role.scheduler_role.id

    policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
        {
        Effect = "Allow"
        Action = "lambda:InvokeFunction"
        Resource = [
            aws_lambda_function.etl_lambda.arn,
            aws_lambda_function.archiver_lambda.arn
        ]
        }
    ]
    })
}

# ETL Event Scheduler
resource "aws_scheduler_schedule_group" "etl_group" {
    name = "c17-raffles-etl-group"
}

resource "aws_scheduler_schedule" "etl_schedule" {
    name       = "c17-raffles-etl-schedule"
    group_name = aws_scheduler_schedule_group.etl_group.name

    flexible_time_window {
    mode = "OFF"
    }

    schedule_expression = "rate(1 minute)"

    target {
        arn      = aws_lambda_function.etl_lambda.arn
        role_arn = aws_iam_role.scheduler_role.arn

        input = jsonencode({
            source = "eventbridge-scheduler"
            time   = "scheduled"
        })
    }

    description = "Trigger ETL pipeline every minute"
    state       = "ENABLED"
}

resource "aws_lambda_permission" "allow_etl_scheduler" {
    statement_id  = "AllowSchedulerInvoke"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.etl_lambda.function_name
    principal     = "scheduler.amazonaws.com"
    source_arn    = aws_scheduler_schedule.etl_schedule.arn

}

# Archiver Scheduler

resource "aws_scheduler_schedule_group" "archiver_group" {
    name = "c17-raffles-archiver-group"
}

resource "aws_scheduler_schedule" "archiver_schedule" {
    name       = "c17-raffles-archiver-schedule"
    group_name = aws_scheduler_schedule_group.archiver_group.name

    flexible_time_window {
    mode = "OFF"
    }

    schedule_expression = "cron(55 23 * * ? *)"
    schedule_expression_timezone = "Europe/London"

    target {
        arn      = aws_lambda_function.archiver_lambda.arn
        role_arn = aws_iam_role.scheduler_role.arn

        input = jsonencode({
            source = "eventbridge-scheduler"
            time   = "scheduled"
        })
    }

    description = "Trigger Archiver once per day"
    state       = "ENABLED"
}

resource "aws_lambda_permission" "allow_archiver_scheduler" {
    statement_id  = "AllowSchedulerInvoke"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.archiver_lambda.function_name
    principal     = "scheduler.amazonaws.com"
    source_arn    = aws_scheduler_schedule.archiver_schedule.arn

}