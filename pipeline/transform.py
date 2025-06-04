"""Standardisation and normalisation of the plant data in csv before loading to DB."""

import datetime

import pandas as pd
import numpy as np

from utilities import get_logger, set_logger, load_csv_data


def clean_dataframe(file_path: str = 'data/output.csv') -> pd.DataFrame:
    """Filters selected columns from the initial dataframe
    that we need for the FACT update every minute."""
    logger = get_logger()
    logger.info("Loading data from file path...")
    try:
        input_dataframe = load_csv_data(file_path)
    except Exception as exc:
        logger.info("Data did not successfully load.")
        raise exc
    logger.info("Data successfully loaded!")

    logger.info("Extracting and normalising data columns..")

    new_dataframe = input_dataframe[['temperature', 'soil_moisture',
                                    'recording_taken', 'last_watered',
                                     'plant_id']].copy()
    new_dataframe = new_dataframe.dropna()  # skip rows if ANY values are null

    # On numeric columns convert all chars that aren't numbers to null and then remove them
    new_dataframe = new_dataframe[pd.to_numeric(
        new_dataframe['plant_id'], errors='coerce').notnull()]
    new_dataframe = new_dataframe[pd.to_numeric(
        new_dataframe['temperature'], errors='coerce').notnull()]
    new_dataframe = new_dataframe[pd.to_numeric(
        new_dataframe['soil_moisture'], errors='coerce').notnull()]

    # Checking for minus values
    numeric_cols = new_dataframe.select_dtypes(include='number')
    mask = (numeric_cols >= 0).all(axis=1)
    new_dataframe = new_dataframe[mask]

    # Column type conversion
    new_dataframe['recording_taken'] = pd.to_datetime(
        new_dataframe["recording_taken"])
    new_dataframe['last_watered'] = pd.to_datetime(
        new_dataframe["last_watered"])

    logger.info("Dataframe successfully filtered/converted!")
    return new_dataframe


def save_dataframe_to_csv(output_dataframe: pd.DataFrame,
                          file_path_minute: str = 'data/normalised_minute_output.csv',
                          file_path_day: str = 'data/normalised_day_output.csv') -> None:
    """Save current minute dataframe to:
    1. A new normalised csv file representing the minute. This is used directly by transform.py.
    2. A csv file representing the whole day. This is used later by long-term data to summarise the day."""
    logger = get_logger()

    for file_path in [file_path_minute, file_path_day]:
        if not isinstance(file_path, str):
            raise TypeError("Please use a string for your filename.")
        if file_path[-4:] != ".csv":
            raise ValueError("Please end your filename in .csv.")

    # For file_path_minute, overwrite existing file
    logger.info("Saving cleaned plant data at %s to %s...",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), file_path_minute)
    output_dataframe.to_csv(file_path_minute, index=False)
    logger.info("Successfully wrote data to %s!", file_path)


if __name__ == "__main__":
    set_logger()
    save_dataframe_to_csv(clean_dataframe())
