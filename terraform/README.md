# 🏗️ Terraform

This directory contains the Terraform code used to provision and manage the AWS infrastructure needed to run the ETL pipeline.

## ☁️ Provisioned Cloud Resources
- **s3 Bucket**  
    Contains daily summary data indefinitely in the form of time-partitioned parquet files.

- **Lambda functions**  
   The main.py file provisions two lambda functions:
    1. batch uploads new sensor readings to a database hosted on AWS RDS.
    2. retrieves any data that is not within the appropriate boundaries for supporting healthy plant growth and triggers an email to be sent to the user with an alert.

- **EventBridge Event**  
    Triggers every minute and invokes the lambda function which batch uploads new sensor readings to the RDS.

- **ECR Repository**  
    Contains the docker images that the lambda functions are based on. 

## 📁 File Structure

- `main.tf`  
  Contains the terraform code that provisions the cloud resources.

- `variables.tf`  
  Declares variables to terraform required by main.tf.

- `terraform.tfvars`  
  Assigns values to the variables declared in variables.tf and required by main.tf.

## 🧪 How to Run
> 🚧 
>Warning: These scripts are used to create and update cloud resources and do not need to be run multiple times.
>
### Creating Resources
- Ensure that you have Terraform installed and that you have connected it to AWS using your AWS credentials.
- Ensure that you are in the directory that contains the terraform files and run `terraform init` in your terminal to initialise the working directory.
- Then run `terraform plan` to see an overview of what will be created.
- Finally run `terraform apply` and enter **'yes'** when prompted to provision or update the resources.

### Deleting Resources
> 🚧 
>Warning: Deleting the cloud resources specified in this document will cause the pipeline to fail and could lead to data loss.
>
- To delete cloud resources you can run `terraform destroy`.
