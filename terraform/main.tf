######################### 
### Cloud Provisions
#########################
provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY_ID
    secret_key = var.AWS_SECRET_ACCESS_KEY
}

variable "vpc_id" {
    description = "VPC ID where RDS is located"
    type        = string
    default     = "vpc-00b3f6b2893c390f2"
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

data "aws_ecr_repository" "plant_health_alert_image_repo" {
    name = "c17-raffles-plant-health-lambda"
}

data "aws_ecr_image" "plant_health_alert_image" {
    repository_name = data.aws_ecr_repository.plant_health_alert_image_repo.name
    image_tag       = "latest"
}

#########################
### IAM 
#########################

resource "aws_iam_role" "step_function_role" {
  name = "c17-raffles-step-function-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "states.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

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

resource "aws_iam_role_policy" "scheduler_step_function_policy" {
    name = "scheduler-step-function-invoke"
    role = aws_iam_role.scheduler_role.id

    policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
        {
        Effect = "Allow"
        Action = "states:StartExecution"
        Resource = aws_sfn_state_machine.raffles_etl_workflow.arn
        },
        {
        Effect = "Allow"
        Action = "lambda:InvokeFunction"
        Resource = [
            aws_lambda_function.archiver_lambda.arn
        ]
        }
    ]
    })
}

resource "aws_iam_policy" "step_function_policy" {
  name = "c17-raffles-step-function-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          aws_lambda_function.etl_lambda.arn,
          aws_lambda_function.plant_health_alert_lambda.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogDelivery",
          "logs:GetLogDelivery",
          "logs:UpdateLogDelivery",
          "logs:DeleteLogDelivery",
          "logs:ListLogDeliveries",
          "logs:PutResourcePolicy",
          "logs:DescribeResourcePolicies",
          "logs:DescribeLogGroups"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution",
          "states:DescribeExecution",
          "states:StopExecution"
        ]
        Resource = aws_sfn_state_machine.raffles_etl_workflow.arn
      }
    ]
  })
}

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
      resources = [ "arn:aws:logs:*:*:*" ]
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

data "aws_iam_policy_document" "plant_health_alert_lambda_role_permissions_policy_doc" {
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
      "ses:SendEmail",
      "ses:SendRawEmail"
    ]
    resources = ["*"]
  }

}

resource "aws_iam_policy" "step_function_lambda_invoke_policy" {
  name = "c17-raffles-step-function-lambda-invoke-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "lambda:InvokeFunction"
        Resource = [
          aws_lambda_function.etl_lambda.arn,
          aws_lambda_function.plant_health_alert_lambda.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "step_function_lambda_invoke" {
  role       = aws_iam_role.step_function_role.name
  policy_arn = aws_iam_policy.step_function_lambda_invoke_policy.arn
}

resource "aws_iam_role" "etl_lambda_role" {
    name = "c17-raffles-etl-lambda-role"
    assume_role_policy = data.aws_iam_policy_document.lambda_role_trust_policy_doc.json
}

resource "aws_iam_role" "archiver_lambda_role" {
  name = "c17-raffles-archiver-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_role_trust_policy_doc.json
}

resource "aws_iam_role" "plant_health_alert_lambda_role" {
  name = "c17-raffles-alerter-lambda-role"
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

resource "aws_iam_policy" "plant_health_alert_lambda_role_permissions_policy" {
    name = "c17-raffles-plant-health-alert-lambda-permissions-policy"
    policy = data.aws_iam_policy_document.plant_health_alert_lambda_role_permissions_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "etl_lambda_role_policy_connection" {
    role = aws_iam_role.etl_lambda_role.name
    policy_arn = aws_iam_policy.etl_lambda_role_permissions_policy.arn
}
 
resource "aws_iam_role_policy_attachment" "archiver_lambda_role_policy_connection" {
  role       = aws_iam_role.archiver_lambda_role.name
  policy_arn = aws_iam_policy.archiver_lambda_role_permissions_policy.arn
}

resource "aws_iam_role_policy_attachment" "plant_health_alert_lambda_role_policy_connection" {
  role       = aws_iam_role.plant_health_alert_lambda_role.name
  policy_arn = aws_iam_policy.plant_health_alert_lambda_role_permissions_policy.arn
}


resource "aws_iam_role_policy_attachment" "step_function_policy_attachment" {
  role       = aws_iam_role.step_function_role.name
  policy_arn = aws_iam_policy.step_function_policy.arn
}

#########################
### Lambda 
#########################
resource "aws_lambda_function" "etl_lambda" {
    function_name = "c17-raffles-etl-lambda"
    role = aws_iam_role.etl_lambda_role.arn
    package_type = "Image"
    image_uri = data.aws_ecr_image.etl_lambda_image.image_uri
    timeout = 120
    vpc_config {
        subnet_ids         = var.subnet_ids
        security_group_ids = [aws_security_group.lambda_sg.id]
    }
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


resource "aws_lambda_function" "plant_health_alert_lambda" {
    function_name = "c17-raffles-plant-health-check-lambda"
    role = aws_iam_role.plant_health_alert_lambda_role.arn
    package_type = "Image"
    image_uri = data.aws_ecr_image.plant_health_alert_image.image_uri
    timeout = 30
    environment {
        variables = {
            S3_BUCKET = var.S3_BUCKET
            SES_REGION = var.AWS_REGION
            SES_RECIPIENT_EMAIL = var.SES_RECIPIENT_EMAIL
            SES_SOURCE_EMAIL = var.SES_SOURCE_EMAIL
        }
    }
}

resource "aws_security_group" "lambda_sg" {
    name        = "c17-raffles-lambda-sg"
    description = "Security group for Lambda functions"
    vpc_id      = var.vpc_id

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = {
        Name = "c17-raffles-lambda-sg"
    }
}

#########################
### Cloudwatch Log Group 
#########################

resource "aws_cloudwatch_log_group" "etl_lambda_logs" {
    name              = "/aws/lambda/${aws_lambda_function.etl_lambda.function_name}"
    retention_in_days = 14
    lifecycle {
        create_before_destroy = true
    }
}

resource "aws_cloudwatch_log_group" "archiver_lambda_logs" {
    name              = "/aws/lambda/${aws_lambda_function.archiver_lambda.function_name}"
    retention_in_days = 14
    lifecycle {
        create_before_destroy = true
    }
}

resource "aws_cloudwatch_log_group" "plant_health_alert_lambda_logs" {
    name              = "/aws/lambda/${aws_lambda_function.plant_health_alert_lambda.function_name}"
    retention_in_days = 14
    lifecycle {
        create_before_destroy = true
    }
}

resource "aws_cloudwatch_log_group" "step_function_logs" {
    name              = "/aws/states/c17-raffles-etl-alerts-workflow"
    retention_in_days = 14
    lifecycle {
        create_before_destroy = true
    }
}

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
        arn      = aws_sfn_state_machine.raffles_etl_workflow.arn
        role_arn = aws_iam_role.scheduler_role.arn

        input = jsonencode({
            source = "eventbridge-scheduler"
            time   = "scheduled"
        })
    }

    description = "Trigger ETL pipeline and Alerter every minute"
    state       = "ENABLED"
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

######################### 
### Lambda Permissions
#########################

resource "aws_lambda_permission" "allow_archiver_scheduler" {
    statement_id  = "AllowSchedulerInvoke"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.archiver_lambda.function_name
    principal     = "scheduler.amazonaws.com"
    source_arn    = aws_scheduler_schedule.archiver_schedule.arn

}

resource "aws_lambda_permission" "allow_step_function_etl" {
  statement_id  = "AllowStepFunctionInvokeETL"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.etl_lambda.function_name
  principal     = "states.amazonaws.com"
  source_arn    = aws_sfn_state_machine.raffles_etl_workflow.arn
}

resource "aws_lambda_permission" "allow_step_function_alerter" {
  statement_id  = "AllowStepFunctionInvokeAlerter"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.plant_health_alert_lambda.function_name
  principal     = "states.amazonaws.com"
  source_arn    = aws_sfn_state_machine.raffles_etl_workflow.arn
}

######################### 
### Step Function
#########################

resource "aws_sfn_state_machine" "raffles_etl_workflow" {
    name     = "c17-raffles-etl-alerts-workflow"
    role_arn = aws_iam_role.step_function_role.arn

    definition = jsonencode({
        Comment = "ETL and Alert workflow with data passing"
        StartAt = "RunETLLambda"
        States = {
        RunETLLambda = {
            Type = "Task"
            Resource = aws_lambda_function.etl_lambda.arn
            ResultPath = "$.etl_result"
            Next = "RunAlerterLambda"
            Catch = [
            {
                ErrorEquals = ["States.ALL"]
                Next = "HandleETLFailure"
                ResultPath = "$.error"
            }
            ]
        }
        RunAlerterLambda = {
            Type = "Task"
            Resource = aws_lambda_function.plant_health_alert_lambda.arn
            InputPath = "$"
            End = true
            Catch = [
            {
                ErrorEquals = ["States.ALL"]
                Next = "HandleAlerterFailure"
                ResultPath = "$.error"
            }
            ]
        }
        HandleETLFailure = {
            Type = "Fail"
            Cause = "ETL Lambda failed"
            Error = "ETLLambdaError"
        }
        HandleAlerterFailure = {
            Type = "Fail"
            Cause = "Alerter Lambda failed"
            Error = "AlerterLambdaError"
        }
        }
    })

    logging_configuration {
        level                  = "ALL"
        include_execution_data = true
        log_destination        = "${aws_cloudwatch_log_group.step_function_logs.arn}:*"
    }
}