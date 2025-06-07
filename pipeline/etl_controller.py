"""A script which runs all stages of the ETL pipeline."""
from os import environ as ENV
from dotenv import load_dotenv
import pandas as pd
from extract import PlantAPIClient
from transform import clean_dataframe
from load import insert_transformed_data

from utils import set_logger, get_logger


def run_pipeline() -> pd.DataFrame:
    """Runs each stage of the pipeline in succession."""
    set_logger()
    load_dotenv()
    try:
        client = PlantAPIClient(ENV["BASE_URL"])
        plant_data = client.get_all_plants()
        if not plant_data:
            return pd.DataFrame()

        plant_df = pd.DataFrame.from_dict(plant_data)
        transformed_dataframe = clean_dataframe(plant_df)
        return insert_transformed_data(transformed_dataframe)
    except Exception as e:
        logger = get_logger()
        logger.error(f"Pipeline failed: {str(e)}")
        return pd.DataFrame()


if __name__ == "__main__":
    run_pipeline()
