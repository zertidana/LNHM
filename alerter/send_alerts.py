"""A script which processes plant reading errors and sends HTML email
alerts to botanists via AWS SES"""

from io import StringIO
from os import environ as ENV
from datetime import datetime, timedelta, timezone
from botocore.exceptions import BotoCoreError, ClientError
import pandas as pd
from boto3 import client
from utils import set_logger, get_logger


def create_ses_client() -> client:
    """Returns an AWS SES client for sending emails."""
    logger = get_logger()
    logger.info("Creating AWS SES client...")
    return client("ses", region_name=ENV.get("AWS_REGION", "eu-west-2"))


def create_s3_client() -> client:
    """Returns an AWS S3 client for tracking sent alerts."""
    logger = get_logger()
    logger.info("Creating S3 client...")
    return client("s3", region_name=ENV.get("AWS_REGION", "eu-west-2"))


def extract_error_from_event(event) -> pd.DataFrame:
    """Extract the error dataframe from the AWS Step Function."""
    logger = get_logger()

    logger.info("Collecting plant errors from last ETL run...")
    if isinstance(event, dict):
        error_data = event.get("etl_result", {}).get("error_data", [])
    else:
        error_data = []

    if not error_data:
        logger.info("No plant health readings contain errors.")
        return pd.DataFrame()

    return pd.DataFrame(error_data)


def create_html_email(df: pd.DataFrame) -> str:
    """Creates a formatted HTML email."""
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    table_html = df.to_html(index=False, classes='alert-table', border=0)
    return f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                }}
                .alert-table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                .alert-table th, .alert-table td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                }}
                .alert-table th {{
                    background-color: #f2f2f2;
                    text-align: left;
                }}
            </style>
        </head>
        <body>
            <h2>Plant Health Alert</h2>
            <p>These readings triggered alerts as of <strong>{timestamp}</strong>:</p>
            {table_html}
            <p>Please investigate these issues promptly.</p>
        </body>
    </html>
    """


def send_ses_email(ses_client: client, html_content: str, error_count: int) -> None:
    """Send the HTML email alert via AWS SES."""
    logger = get_logger()
    try:
        response = ses_client.send_email(
            Source=ENV["SES_SOURCE_EMAIL"],
            Destination={
                "ToAddresses": [ENV["SES_RECIPIENT"]]
            },
            Message={
                "Subject": {
                    "Data": f"Plant Health Alert - {error_count} Attention Required"
                },
                "Body": {
                    "Html": {
                        "Data": html_content
                    }
                }
            }
        )
        logger.info("SES email sent! Message ID: %s", response["MessageId"])
    except Exception as e:
        logger.error("Failed to send SES email: %s", e)
        raise


def get_previous_alerts_from_s3(s3_client: client) -> pd.DataFrame:
    """Get previously sent alerts from AWS S3."""
    logger = get_logger()
    try:
        response = s3_client.list_objects(
            Bucket=ENV["S3_BUCKET"], Prefix="alert_history/")
        contents = response.get("Contents", [])
        if not contents:
            logger.info("No previous alerts found in S3.")
            return pd.DataFrame()

        dfs = []
        for obj in contents:
            key = obj["Key"]
            file_obj = s3_client.get_object(Bucket=ENV["S3_BUCKET"], Key=key)
            file_content = file_obj["Body"].read().decode("utf-8")
            df = pd.read_json(file_content)

            if "last_alert" in df.columns:
                df["last_alert"] = pd.to_datetime(df["last_alert"], utc=True)

            dfs.append(df)

        combined_df = pd.concat(
            dfs, ignore_index=True) if dfs else pd.DataFrame()
        logger.info("Loaded %s previous alert records from S3.",
                    len(combined_df))
        return combined_df

    except BotoCoreError as e:
        logger.error("Error retrieving previous alerts from S3: %s", e)
        return pd.DataFrame()


def save_alert_history_to_s3(s3_client: client, error_data: pd.DataFrame) -> None:
    """Save the alert history to AWS S3 as a json."""
    logger = get_logger()
    error_data["last_alert"] = datetime.now(timezone.utc)
    json_data = error_data.to_json(orient="records", date_format="iso")
    json_buffer = StringIO(json_data)
    s3_client.put_object(
        Bucket=ENV["S3_BUCKET"],
        Key=f"alert_history/alert_history_{datetime.now():%Y-%m-%d_%H%M%S}",
        Body=json_buffer.getvalue(),
        ContentType="application/json"
    )
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    logger.info("Alert history saved to S3: %s", timestamp)


def run_plant_alerter(event) -> dict:
    """Run all components of the plant alerter process."""
    set_logger()
    logger = get_logger()

    error_df = extract_error_from_event(event)
    if error_df.empty:
        logger.info("No errors found, no alert will be sent.")
        return {"alert_sent": False, "message": "No errors detected."}

    s3_client = create_s3_client()

    previous_alerts = get_previous_alerts_from_s3(s3_client)
    if not previous_alerts.empty:
        recent_alerts = previous_alerts[previous_alerts["last_alert"]
                                        > datetime.now(timezone.utc) - timedelta(hours=1)]
        if "plant_id" in error_df.columns:
            error_df = error_df[~error_df["plant_id"].isin(
                recent_alerts["plant_id"])]

        if error_df.empty:
            logger.info(
                "No new errors after filtering out plants recently alerted.")
            return {"alert_sent": False, "message": "No new errors after filtering recent alerts."}

    html_email = create_html_email(error_df)
    ses_client = create_ses_client()
    send_ses_email(ses_client, html_email, len(error_df))
    save_alert_history_to_s3(s3_client, error_df)

    logger.info("Plant alerter process completed successfully.")
    return {"alert_sent": True, "alert_count": len(error_df)}


def alerter_lambda_handler(event, context):
    """AWS Lambda handler to trigger plant alerting process."""
    try:
        run_plant_alerter(event)
        return {
            "statusCode": 200,
            "body": "Alerter executed successfully."
        }
    except (BotoCoreError, ClientError) as e:
        return {
            "statusCode": 500,
            "body": f"Alerter failed: {str(e)}"
        }
