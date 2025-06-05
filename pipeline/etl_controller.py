"""A script which runs all stages of the ETL pipeline."""
from os import environ as ENV
from dotenv import load_dotenv
import pandas as pd
from extract import PlantAPIClient
from transform import clean_dataframe
from load import insert_transformed_dataframe

from utilities import get_logger, set_logger


def run_pipeline() -> None:
    """Runs each stage of the pipeline in succession."""
    set_logger()
    load_dotenv()
    # Pull plant data from API
    client = PlantAPIClient(ENV["BASE_URL"])
    plant_data = client.get_all_plants()
    plant_df = pd.DataFrame.from_dict(plant_data)
    print(plant_df)
    # Clean plant data (transform)
    transformed_dataframe = clean_dataframe(plant_df)
    # Load to RDS
    insert_transformed_dataframe(transformed_dataframe)


if __name__ == "__main__":
    run_pipeline()
