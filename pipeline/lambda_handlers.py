"""AWS Lambda entrypoint to run the ETL pipeline."""
from etl_controller import run_pipeline


def etl_lambda_handler(event, context):
    """AWS Lambda handler to trigger ETL pipeline."""
    try:
        run_pipeline()
        return {
            "statusCode": 200,
            "body": "ETL pipeline executed successfully."
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"ETL pipeline failed: {str(e)}"
        }
