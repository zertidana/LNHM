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
    """Filters selected columns from the initial dataframe
    that we need for the FACT update every minute."""
    logger = get_logger()
    logger.info("Loading data from file path...")
    try:
        input_dataframe = load_data(file_path)
    except Exception as exc:
        logger.info("Data did not successfully load.")
    logger.info("Data successfully loaded!")

    logger.info("Checking data columns..")

    new_dataframe = input_dataframe[['recording_taken', 'plant_id',
                                    'temperature', 'soil_moisture',
                                     'last_watered']].copy()
    new_dataframe = new_dataframe.dropna()

    logger.info("Dataframe successfully filtered!")

    return new_dataframe


def dataframe_to_csv(file_path: str = 'data/normalised_output.csv') -> None:
    """Create new normalised csv file."""
    return None


if __name__ == "__main__":
    set_logger()
    print(clean_dataframe())
