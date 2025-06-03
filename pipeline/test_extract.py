# pylint: skip-file

"""Testing extract pipeline."""

import pytest
from pytest import mark
from unittest.mock import patch, mock_open
from extract import fetch_data, save_to_csv, get_all_plants
from dotenv import load_dotenv

load_dotenv()


def test_api_check_valid():
    """Check for valid api call."""
    """
    

    
    """
    assert fetch_data(4)
    assert fetch_data(9)
    assert fetch_data(13)


def test_api_check_invalid():
    """Check for plant outside of range."""
    assert fetch_data(57)
    assert fetch_data(61)
    assert fetch_data(82)


def test_get_all_plants_raises_type_error():
    """Check for raises type error"""
    with pytest.raises(TypeError):
        assert get_all_plants(890)


def test_get_all_plants_not_empty():
    assert len(get_all_plants(url)) > 0


def test_save_to_csv():
    with pytest.raises(TypeError):
        save_to_csv(12984)


""""
get_all_plants

a bunch of error data
checking to stop after 5 





"""
