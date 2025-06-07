
# Alerter

This directory contains the scripts required to send alerts via AWS SES.

## File Structure

- `send_alerts.py`
    Defines the lambda handler for the AWS lambda function which sends alerts based on a previous lambda event output (plants requiring attention or containing errors).
- `Dockerfile`
    Builds the docker image used to package and deploy the AWS lambda function.

## Alerter Docker Container

To build the terraform container and push it to an ECR repository for use as a Lambda, run:

1. `docker build --platform linux/amd64 --provenance=false -t [your-container-name] .`
2. `docker tag [your-container-name]:latest [your-ecr-repo-id]`
3. `docker push [your-ecr-repo-id]:latest`                           
