- Connect VPC (Done)
- Connect Subnet (Done)
- Security groups (EC2, s3, RDS, lambda)
- IAM roles and policies? 
- ECR repository (Done)
- ECS task using an EC2 (needs docker image) (Done)

- s3 bucket to store archive data (Done)
- Glue crawler to query archive data
    - Glue database
    - Glue crawler
    - IAM role
- Lambda function to check for notifs
    - IAM policy fot lambda to SNS and SES
- SNS to send message
    - SNS topic
    - SNS topic subscription
- SES to send email (topics, subscriptions and identities)
    - IAM policies
    - Can’t verify email using terraform 