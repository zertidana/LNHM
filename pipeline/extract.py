"""An extract script for the plant health monitoring ETL pipeline."""

from os import environ as ENV
import json
import csv
from dotenv import load_dotenv
import requests

from log import get_logger, set_logger


def get_request(base_url: str) -> dict:
    """Get request from a given URL string."""
    logger = get_logger()
    if not isinstance(base_url, str):
        logger.critical("Invalid URL type.")
        raise TypeError("Invalid URL type.")
    try:
        request = requests.get(base_url, timeout=10)
        return request.json()
    except requests.exceptions.Timeout as exc:
        logger.critical("Request timed out.")
        raise exc


def fetch_data(base_url: str, plant_id: int) -> dict:
    """Connects to the api and returns the data as json"""
    logger = get_logger()
    logger.info("Connecting to API...")

    if not isinstance(base_url, str):
        logger.critical("Invalid URL type.")
        raise TypeError("Invalid URL type.")
    if not isinstance(plant_id, int):
        logger.critical("Invalid plant_id type.")
        raise TypeError("Invalid plant_id type.")

    base_url = base_url + str(plant_id)
    data = get_request(base_url)
    logger.info("Received response for plant %s.", plant_id)
    return data


def get_all_plants(base_url: str, not_found_limit: int = 5) -> list[dict]:
    """Collects all the plant data and returns as a dataframe."""
    logger = get_logger()
    logger.info("Collating plants...")
    if not isinstance(base_url, str):
        logger.critical("URL is invalid. Aborting.")
        raise TypeError("Please use a valid url.")
    if not isinstance(not_found_limit, int):
        logger.critical("Not found limit is invalid. Aborting.")
        raise TypeError("Please use a valid int value.")

    list_of_plants = []

    plant_id = 1  # Start index from 1
    not_found_count = 0  # How many plants not found in a row
    while True:
        json_data = fetch_data(base_url, plant_id)
        if json_data.get('error'):
            error_msg = json_data['error']
            if error_msg == 'plant not found':
                not_found_count += 1
            else:  # other error (sensor malfunction)
                not_found_count = 0
            logger.warning(
                "Plant %s data returned an error message: %s", plant_id, error_msg)
        else:
            logger.info(
                "Plant %s data successfully saved.", plant_id)
            list_of_plants.append(json_data)
        if not_found_count >= not_found_limit:
            break
        plant_id += 1
    return list_of_plants


def save_to_csv(plants_list: list[dict], filename: str = "data/output.csv") -> None:
    """Saves data to a local output csv file."""
    logger = get_logger()

    if not isinstance(plants_list, list):
        raise TypeError("Please use a list of dictionaries.")
    if not isinstance(filename, str):
        raise TypeError("Please use a string for your filename.")
    if filename[-4:] != ".csv":
        raise ValueError("Please end your filename in .csv.")

    logger.info("Updating data keys.")
    all_keys = set()

    for plant in plants_list:
        all_keys.update(plant.keys())

    keys = sorted(all_keys)
    logger.info("Saving plant data to %s...", filename)

    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(plants_list)
    logger.info("Successfully wrote data to %s!", filename)


if __name__ == "__main__":
    set_logger()
    load_dotenv()

    url = ENV["BASE_URL"]
    plant_data = get_all_plants(url)
    save_to_csv(plant_data)
