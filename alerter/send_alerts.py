"""A script which processes plant reading errors and sends HTML email
alerts to botanists via AWS SES"""

from io import StringIO
from os import environ as ENV
from datetime import datetime, timedelta, timezone
import json
import pandas as pd
from boto3 import client
from utilities import set_logger, get_logger


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
    error_data = event.get("error_data", [])
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
                "ToAddresses": ENV["SES_RECIPIENTS"].split(",")
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
        logger.info(f"SES email sent! Message ID: {response['MessageId']}")
    except Exception as e:
        logger.error(f"Failed to send SES email: {e}")
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
            dfs.append(df)

        combined_df = pd.concat(
            dfs, ignore_index=True) if dfs else pd.DataFrame()
        logger.info(
            f"Loaded {len(combined_df)} previous alert records from S3.")
        return combined_df

    except Exception as e:
        logger.error(f"Error retrieving previous alerts from S3: {e}")
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
    logger.info(f"Alert history saved to S3: {datetime.now():%Y-%m-%d_%H%M%S}")


def run_plant_alerter(event) -> dict:
    """Run all components of the plant alerter process."""
    logger = get_logger()

    error_df = extract_error_from_event(event)
    if error_df.empty:
        logger.info("No errors found, no alert will be sent.")
        return {"alert_sent": False, "message": "No errors detected."}

    s3_client = create_s3_client()

    previous_alerts = get_previous_alerts_from_s3(s3_client)
    if not previous_alerts.empty:
        previous_alerts["error_msg"]

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
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Alerter failed: {str(e)}"
        }


if __name__ == "__main__":
    set_logger()
    pass
