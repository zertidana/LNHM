"""Streamlit page for historical data."""
# pylint: disable=redefined-outer-name, import-error, no-member
import sys
import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

from visualisations.visualisations_archived_data import (get_moisture_boxplot,
                                                         get_moisture_levels_line_graph_archived,
                                                         get_temperature_line_chart,
                                                         identify_outliers
                                                         )


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
    local_df = pd.read_csv(
        "streamlit/data/plant_ids_names.csv", na_values=["NULL"])

    s3_df = load_historical_data()

    print(local_df[['plant_id', 'plant_name']])

    print("local_df columns:", local_df.columns.tolist())
    print("s3_df columns:", s3_df.columns.tolist())

    df = pd.merge(local_df, s3_df, on="plant_id", how="left")

    print(df)

    st.title("📈 Historical Data Analysis")

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
    plant_names = df["plant_name"].unique()
    select_all = st.checkbox("Select All Plants", value=True)

    selected = st.multiselect(
        "Select specific plant(s)", plant_names, default=plant_names)

    filtered_df = df[df["plant_name"].isin(selected)]

    if selected:
        line_chart = get_temperature_line_chart(df, selected)
        st.altair_chart(line_chart, use_container_width=True)
    else:
        st.warning("No plants selected.")

    st.subheader("💦 Daily Average Moisture by Plant (Line Graph)")
    plant_names = df["plant_name"].unique()
    selected_plant = st.selectbox("Select Plant Name", plant_names)
    moisture_line_graph = get_moisture_levels_line_graph_archived(
        df, selected_plant)
    st.altair_chart(moisture_line_graph, use_container_width=True)

    st.subheader("Daily Moisture Distribution by Plant")
    plant_names = df["plant_name"].unique()
    select_all = st.checkbox("Select all plants", value=True)

    if select_all:
        selected_plants = plant_names
    else:
        selected_plants = st.multiselect(
            "Select Plant(s)", plant_names, default=[])

    filtered_df = df[df["plant_name"].isin(selected_plants)]
    # Only show the plot if there's data selected
    if not filtered_df.empty:
        moisture_boxplot = get_moisture_boxplot(filtered_df)
        st.altair_chart(moisture_boxplot, use_container_width=True)
    else:
        st.warning("No plants selected.")

    st.subheader("🗓️ Data Overview")
    st.dataframe(df)
