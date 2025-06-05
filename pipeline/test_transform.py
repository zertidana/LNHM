# pylint: skip-file

"""Tests the functionality of the transform pipeline."""

import pytest
from pytest import mark
from unittest.mock import patch, mock_open
from transform import clean_dataframe_from_csv, save_dataframe_to_csv, summarise_day_from_csv
import pandas as pd


@patch('transform.load_csv_data')
def test_transform_clean_dataframe_valid(test_load_data):
    """Tests data to make sure it is validated"""

    test_load_data_value = pd.DataFrame([{"temperature": 16.909027178208355, "soil_moisture": 95.62121144519884,
                                        "recording_taken": "2025-06-03T14:30:31.531Z",
                                          "last_watered": "2025-06-03T13:15:17.000Z",
                                          "error": None, "plant_id": 33}])
    test_load_data.return_value = test_load_data_value
    cleaned_dataframe = clean_dataframe_from_csv('fake_file_path')

    # Check for correct column names
    expected_columns = ['temperature', 'soil_moisture', 'recording_taken', 'last_watered',
                        'error_msg', 'plant_id']
    assert list(cleaned_dataframe.columns) == expected_columns

    cleaned_dataframe = cleaned_dataframe.drop(columns=['error_msg'])

    # Check for no null values in every column except error_msg
    assert not cleaned_dataframe.isnull().values.any()
