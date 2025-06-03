# pylint: skip-file
# pylint: disable=unused-variable
"""Testing extract pipeline."""

import pytest
from pytest import mark
from unittest.mock import patch, mock_open
from extract import fetch_data, save_to_csv


def test_api_check():
    """Check for api."""
    assert fetch_data(4)
