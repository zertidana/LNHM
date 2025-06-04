"""Standardisation and normalisation of the plant data in csv before loading to DB."""

import pandas as pd

from log import get_logger, set_logger


def load_data(file_path: str = 'data/output.csv') -> pd.DataFrame:
    """Loads the unclean data from csv."""
    logger = get_logger()
    if not isinstance(file_path, str):
        logger.critical("Invalid URL type.")
        raise TypeError("Invalid URL type.")
    if file_path[-4:] != ".csv":
        logger.critical("Filename doesn't end in .csv.")
        raise ValueError("Please end your filename in .csv.")
    return pd.read_csv(file_path)


def clean_dataframe(file_path: str = 'data/output.csv') -> pd.DataFrame:
    """Cleans the dataframe."""
    logger = get_logger()
    logger.info("Loading data from file path...")
    try:
        input_dataframe = load_data(file_path)
    except Exception as exc:
        logger.info("Data did not successfully load.")
    logger.info("Data successfully loaded!")

    logger.info("Checking data columns..")
    new_dataframe = input_dataframe[
        'plant_id': 'plant_id'
        'temperature': 'temperature',
        'soil_moisture': 'soil_moisture',
        'recording_taken': 'recording_taken',
        'last_watered': 'last_watered'
    ]
    new_dataframe = new_dataframe[['plant_id', 'temperature',
                                   'soil_moisture', 'recording_taken',
                                   'last_watered']]

    """
    CHECK FOR NULL VALUES every single one of these needs to be included (NOT NULL)
    Throw critical notification if <30% moisture (to do with email/SNS)

    plant_id = int
    temperature = float
    soil_moisture = float
    recording_taken = timestamptz
    last_watered = timestamptz

    Check manually for each, if they don't fit into those
    Skip the row
    """

    logger.info("Dataframe successfully normalised!")

    return new_dataframe


def dataframe_to_csv(file_path: str = 'data/normalised_output.csv') -> None:
    """Create new normalised csv file."""
    return None


if __name__ == "__main__":
    set_logger()
    clean_dataframe()
