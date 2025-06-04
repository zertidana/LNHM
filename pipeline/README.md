# 🚰 ETL Pipeline

## 📁 Files

`extract.py` - Connects to the base url, collates all plants and saves this data as a CSV file.
Functions:
save_to_csv -> creates csv file of all plant data.


`transform.py` - Standardization and normalization of the plant data in csv before loading to DB.
Functions:
load_data -> loads data from csv into pandas dataframe.
clean_dataframe -> ensures correct dataframe is being used, with consistent naming conventions and eliminating null values.
save_dataframe_to_csv -> Creates new csv of the normalised data.


`load.py` - Loads all of the clean data to the database.  


`analyse.ipynb` - Further extraction of the data to further the understanding of data.

## Instructions

