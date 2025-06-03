"""Standardization and normalization of the plant data in csv before loading to DB."""

import pandas as pd


def load_data(file_path='data/output.csv') -> pd.DataFrame:
    """Loads the unclean data from csv."""
    return pd.read_csv(file_path)


def cleaning(df) -> pd.DataFrame:
    df = df[
        'name': 'plant_name',
        'temperature': 'temperature',
        'soil_moisture': 'soil_moisture',
        'recording_taken': 'recording_taken',
        'last_watered': 'last_watered'
    ]
    df = df[['plant_name', 'temperature',
             'soil_moisture', 'recording_taken',
             'last_watered']]
