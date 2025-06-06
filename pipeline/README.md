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

- `etl_controller.py`
  Runs all three stages of the ETL pipeline (extract, transform, load) in succession.

## 🧪 How to Run
Ensure you are in a virtual environment, you can do that by running the bash command:
```bash
bash set_up_venv.sh
```

If you would like CSV files, then run the ETL steps in order:
`python3 extract.py`  
`python3 transform.py`  
`python3 load.py`  

If you would like to run the full ETL pipeline without CSV, run:
`python3 etl_controller.py`

## ETL Container

To build the terraform container and push it to an ECR repository for use as a Lambda, run:

1. `docker build --platform linux/amd64 --provenance=false -t [your-container-name] .`
2. `docker tag [your-container-name]:latest [your-ecr-repo-id]`
3. `docker push [your-ecr-repo-id]:latest`                           
