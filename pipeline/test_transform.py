# pylint: skip-file

"""Tests the functionality of the transform pipeline."""

import pytest
from pytest import mark
from unittest.mock import patch, mock_open
from transform import load_data, clean_dataframe


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
    pass
    """
    test_load_data_value = #dataframe goes here
    test_load_data.return_value = test_load_data_value
    cleaned_dataframe = clean_dataframe('fake_file_path')
    
    check column for right names
    check to see if there are no null values
    """
