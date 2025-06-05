##################### Cloud Provisions #################
provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY_ID
    secret_key = var.AWS_SECRET_ACCESS_KEY
}

data "aws_vpc" "c17-vpc" {
    id = var.VPC_ID
}

data "aws_db_subnet_group" "subnet-group" {
    name = "c17-public-subnet-group"
}

###################### ECR ############################
data "aws_ecr_repository" "etl_lambda_image_repo" {
    name = "c17-raffles-etl-lambda"
}

data "aws_ecr_image" "etl_lambda_image" {
    repository_name = data.aws_ecr_repository.etl_lambda_image_repo.name
    image_tag       = "latest"
}

data "aws_ecr_repository" "health_check_image_repo" {
    name = "c17-raffles-plant-health-lambda"
}

data "aws_ecr_image" "health_check_image" {
    repository_name = data.aws_ecr_repository.health_check_image_repo.name
    image_tag       = "latest"
}

######################### Lambda ##########################
data "aws_iam_policy_document" "lambda-role-trust-policy-doc" {
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

data "aws_iam_policy_document" "lambda-role-permissions-policy-doc" {
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
        "s3:*"
      ]
      resources = [ "*" ]
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
        "ses:SendEmail",
        "ses:SendRawEmail"
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

resource "aws_iam_role" "lambda-role" {
    name = "c17-raffles-lambda-role"
    assume_role_policy = data.aws_iam_policy_document.lambda-role-trust-policy-doc.json
}

resource "aws_iam_policy" "lambda-role-permissions-policy" {
    name = "c17-raffles-lambda-permissions-policy"
    policy = data.aws_iam_policy_document.lambda-role-permissions-policy-doc.json
}

resource "aws_iam_role_policy_attachment" "lambda-role-policy-connection" {
    role = aws_iam_role.lambda-role.name
    policy_arn = aws_iam_policy.lambda-role-permissions-policy.arn
}

resource "aws_lambda_function" "etl_lambda" {
    function_name = "c17-raffles-etl-lambda"
    role = aws_iam_role.lambda-role.arn
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
    vpc_config {
        subnet_ids         = data.aws_db_subnet_group.subnet-group.subnet_ids
        security_group_ids = [aws_security_group.lambda_sg.id]
    }
}


resource "aws_lambda_function" "health_check_lambda" {
    function_name = "c17-raffles-plant-health-check-lambda"
    role = aws_iam_role.lambda-role.arn
    package_type = "Image"
    image_uri = data.aws_ecr_image.health_check_image.image_uri
    timeout = 30
    environment {
        variables = {
            DB_DRIVER = var.DB_DRIVER
            DB_HOST = var.DB_HOST
            DB_PORT = var.DB_PORT
            DB_USER = var.DB_USER
            DB_PASSWORD = var.DB_PASSWORD
            DB_NAME = var.DB_NAME
            DB_SCHEMA = var.DB_SCHEMA
            SES_REGION = var.AWS_REGION
        }
    }
    vpc_config {
        subnet_ids         = data.aws_db_subnet_group.subnet-group.subnet_ids
        security_group_ids = [aws_security_group.lambda_sg.id]
    }
}

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

resource "aws_cloudwatch_log_group" "etl_lambda_logs" {
    name              = "/aws/lambda/${aws_lambda_function.etl_lambda.function_name}"
    retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "health_check_lambda_logs" {
    name              = "/aws/lambda/${aws_lambda_function.health_check_lambda.function_name}"
    retention_in_days = 14
}

###################### S3 ##########################
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

###################### EventBridge ##########################

resource "aws_cloudwatch_event_rule" "etl_schedule" {
    name                = "c17-raffles-etl-schedule"
    description         = "Trigger ETL pipeline every minute"
    schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "etl_target" {
    rule      = aws_cloudwatch_event_rule.etl_schedule.name
    target_id = "ETLLambda"
    arn       = aws_lambda_function.etl_lambda.arn
    role_arn  = aws_iam_role.lambda-role.arn
}

resource "aws_lambda_permission" "allow_etl_eventbridge" {
    statement_id  = "AllowETLEventBridgeInvoke"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.etl_lambda.function_name
    principal     = "events.amazonaws.com"
    source_arn    = aws_cloudwatch_event_rule.etl_schedule.arn
}

resource "aws_cloudwatch_event_rule" "rds_write_rule" {
    name        = "c17-raffles-rds-write-rule"
    description = "Trigger health check when RDS is written to"

    event_pattern = jsonencode({
        source      = ["aws.rds"]
        detail-type = ["AWS API Call via CloudTrail"]
        detail = {
            eventName = ["ExecuteStatement"]
            requestParameters = {
                databaseName = [var.DB_NAME]
            }
        }
    })
}

resource "aws_cloudwatch_event_target" "health_check_target" {
    rule      = aws_cloudwatch_event_rule.rds_write_rule.name
    target_id = "HealthCheckLambda"
    arn       = aws_lambda_function.health_check_lambda.arn
    role_arn  = aws_iam_role.lambda-role.arn
}

resource "aws_lambda_permission" "allow_health_check_eventbridge" {
    statement_id  = "AllowHealthCheckEventBridgeInvoke"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.health_check_lambda.function_name
    principal     = "events.amazonaws.com"
    source_arn    = aws_cloudwatch_event_rule.rds_write_rule.arn
}
