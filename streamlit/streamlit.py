"""Streamlit Dashboard."""

import pandas as pd
from dotenv import load_dotenv
import streamlit as st

from visualisations import (get_average_moisture_level_per_plant_bar_chart,
                            get_average_temperature_per_plant_bar_chart,
                            get_moisture_levels_line_graph,
                            get_temperature_line_graph,
                            show_plant_info)

# pylint: disable=no-member


# Saving these for when we get the RDS details...

# @st.cache_resource
# def connect_to_database():
#     pass


# @st.cache_data
# def get_data() -> pd.Dataframe:
#     pass


# @st.cache_data
# def get_alerts(df) -> pd.DataFrame:
#     pass


if __name__ == "__main__":
    load_dotenv()

    FILE_NAME = "data/normalised_day_output.csv"
    df = pd.read_csv(FILE_NAME)

    # st.set_page_config(
    #     page_title="Plant Analytics",
    #     page_icon="🌿"
    # )
    st.title("🌿 Plant Sensor Insights 🌿")

    st.subheader("🔍 Filters")
    plant_name = st.selectbox("Plant name", df["plant_id"].unique())
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
