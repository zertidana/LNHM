# pylint: skip-file

"""Tests the functionality of the transform pipeline."""

import pytest
from pytest import mark
from unittest.mock import patch, mock_open
from transform import load_data, clean_dataframe
import pandas as pd


def test_transform_load_data_type_invalid():
    """Checks for an invalid type of file_path in load_data."""
    with pytest.raises(TypeError) as exc:
        load_data(23)
    assert str(exc.value) == 'Invalid URL type.'


def test_transform_load_data_type_not_csv():
    """Checks if the file_path ends with a .csv."""
    with pytest.raises(ValueError) as exc:
        load_data("data/normalised_output")
    assert str(exc.value) == 'Please end your filename in .csv.'


@patch('transform.load_data')
def test_transform_clean_dataframe_valid(test_load_data):
    """Tests data to make sure it is validated"""

    test_load_data_value = pd.DataFrame([{"plant_id": 33, "temperature": 16.909027178208355, "soil_moisture": 95.62121144519884,
                                        "last_watered": "2025-06-03T13:15:17.000Z", "recording_taken": "2025-06-03T14:30:31.531Z"}])
    test_load_data.return_value = test_load_data_value
    cleaned_dataframe = clean_dataframe('fake_file_path')

    # Check for correct column names
    expected_columns = ["recording_taken", "plant_id", "temperature",
                        "soil_moisture", "last_watered"]
    assert list(cleaned_dataframe.columns) == expected_columns

    # Check for no null values
    assert not cleaned_dataframe.isnull().values.any()
