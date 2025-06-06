"""An extract script for the plant health monitoring ETL pipeline."""

from os import environ as ENV
import csv
from dotenv import load_dotenv
import requests

from utilities import get_logger, set_logger


class PlantAPIClient:
    """Client for retrieving plant health data from API."""

    def __init__(self, base_url: str, not_found_limit: int = 5):
        self.logger = get_logger()
        self._base_url = base_url
        self._not_found_limit = not_found_limit

    @property
    def base_url(self) -> str:
        """Returns the base url."""
        return self._base_url

    @base_url.setter
    def base_url(self, value: str):
        if not isinstance(value, str):
            raise TypeError("base_url must be a string.")
        self._base_url = value

    @property
    def not_found_limit(self) -> int:
        """Returns not found limit."""
        return self._not_found_limit

    @not_found_limit.setter
    def not_found_limit(self, value: int):
        if not isinstance(value, int):
            raise TypeError("not_found_limit must be an integer.")
        self._not_found_limit = value

    def get_request(self, base_url: str) -> dict:
        """Get request from a given URL string."""
        if not isinstance(base_url, str):
            self.logger.critical("Invalid URL type.")
            raise TypeError("Invalid URL type.")
        try:
            response = requests.get(base_url, timeout=10)
            return response.json()
        except requests.exceptions.Timeout as exc:
            self.logger.critical("Request timed out.")
            raise exc

    def fetch_data(self, plant_id: int) -> dict:
        """Connects to the api and returns the data as json."""
        self.logger.info("Connecting to API...")
        if not isinstance(self.base_url, str):
            self.logger.critical("Invalid URL type.")
            raise TypeError("Invalid URL type.")
        if not isinstance(plant_id, int):
            self.logger.critical("Invalid plant_id type.")
            raise TypeError("Invalid plant_id type.")

        plant_url = self.base_url + str(plant_id)
        data = self.get_request(plant_url)
        self.logger.info("Received response for plant %s.", plant_id)
        return data

    def get_all_plants(self) -> list[dict]:
        """Collects all the plant data and returns as a dataframe."""
        self.logger.info("Collating plants...")
        if not isinstance(self.base_url, str):
            self.logger.critical("URL is invalid. Aborting.")
            raise TypeError("Please use a valid url.")
        if not isinstance(self.not_found_limit, int):
            self.logger.critical("Not found limit is invalid. Aborting.")
            raise TypeError("Please use a valid int value.")

        list_of_plants = []

        plant_id = 1  # Start index from 1
        not_found_count = 0  # How many plants not found in a row
        while True:
            json_data = self.fetch_data(plant_id)
            if json_data.get('error'):
                error_msg = json_data['error']
                if error_msg == 'plant not found':
                    not_found_count += 1
                # other error than not found (e.g. sensor malfunction) Must record
                else:
                    if plant_id <= 50:  # duct tape fix
                        not_found_count = 0
                    list_of_plants.append(json_data)
                self.logger.warning(
                    "Plant %s data returned an error message: %s", plant_id, error_msg)
            else:
                self.logger.info(
                    "Plant %s data successfully saved.", plant_id)
                list_of_plants.append(json_data)
            if not_found_count >= self.not_found_limit:
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
    client = PlantAPIClient(url)
    plant_data = client.get_all_plants()
    save_to_csv(plant_data)
