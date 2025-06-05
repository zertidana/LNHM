"""Standardisation and normalisation of the plant data in csv before loading to DB."""

import datetime
import os
import pandas as pd

from utilities import get_logger, set_logger, load_csv_data


def clean_dataframe_from_csv(file_path: str = 'data/output.csv') -> pd.DataFrame:
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
    new_dataframe = clean_dataframe(input_dataframe)

    return new_dataframe


def clean_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Filters selected columns from the initial dataframe
    that we need for the FACT update every minute."""
    logger = get_logger()
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(
            f"Incorrect type for parameter 'dataframe' - type: {type(dataframe)}")

    new_dataframe = dataframe[['temperature', 'soil_moisture',
                               'recording_taken', 'last_watered',
                               'plant_id', 'error']].copy()

    print(new_dataframe)

    # If error is null then skip rows if ANY values apart from error are null
    error_mask = new_dataframe['error'].isna()
    other_cols_null_or_empty = new_dataframe[new_dataframe.columns.difference(['error'])].isna() | new_dataframe[new_dataframe.columns.difference(['error'])].applymap(
        lambda x: isinstance(x, str) and x.strip() == '')
    rows_to_drop = error_mask & other_cols_null_or_empty.any(axis=1)
    new_dataframe = new_dataframe[~rows_to_drop].copy()

    print(new_dataframe)

    # On numeric columns remove all rows that contain non-numeric data
    for col in ['plant_id', 'temperature', 'soil_moisture']:
        new_dataframe = new_dataframe[new_dataframe[col].isna() | pd.to_numeric(
            new_dataframe[col], errors='coerce').notna()]

    # Checking for minus values, if minus then update error value
    numeric_cols = new_dataframe.select_dtypes(include=['number']).columns
    negative_mask = (new_dataframe[numeric_cols] < 0).any(axis=1)
    new_dataframe.loc[negative_mask, 'error'] = 'negative value error'

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

    today = datetime.datetime.now()

    for file_path in [file_path_minute, file_path_day]:
        if not isinstance(file_path, str):
            raise TypeError("Please use a string for your filename.")
        if file_path[-4:] != ".csv":
            raise ValueError("Please end your filename in .csv.")

    # For file_path_minute, overwrite minute file
    logger.info("Saving cleaned plant data at %s to %s...",
                today.strftime("%Y-%m-%d %H:%M"), file_path_minute)
    output_dataframe.to_csv(file_path_minute, index=False)
    logger.info("Successfully wrote data to %s!", file_path_minute)
    if os.path.exists(file_path_day):
        day_data = load_csv_data(file_path_day)[
            'recording_taken'].head(1).to_string(index=False)
        day_data_date = datetime.datetime.fromisoformat(day_data)
        if not day_data_date.date() == today.date():
            logger.info("The date has changed. Calling summarise function.")
            summarise_day_from_csv(day_data_date)
            output_dataframe.to_csv(file_path_day, index=False)
    else:
        logger.info("Also adding cleaned plant data on %s to %s...",
                    today.strftime("%Y-%m-%d %H:%M:%S"), file_path_day)
        output_dataframe.to_csv(
            file_path_day, header=False, index=False, mode='a')
        logger.info("Successfully wrote data to %s!", file_path_day)


def summarise_day_from_csv(day_data_date: datetime, file_path_day: str = 'data/normalised_day_output.csv',
                           output_path_historical: str = 'data/historical_data.csv') -> None:
    """Summarise the day's averages for each unique plant_id,
    and save as historical data."""
    logger = get_logger()
    day_data = load_csv_data(file_path_day)
    summarised_day_data = dataframe_daily_summary(day_data, day_data_date)

    # Check if file exists and add headers if not
    if os.path.exists(output_path_historical):
        data_header = False
    else:
        data_header = True
    summarised_day_data.to_csv(
        output_path_historical, header=data_header, index=False, mode='a')
    logger.info("Successfully saved historical data to %s.",
                output_path_historical)


def dataframe_daily_summary(df: pd.DataFrame, date: datetime):
    """Returns a daily summary of plant health data for a given day."""
    logger = get_logger()
    summarised_day_data = df.groupby('plant_id').agg({
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


if __name__ == "__main__":
    set_logger()
    save_dataframe_to_csv(clean_dataframe_from_csv())
