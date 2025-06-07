"""A script which archives a summary of short term 
storage data (last 24hr) as a CSV file and uploads to AWS S3."""
import io
from datetime import datetime
from os import environ as ENV
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from dotenv import load_dotenv
from boto3 import client
from botocore.exceptions import BotoCoreError, ClientError
from utils import set_logger, get_logger


def create_tsql_engine() -> sqlalchemy.Engine:
    """Returns a tsql engine based on .env variables."""
    return sqlalchemy.create_engine(
        (f"mssql+pyodbc://{ENV['DB_USER']}:{ENV['DB_PASSWORD']}"
         f"@{ENV['DB_HOST']}/{ENV['DB_NAME']}?driver={ENV['DB_DRIVER']}"),
        connect_args={'connect_timeout': 10,
                      'TrustServerCertificate': 'yes'},
        echo=False)


def dataframe_daily_summary(df: pd.DataFrame, date: datetime) -> pd.DataFrame:
    """Returns a daily summary of plant health data for a given day."""
    logger = get_logger()

    df_valid = df[df['error_msg'].isna()].copy()

    summarised_day_data = df_valid.groupby('plant_id').agg({
        'temperature': 'mean',
        'soil_moisture': 'mean',
        'recording_taken': 'count',
        'last_watered': 'max'
    }).reset_index()

    summarised_day_data.rename(columns={
        'temperature': 'avg_temperature',
        'soil_moisture': 'avg_soil_moisture',
        'recording_taken': 'recording_count',
    }, inplace=True)
    summarised_day_data['date'] = date.strftime("%Y-%m-%d")

    logger.info("Summarised data for day %s.",
                date.strftime("%Y-%m-%d"))
    return summarised_day_data


def get_day_plant_readings(engine: sqlalchemy.Engine) -> pd.DataFrame:
    """Returns all plant readings as a dataframe."""
    logger = get_logger()
    try:
        query = "SELECT * FROM FACT_plant_reading"
        logger.info("Successfully retrieved daily plant data.")
        return pd.read_sql(query, engine)
    except SQLAlchemyError as exc:
        logger.critical(exc)
        raise exc


def cleanup_plant_readings(engine: sqlalchemy.Engine) -> None:
    """Deletes all rows from the FACT_plant_reading table."""
    logger = get_logger()
    with engine.connect() as conn:
        try:
            conn.execute(sqlalchemy.text("DELETE FROM FACT_plant_reading"))
            conn.commit()
            logger.info("All rows deleted from FACT_plant_reading.")
        except SQLAlchemyError as exc:
            logger.critical(exc)
            raise exc


def upload_day_summary_as_csv(df: pd.DataFrame) -> None:
    """Uploads a dataframe of a day's summary of plant readings as CSV."""
    s3_client = client(
        's3',
        region_name=ENV.get('AWS_REGION', 'eu-west-2')
    )

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    try:
        s3_client.put_object(
            Bucket=ENV["S3_BUCKET"],
            Key=f"daily_summaries/plant_readings_{datetime.now():%Y-%m-%d}.csv",
            Body=csv_buffer.getvalue()
        )
    except (BotoCoreError, ClientError) as exc:
        get_logger().critical("S3 upload failed: %s", exc)
        raise


def run_summarise_and_delete() -> None:
    """Run all components of this script to summarise plant readings, 
    upload to S3 and clear the RDS db."""
    set_logger()
    load_dotenv()
    eng = create_tsql_engine()
    df = get_day_plant_readings(eng)
    summarised_day_data = dataframe_daily_summary(df, datetime.today())
    upload_day_summary_as_csv(summarised_day_data)
    cleanup_plant_readings(eng)


def archive_lambda_handler(event, context):
    """AWS Lambda handler to trigger ETL pipeline."""
    try:
        run_summarise_and_delete()
        return {
            "statusCode": 200,
            "body": "Succesfully summarised daily "
            "plant readings, uploaded to S3 and cleaned up the db."
        }
    except (SQLAlchemyError, BotoCoreError,
            ClientError) as exc:
        return {
            "statusCode": 500,
            "body": f"S3 Archiver failed due to processing error: {str(exc)}"
        }


if __name__ == "__main__":
    pass
    # run_summarise_and_delete()
