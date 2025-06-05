# pylint: skip-file

"""Tests the functionality of the load script in the pipeline."""

import pytest
from pytest import mark
from unittest.mock import patch, mock_open
from transform import clean_dataframe, save_dataframe_to_csv, summarise_day
from utilities import load_csv_data
import pandas as pd

"""
How to test?

"""


def test_transform_load_data_type_invalid():
    """Checks for an invalid type of file_path in load_data."""
    with pytest.raises(TypeError) as exc:
        load_csv_data(23)
    assert str(exc.value) == 'Invalid URL type.'


def test_transform_load_data_type_not_csv():
    """Checks if the file_path ends with a .csv."""
    with pytest.raises(ValueError) as exc:
        load_csv_data("data/normalised_output")
    assert str(exc.value) == 'Please end your filename in .csv.'


def test_load_example_test():
    assert True
