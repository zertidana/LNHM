"""Streamlit Dashboard."""
from os import environ as ENV
import pandas as pd
from dotenv import load_dotenv
import pyodbc
import streamlit as st

from visualisations.visualisations import (get_average_moisture_level_per_plant_bar_chart,
                                           get_average_temperature_per_plant_bar_chart,
                                           get_moisture_levels_line_graph,
                                           get_temperature_line_graph,
                                           show_plant_info,
                                           get_average_temperature_per_city_bar_chart,
                                           get_moisture_level_per_botanist_bar_chart,
                                           get_avg_temp_area_chart)

# pylint: disable=no-member, invalid-name, too-many-arguments, c-extension-no-member
load_dotenv()

st.set_page_config(
    page_title="Plant Analytics",
    page_icon="🌿",
    layout="wide"
)

# st.markdown("""
#     <style>
#     @font-face {
#         font-family: 'Thicker';
#         src: url('path_to_your_font/Thicker-Regular.woff2') format('woff2'),
#              url('path_to_your_font/Thicker-Regular.ttf') format('truetype');
#         font-weight: normal;
#         font-style: normal;
#     }

#     html, body, [class*="css"], .stApp, .stTextInput, .stButton, .stMarkdown, .stSidebar,
#     .css-18ni7ap, .css-1d391kg, .css-1v0mbdj, .css-1kyxreq {
#         font-family: 'Thicker', sans-serif !important;
#     }
#     </style>
#     """, unsafe_allow_html=True)


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
    """Loads data from DB."""
    query = """
    SELECT plant_name, botanist_name, temperature, soil_moisture, recording_taken, city, country_name
    FROM FACT_plant_reading
    LEFT JOIN DIM_plant 
    ON FACT_plant_reading.plant_id = DIM_plant.plant_id
    LEFT JOIN DIM_botanist 
    ON DIM_plant.botanist_id = DIM_botanist.botanist_id
    LEFT JOIN DIM_origin_location 
    ON DIM_plant.location_id = DIM_origin_location.location_id
    LEFT JOIN DIM_country
    ON DIM_country.country_id = DIM_origin_location.country_id;


    """
    return pd.read_sql(query, _connection)


if __name__ == "__main__":

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
    image_url = df.loc[df["plant_name"] == plant_name, "regular_url"].values[0]
    st.image(image_url, width=100)
    show_plant_info(df, plant_name)

    st.subheader("🌡️ Plant Temperature Recordings")
    line_graph = get_temperature_line_graph(df, plant_name)
    st.altair_chart(line_graph, use_container_width=True)

    bar_chart_2 = get_average_temperature_per_plant_bar_chart(df)
    st.altair_chart(bar_chart_2, use_container_width=True)

    table = get_avg_temp_area_chart(df)
    st.altair_chart(table, use_container_width=True)

    st.subheader("🪴 Moisture Levels Over Recordings")
    line_graph_2 = get_moisture_levels_line_graph(df, plant_name)
    st.altair_chart(line_graph_2, use_container_width=True)

    bar_chart = get_average_moisture_level_per_plant_bar_chart(df)
    st.altair_chart(bar_chart, use_container_width=True)

    st.subheader("🌍 City-Wise Overview")
    temp_by_city = get_average_temperature_per_city_bar_chart(df)
    st.altair_chart(temp_by_city, use_container_width=True)

    st.subheader("🧑‍🔬 Botanist Performance")
    per_botanist = get_moisture_level_per_botanist_bar_chart(df)
    st.altair_chart(per_botanist, use_container_width=True)
