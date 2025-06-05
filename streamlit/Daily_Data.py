"""Streamlit Dashboard."""
from os import environ as ENV
import pandas as pd
from dotenv import load_dotenv
import pyodbc
import streamlit as st

from visualisations import (get_average_moisture_level_per_plant_bar_chart,
                            get_average_temperature_per_plant_bar_chart,
                            get_moisture_levels_line_graph,
                            get_temperature_line_graph,
                            show_plant_info)

# pylint: disable=no-member

st.set_page_config(
    page_title="Plant Analytics",
    page_icon="🌿",
    layout="wide"
)


@st.cache_resource
def get_connection(driver, host, port, database, username, password):
    """Create and cache a SQL Server connection using pyodbc."""
    conn_str = (
        f"DRIVER={driver};"
        f"SERVER={host},{port};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)


@st.cache_data
def load_data(_connection):
    query = """
    SELECT plant_name, botanist_name, temperature, soil_moisture, recording_taken, city
    FROM FACT_plant_reading
    LEFT JOIN DIM_plant 
    ON FACT_plant_reading.plant_id = DIM_plant.plant_id
    LEFT JOIN DIM_botanist 
    ON DIM_plant.botanist_id = DIM_botanist.botanist_id
    LEFT JOIN DIM_origin_location 
    ON DIM_plant.location_id = DIM_origin_location.location_id;


    """
    return pd.read_sql(query, _connection)


@st.cache_data
def get_alerts(df) -> pd.DataFrame:
    pass


if __name__ == "__main__":
    load_dotenv()

    conn = get_connection(ENV['DB_DRIVER'],
                          ENV['DB_HOST'],
                          ENV['DB_PORT'],
                          ENV['DB_NAME'],
                          ENV['DB_USER'],
                          ENV['DB_PASSWORD'])

    df = load_data(conn)

    st.title("🌿 Plant Sensor Insights 🌿")

    st.subheader("🔍 Filters")
    plant_name = st.selectbox("Plant name", df["plant_name"].unique())
    df["recording_taken"] = pd.to_datetime(
        df["recording_taken"], format='ISO8601')

    show_plant_info(df, plant_name)

    st.subheader("🌡️ Plant Temperature Recordings")
    line_graph = get_temperature_line_graph(df, plant_name)
    st.altair_chart(line_graph, use_container_width=True)

    bar_chart_2 = get_average_temperature_per_plant_bar_chart(df)
    st.altair_chart(bar_chart_2, use_container_width=True)

    st.subheader("🪴 Moisture Levels Over Recordings")
    line_graph_2 = get_moisture_levels_line_graph(df, plant_name)
    st.altair_chart(line_graph_2, use_container_width=True)

    bar_chart = get_average_moisture_level_per_plant_bar_chart(df)
    st.altair_chart(bar_chart, use_container_width=True)
