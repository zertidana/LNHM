# pylint: skip-file

"""Testing extract pipeline."""

import pytest
from pytest import mark
from unittest.mock import patch, mock_open
from extract import PlantAPIClient, save_to_csv
from dotenv import load_dotenv
import requests
import requests_mock
import json

load_dotenv()


"""
get_request: gets request from URL
"""


def test_get_request_invalid_type():
    """Checks for an invalid type in get_request."""
    client = PlantAPIClient("http://testapi.com/")
    with pytest.raises(TypeError) as exc:
        client.get_request(23)
    assert str(exc.value) == 'Invalid URL type.'


def test_get_request_valid_type(requests_mock):
    """Checks for an valid type in get_request."""
    client = PlantAPIClient("http://testapi.com/")
    requests_mock.get(client.base_url, json={'plant_id': '233'})
    assert type(client.get_request(client.base_url)) == dict


"""
fetch data - connects to API using get_request,
and converts the data as json and returns according to plant id
url, plant_id
"""


@pytest.fixture
def plant_33():
    return {
        "plant_id": 33,
        "name": "Schefflera Arboricola",
        "temperature": 16.909027178208355,
        "origin_location": {
            "latitude": -58.3733,
            "longitude": 6.5244,
            "city": "Cutler Bay",
            "country": "Mexico"
        },
        "botanist": {
            "name": "Marty Lang",
            "email": "marty.lang@lnhm.co.uk",
            "phone": "1-539-229-4058"
        },
        "last_watered": "2025-06-03T13:15:17.000Z",
        "soil_moisture": 95.62121144519884,
        "recording_taken": "2025-06-03T14:30:31.531Z",
        "images": {
            "license": 451,
            "license_name": "CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
            "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "original_url": "https://perenual.com/storage/image/upgrade_access.jpg",
            "regular_url": "https://perenual.com/storage/image/upgrade_access.jpg",
            "medium_url": "https://perenual.com/storage/image/upgrade_access.jpg",
            "small_url": "https://perenual.com/storage/image/upgrade_access.jpg",
            "thumbnail": "https://perenual.com/storage/image/upgrade_access.jpg"
        },
        "scientific_name": [
            "Schefflera arboricola"
        ]
    }


@pytest.fixture
def plant_not_found():
    return {
        "plant_id": 33,
        "error": "plant not found",
    }


def test_fetch_data_invalid_type_url():
    """Checks if url in fetch_data is a valid type."""
    client = PlantAPIClient(23)
    with pytest.raises(TypeError) as exc:
        client.fetch_data(1)
    assert str(exc.value) == 'Invalid URL type.'


def test_fetch_data_invalid_type_plant_id():
    """Checks if plant_id in fetch_data is a valid type."""
    client = PlantAPIClient("http://testapi.com/")
    with pytest.raises(TypeError) as exc:
        client.fetch_data("Crazy")
    assert str(exc.value) == 'Invalid plant_id type.'


@patch('extract.PlantAPIClient.get_request')
def test_fetch_data_valid(fake_plant_request, plant_33):
    """Test fetch_data returns correct data type and content"""
    client = PlantAPIClient("http://testapi.com/")
    fake_plant_request.return_value = plant_33

    result = client.fetch_data(1)

    assert isinstance(result, dict)
    assert result == plant_33


"""
get_all_plants - loops over fetch_data and changes function based on response,
terminates when 5 in a row return ‘not found’
"""


def test_get_all_plants_invalid_type_url():
    """Check if URL is raised if wrong type."""
    client = PlantAPIClient(5)
    with pytest.raises(TypeError) as exc:
        client.get_all_plants()
    assert str(exc.value) == 'Please use a valid url.'


def test_get_all_plants_invalid_type_not_found_limit():
    """Check if not_found_limit is raised if wrong type."""
    client = PlantAPIClient("http://testapi.com/", "imnotvalid")
    with pytest.raises(TypeError) as exc:
        client.get_all_plants()
    assert str(exc.value) == 'Please use a valid int value.'


@patch('extract.PlantAPIClient.get_request')
def test_get_all_plants_terminates_after_5_loops(fake_get_request, plant_not_found):
    """Test if get_all_plants terminates immediately
    after 5 responses with 'error: plant not found'
    list it returns should also be empty?"""
    client = PlantAPIClient("http://testapi.com/")
    fake_get_request.return_value = plant_not_found
    returned_value = client.get_all_plants()
    assert len(returned_value) == 0
    assert type(returned_value) == list
    assert fake_get_request.call_count == 5


"""

save_to_csv - takes a list of dictionaries and saves to a csv file

"""


def test_save_to_csv_invalid_type_plants_list():
    """Tests for invalid type of plants_list."""
    with pytest.raises(TypeError) as exc:
        save_to_csv(12984)
    assert str(exc.value) == "Please use a list of dictionaries."


def test_save_to_csv_invalid_type_filename():
    """Tests for invalid type of filename."""
    with pytest.raises(TypeError) as exc:
        save_to_csv([{"example": "yep"}], 23)
    assert str(exc.value) == "Please use a string for your filename."


def test_save_to_csv_invalid_format_filename_or_empty():
    """Tests for invalid type of filename, or if it doesn't contain .csv."""
    with pytest.raises(ValueError) as exc:
        save_to_csv([{"example": "yep"}], "cool")
    assert str(exc.value) == "Please end your filename in .csv."
