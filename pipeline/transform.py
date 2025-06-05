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
                               'error', 'plant_id']].copy()

    new_dataframe.rename(columns={
        'error': 'error_msg',
    }, inplace=True)

    # If error is null then skip rows if ANY values apart from error are null
    error_mask = new_dataframe['error_msg'].isna()
    other_cols_null_or_empty = new_dataframe[new_dataframe.columns.difference(['error_msg'])].isna() | new_dataframe[new_dataframe.columns.difference(['error'])].map(
        lambda x: isinstance(x, str) and x.strip() == '')
    rows_to_drop = error_mask & other_cols_null_or_empty.any(axis=1)
    new_dataframe = new_dataframe[~rows_to_drop].copy()

    # On numeric columns remove all rows that contain non-numeric data
    for col in ['plant_id', 'temperature', 'soil_moisture']:
        new_dataframe = new_dataframe[new_dataframe[col].isna() | pd.to_numeric(
            new_dataframe[col], errors='coerce').notna()]

    # If soil_moisture < 30, then update error value for alerts
    new_dataframe.loc[new_dataframe['soil_moisture']
                      < 30, 'error_msg'] = 'low soil moisture error'

    # If temperature > 30C & temperature < 10C then update error value for alerts
    new_dataframe.loc[new_dataframe['temperature']
                      <= 10, 'error_msg'] = 'low temperature error'
    new_dataframe.loc[new_dataframe['temperature']
                      >= 30, 'error_msg'] = 'high temperature error'

    # Checking for minus values, if minus then update error value
    numeric_cols = new_dataframe.select_dtypes(include=['number']).columns
    negative_mask = (new_dataframe[numeric_cols] < 0).any(axis=1)
    new_dataframe.loc[negative_mask, 'error_msg'] = 'negative value error'

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

    # Check if the file exists and read the date.
    if os.path.exists(file_path_day):
        day_data = load_csv_data(file_path_day)[
            'recording_taken'].head(1).to_string(index=False)
        day_data = datetime.datetime.fromisoformat(day_data)
        # If it doesn't match, the day has changed
        if day_data.date() != today.date():
            logger.info("The date has changed. Calling summarise function.")
            summarise_day_from_csv(day_data)
            output_dataframe.to_csv(file_path_day, index=False)
        else:  # Else continue adding to the file
            logger.info("Also adding cleaned plant data on %s to %s...",
                        today.strftime("%Y-%m-%d %H:%M:%S"), file_path_day)
            output_dataframe.to_csv(
                file_path_day, header=False, index=False, mode='a')
    else:  # If the file doesn't exist, make it with headers and add
        logger.info("Also adding cleaned plant data on %s to %s...",
                    today.strftime("%Y-%m-%d %H:%M:%S"), file_path_day)
        output_dataframe.to_csv(
            file_path_day, index=False)
    logger.info("Successfully wrote data to %s!", file_path_day)


def summarise_day_from_csv(datetime_value: datetime, file_path_day: str = 'data/normalised_day_output.csv',
                           output_path_historical: str = 'data/historical_data.csv') -> None:
    """Summarise the day's averages for each unique plant_id,
    and save as historical data."""
    logger = get_logger()
    day_data = load_csv_data(file_path_day)
    summarised_day_data = dataframe_daily_summary(day_data, datetime_value)

    # Check if file exists and add headers if not
    if os.path.exists(output_path_historical):
        data_header = False
    else:
        data_header = True
    summarised_day_data.to_csv(
        output_path_historical, header=data_header, index=False, mode='a')
    logger.info("Successfully saved historical data to %s.",
                output_path_historical)


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


if __name__ == "__main__":
    set_logger()
    df = clean_dataframe_from_csv()
    # save_dataframe_to_csv(df)
    summarise_day_from_csv(datetime.date.today() - datetime.timedelta(days=1))
