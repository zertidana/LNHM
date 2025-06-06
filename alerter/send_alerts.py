"""A script which processes plant reading errors and sends HTML email
alerts to botanists via AWS SES"""

from io import StringIO
from os import environ as ENV
from datetime import datetime, timedelta
import json
import pandas as pd
from boto3 import client


def create_ses_client() -> client:
    """Returns an AWS SES client for sending emails."""
    return client("ses", region_name=ENV.get("AWS_REGION", "eu-west-2"))


def create_s3_client() -> client:
    """Returns an AWS S3 client for tracking sent alerts."""
    return client("s3", region_name=ENV.get("AWS_REGION", "eu-west-2"))


def extract_error_from_event(event) -> pd.DataFrame:
    """Extract the error dataframe from the AWS Step Function."""
    error_data = event.get("error_data", [])
    if not error_data:
        logger.info("No plant health readings contain errors.")
        return pd.DataFrame()

    return pd.DataFrame(error_data)


def send_ses_email(ses_client, html_content: str, error_count: int) -> None:
    """Send the HTML email alert via AWS SES."""


def get_previous_alerts_from_s3(s3_client) -> pd.DataFrame:
    """Get previously sent alerts from AWS S3."""


def save_alert_history_to_s3(s3_client, error_data: pd.DataFrame) -> None:
    """Save the alert history to AWS S3 as a json."""
    json_data = error_data.to_json(orient="records", date_format="iso")

    s3_client.put_object(
        Bucket=ENV["S3_BUCKET"],
        Key=f"alert_history/alert_history_{datetime.now():%Y-%m-%d_%H%M%S}",
        Body=json_data,
        ContentType="application/json"
    )
    logger.info(f"Alert history saved to S3: {datetime.now():%Y-%m-%d_%H%M%S}")


def run_plant_alerter(event) -> dict:
    """Run all components of the plant alerter process."""


def alerter_lambda_handler(event, context):
    """AWS Lambda handler to trigger plant alerting process."""


if __name__ == "__main__":
    pass
