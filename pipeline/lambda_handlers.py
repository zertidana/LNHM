"""AWS Lambda entrypoint to run the ETL pipeline."""
from etl_controller import run_pipeline
import pandas as pd


def etl_lambda_handler(event, context):
    """AWS Lambda handler to trigger ETL pipeline."""
    try:
        error_data = run_pipeline()
        return {
            "statusCode": 200,
            "body": "ETL pipeline executed successfully.",
            "error_data": error_data.to_dict('records') if not error_data.empty else []
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"ETL pipeline failed: {str(e)}",
            "error_data": []
        }
