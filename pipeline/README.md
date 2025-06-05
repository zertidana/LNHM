# 🚰 ETL Pipeline

This directory contains the scripts used to extract, transform, and load plant health data into a Microsoft SQL Server database.

## 📁 File Structure

- `extract.py`  
  Connects to the API's plant endpoints, collects data from all plants, and saves it as a raw CSV file.

- `transform.py`  
  Standardises and normalises the extracted data, then outputs a new cleaned CSV file.

- `load.py`  
  Loads the cleaned data into the Microsoft SQL Server database using a batch loading function.

- `analyse.ipynb`  
  A Jupyter notebook for exploratory data analysis to further understand the dataset.

## 🧪 How to Run
Ensure you are in a virtual environment, you can do that by running the bash command:
```bash
bash set_up_venv.sh
```

Then run the ETL steps in order:
`python3 extract.py`  
`python3 transform.py`  
`python3 load.py`  
