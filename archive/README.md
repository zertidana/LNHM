# 📜 Archive

This directory contains the scripts used to upload a summary of daily plant reading data data to the archive for storage and analysis.

## 📁 File Structure

- `archive_plant_reading.py`
    Defines the lambda handler for the AWS lambda function which uploads a daily summary of data from the RDS to the s3 bucket.
- `Dockerfile`
    Builds the docker image used to package and deploy the AWS lambda function.
- `utilities.py`
    Contains helper functions which are used in `archive.py` to set up logging.

