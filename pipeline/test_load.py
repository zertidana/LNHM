# pylint: skip-file

"""Tests the functionality of the load script in the pipeline."""

import pytest
from pytest import mark
from unittest.mock import patch, mock_open
from transform import load_data, clean_dataframe
import pandas as pd

"""
How to test?

"""


def test_load_example_test():
    assert True
