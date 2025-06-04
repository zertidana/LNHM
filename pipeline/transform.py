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
        raise exc
    logger.info("Data successfully loaded!")

    logger.info("Extracting and normalising data columns..")
    new_dataframe = input_dataframe[['recording_taken', 'plant_id',
                                    'temperature', 'soil_moisture',
                                     'last_watered']].copy()
    new_dataframe = new_dataframe.dropna()  # skip rows if ANY values are null

    # On numeric columns convert all chars that aren't numbers to null and then remove them
    new_dataframe = new_dataframe[pd.to_numeric(
        new_dataframe['plant_id'], errors='coerce').notnull()]
    new_dataframe = new_dataframe[pd.to_numeric(
        new_dataframe['temperature'], errors='coerce').notnull()]
    new_dataframe = new_dataframe[pd.to_numeric(
        new_dataframe['soil_moisture'], errors='coerce').notnull()]

    """GET RID OF MINUS VALUES"""

    # Column type conversion
    new_dataframe['recording_taken'] = pd.to_datetime(
        new_dataframe["recording_taken"])
    new_dataframe['last_watered'] = pd.to_datetime(
        new_dataframe["last_watered"])

    logger.info("Dataframe successfully filtered/converted!")
    return new_dataframe


def save_dataframe_to_csv(output_dataframe: pd.DataFrame,
                          file_path: str = 'data/normalised_output.csv') -> None:
    """Create new normalised csv file."""
    logger = get_logger()

    if not isinstance(file_path, str):
        raise TypeError("Please use a string for your filename.")
    if file_path[-4:] != ".csv":
        raise ValueError("Please end your filename in .csv.")

    logger.info("Saving normalised plant data to %s...", file_path)

    output_dataframe.to_csv(file_path, index=False)

    logger.info("Successfully wrote data to %s!", file_path)


if __name__ == "__main__":
    set_logger()
    save_dataframe_to_csv(clean_dataframe())
