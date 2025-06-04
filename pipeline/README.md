# 🚰 ETL Pipeline

## 📁 File Structure

`extract.py` 
- Connects to the plant endpoints of the API
- Collates all plant data together
- Saves the plant data as a CSV file.

`transform.py` 
- Standardises and normalises the extracted data into a new .csv file.

`load.py` 
- Loads all of the cleaned data to the Microsoft SQL server database using a batch engine function.  

`analyse.ipynb` 
- Further extraction of the data to further the understanding of data.

