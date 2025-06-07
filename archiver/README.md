# 📜 Archive

This directory contains the scripts used to upload a summary of daily plant reading data data to the archive for storage and analysis.

## 📁 File Structure

- `archive_plant_reading.py`
    Defines the lambda handler for the AWS lambda function which uploads a daily summary of data from the RDS to the s3 bucket.
- `Dockerfile`
    Builds the docker image used to package and deploy the AWS lambda function.
    
## Archiver Docker Container

To build the archiver as a docker container and push it to an ECR repository for use as a Lambda, run:

1. `docker build --platform linux/amd64 --provenance=false -t [your-container-name] .`
2. `docker tag [your-container-name]:latest [your-ecr-repo-id]`
3. `docker push [your-ecr-repo-id]:latest`    