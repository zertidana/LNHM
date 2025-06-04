# 🚰 ETL Pipeline

## 📁 File Structure

`extract.py` 
- Connects to the API contained at the base url
- Collates all plant data together
- Saves this data as a CSV file.

Functions:

- `get_request` -> Gets standard API request from base_url and saves as dictionary.
- `fetch_data` -> Connects to API and returns the data as a dict.
- `get_all_plants` -> Iterates through all plant API and returns the full thing as a list of dictionaries.
- `save_to_csv` -> Saves the list of dictionaries directly to a .csv file.

`transform.py` 
- Standardization and normalization of the plant data in .csv
- Resaves to normalised .csv

Functions:
- `load_data` -> Loads data from .csv into pandas dataframe.
- `clean_dataframe` -> Cleans dataframe, eliminates nulls, and checks type values.
- `save_dataframe_to_csv` -> Creates new .csv of the normalised data.

`load.py` - Loads all of the clean data to the database.  

Functions:
- `load_data` -> Loads data from .csv into pandas dataframe.
- `insert_transformed_data` -> Inserts data in minute .csv **directly** into Microsoft SQL server using batch engine function.

`analyse.ipynb` - Further extraction of the data to further the understanding of data.

## .env

