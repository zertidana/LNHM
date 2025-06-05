"""Streamlit page for historical data."""
# pylint: disable=redefined-outer-name, import-error, no-member

import pandas as pd

from visualisations import (get_temperature_heatmap,
                            identify_outliers
                            )
import streamlit as st

st.set_page_config(page_title="Historical Data", page_icon="🗂️", layout="wide")


@st.cache_data(ttl=10)
def load_historical_data():
    """Loads historical data."""
    df = pd.read_csv("data/historical_data_dummy.csv",
                     parse_dates=["last_watered", "date"])
    return df


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

    st.subheader("📊 Daily Average Temperature & Moisture by Plant (Heatmap)")
    heatmap = get_temperature_heatmap(df)
    st.altair_chart(heatmap, use_container_width=True)

    st.subheader("🗓️ Data Overview")
    st.dataframe(df)
