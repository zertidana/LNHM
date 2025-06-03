"""An extract script for the plant health monitoring ETL pipeline."""
import os
from os import environ as ENV
import json
import csv
import logging
from dotenv import load_dotenv
import requests


def fetch_data(url, plant_id: int) -> json:
    """Connects to the api and returns the data as json"""
    logger.info("Connecting to API...")
    url = url + str(plant_id)
    response = requests.get(url)
    data = response.json()
    if data.get('error'):
        print(data['error'])
    if not response:
        logger.warning("Plant has no data.")
        raise ValueError(f"Plant {plant_id} has no data.")

    return data


def get_all_plants(url):
    """Collects all the plants per minute."""

    """
    if plant not found in the response
    we raise error
    
    """
    logger.info("Collating plants...")
    pass


def save_to_csv(data, filename="data/output.csv"):
    """Saves data to a local output csv file."""
    pass


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel("INFO")
    load_dotenv()

    url = ENV["BASE_URL"]
    json_data = fetch_data(url, 43)
    print(json_data)
