# 🏛️ Liverpool Natural History Museum (LNMH) 🏛️
The Liverpool Natural History Museum is expanding with a new botanical wing that highlights the diversity and ecological importance of plant life. To ensure long-term plant health, this project implements a cloud-based data pipeline and dashboard to monitor environmental conditions, alert staff to anomalies, and enable data-driven decisions via interactive visualisations.

## 🚰 ETL Pipeline
The ETL pipeline ingests sensor data, transforms it into structured records, and loads it into a cloud-hosted Microsoft SQL Server database for storage and analysis. The pipeline runs on a containerised infrastructure using Docker and Terraform.

## 📈 Visualisation
The data is visualised using Streamlit, a lightweight web app framework chosen for its cost effectiveness and customisation capabilities. Developers can adapt the dashboards to stakeholder needs, offering flexibility in how insights are displayed.

## 📍 Folder Navigation
- `documentation/`: ERD, architecture diagram, dashboard wireframe, and user stories.
- `pipeline/`: ETL scripts and related tests.
- `bash_scripts/`: Shell scripts for running the pipeline and initializing the database.
- `terraform/`: Infrastructure-as-code files, including Docker configuration for the ETL pipeline.


## 🤐 Environment Variable Structure
The following are the variables required in the .env file:
- `BASE_URL`=http://your-sensor-api.com/data
- `DB_DRIVER`=ODBC Driver 17 for SQL Server
- `DB_HOST`=your-database-hostname  
- `DB_PORT`=1433  
- `DB_USER`=your_db_username
- `DB_PASSWORD`=your_db_password
- `DB_NAME`=plant_monitoring_db
- `DB_SCHEMA`=your_schema_name
