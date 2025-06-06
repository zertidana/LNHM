"""Streamlit page for historical data."""
# pylint: disable=redefined-outer-name, import-error, no-member
import os
from dotenv import load_dotenv
import pandas as pd

from visualisations import (get_temperature_line_chart, get_moisture_levels_line_graph_archived,
                            identify_outliers, get_moisture_boxplot
                            )
import streamlit as st
import boto3


st.set_page_config(page_title="Historical Data", page_icon="🗂️", layout="wide")


@st.cache_data(ttl=10)
def load_historical_data():
    """Loads historical data from S3."""

    latest_csv = "historical_data_dummy.csv"

    load_dotenv()
    s3_path = os.getenv("S3_PATH") + latest_csv

    if not s3_path:
        st.error("S3_PATH not set in .env file.")
        return pd.DataFrame()

    try:
        df = pd.read_csv(s3_path, storage_options={
            "key": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret": os.getenv("AWS_SECRET_ACCESS_KEY")
        })
        # st.write("✅ Successfully connected to S3 and loaded data.")
        return df
    except Exception as e:
        st.error(f"Error loading data from S3: {e}")
        return pd.DataFrame()


if __name__ == "__main__":

    st.title("📈 Historical Data Analysis")
    df = load_historical_data()

    st.subheader("🚨 Plants Needing Attention")

    temp_thresh = st.slider(
        "Z-score threshold for temperature outliers", 1.0, 4.0, 2.0)
    moisture_thresh = st.slider(
        "Z-score threshold for moisture outliers", 1.0, 4.0, 2.0)
    outlier_df = identify_outliers(df, temp_thresh, moisture_thresh)

    st.markdown(
        "These are plants whose average temperature or moisture are statistical outliers.")
    st.dataframe(outlier_df.style.format({
        "avg_temperature": "{:.2f}",
        "avg_soil_moisture": "{:.2f}",
        "temp_zscore": "{:.2f}",
        "moisture_zscore": "{:.2f}",
    }))

    st.subheader("🌡️ Daily Average Temperature by Plant (Line Chart)")
    plant_ids = sorted(df["plant_id"].unique())
    select_all = st.checkbox("Select All Plants", value=True)
    if select_all:
        selected = plant_ids
    else:
        selected = st.multiselect(
            "Select specific plant(s)", plant_ids, default=[])

    filtered_df = df[df["plant_id"].isin(selected)]

    if not filtered_df.empty:
        line_chart = get_temperature_line_chart(df, selected)
        st.altair_chart(line_chart, use_container_width=True)
    else:
        st.warning("No plants selected.")

    st.subheader("💦 Daily Average Moisture by Plant (Line Graph)")
    plant_ids = df["plant_id"].unique()
    selected_plant = st.selectbox("Select Plant Name", sorted(plant_ids))
    moisture_line_graph = get_moisture_levels_line_graph_archived(
        df, selected_plant)
    st.altair_chart(moisture_line_graph, use_container_width=True)

    st.subheader("Daily Moisture Distribution by Plant")
    plant_ids = sorted(df["plant_id"].unique())
    select_all = st.checkbox("Select all plants", value=True)

    if select_all:
        selected_plants = plant_ids
    else:
        selected_plants = st.multiselect(
            "Select Plant(s)", plant_ids, default=[])

    filtered_df = df[df["plant_id"].isin(selected_plants)]
    # Only show the plot if there's data selected
    if not filtered_df.empty:
        moisture_boxplot = get_moisture_boxplot(filtered_df)
        st.altair_chart(moisture_boxplot, use_container_width=True)
    else:
        st.warning("No plants selected.")

    st.subheader("🗓️ Data Overview")
    st.dataframe(df)
