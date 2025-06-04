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
resource "aws_ecr_repository" "ecr-repo" {
    name                 = "c17-raffles-lnhm-pipeline"
    image_tag_mutability = "MUTABLE"
    force_delete = true
    image_scanning_configuration {
    scan_on_push = true
    }
}

data "aws_ecr_image" "lambda-image-version" {
    repository_name = data.aws_ecr_repository.ecr-repo.name
    image_tag       = "latest"
}

####################### ECS ##########################

resource "aws_security_group" "ecs_service_sg" {
    name        = "c17-raffles-etl-ecs-service-sg"
    description = "Security group for ECS service tasks"
    vpc_id      = data.aws_vpc.c17-vpc.id

    egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_ecs_task_definition" "etl_task-definition" {
    
    family                   = "c17-raffles-pipeline-td"
    requires_compatibilities = ["EC2"]
    network_mode             = "awsvpc"
    cpu                      = "512"
    memory                   = "1024"
    execution_role_arn = var.EXECUTION_ROLE_ARN

    container_definitions = jsonencode([
        {
        name      = "etl"
        image = data.aws_ecr_image.lambda-image-version.image_uri
        essential = true
        environment = var.CONTAINER_ENV_VARS,
        logConfiguration = {
            logDriver = "awslogs"
            options = {
            "awslogs-group"         = var.LOG_GROUP
            "mode"                  = "non-blocking"
            "awslogs-create-group"  = "true"
            "max-buffer-size"       = "25m"
            "awslogs-region"        = "eu-west-2"
            "awslogs-stream-prefix" = "ecs"
            }
        }
        }
    ])
}

resource "aws_ecs_service" "ecs-service" {
    name            = "c17-raffles-etl-service"
    cluster         = var.ECS_CLUSTER_ID
    task_definition = aws_ecs_task_definition.etl_task.arn
    desired_count   = 1
    launch_type     = "EC2"

    network_configuration {
        subnets          = var.PUBLIC_SUBNET_IDS
        assign_public_ip = true
        security_groups  = [aws_security_group.ecs_service_sg.id]
    }

    deployment_minimum_healthy_percent = 50
    deployment_maximum_percent         = 200
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
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
      ]
      resources = [ "arn:aws:logs:eu-west-2:129033205317:*" ] # Do we need our own here?
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
        "glue:*",
        "athena:*"
      ]
      resources = [ "*" ]
    }
}

# Role (thing that can be assumed to get power)
resource "aws_iam_role" "lambda-role" {
    name = "c17-raffles-lambda-email-terraform-role"
    assume_role_policy = data.aws_iam_policy_document.lambda-role-trust-policy-doc.json
}

resource "aws_iam_policy" "lambda-role-permissions-policy" {
    name = "c17-raffles-lambda-email-permissions-policy"
    policy = data.aws_iam_policy_document.lambda-role-permissions-policy-doc.json
}

# Connect the policy to the role
resource "aws_iam_role_policy_attachment" "lambda-role-policy-connection" {
    role = aws_iam_role.lambda-role.name
    policy_arn = aws_iam_policy.lambda-role-permissions-policy.arn
}

resource "aws_lambda_function" "raffles-alert-lambda" {
    function_name = "c17-raffle-alert-lambda"
    role = aws_iam_role.lambda-role.arn
    package_type = "Image"
    image_uri = data.aws_ecr_image.lambda-image-version.image_uri
    timeout = 120
    environment {
        variables = {
            AWS_REGION_NAME = "eu-west-2", # Obviously we'll change these / extract them out into tfvars
            ATHENA_DB_NAME = "c17-xac-trucks-db",
            ATHENA_OUTPUT_LOCATION = "s3:/athena/output/",
            TARGET_BUCKET_NAME = "c17-xac-trucks",

        }
    }
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
