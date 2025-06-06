"""Historical Data Visualisations for Streamlit dashboard."""

import altair as alt
import pandas as pd
import streamlit as st


@st.cache_data(ttl=3)
def get_temperature_line_chart(df, selected_plants=None):
    """Line chart of daily average temperature per plant."""

    df["date"] = pd.to_datetime(df["date"]).dt.date

    if selected_plants:
        df = df[df["plant_id"].isin(selected_plants)]

    grouped = (
        df.groupby(["plant_id", "date"])["avg_temperature"]
        .mean()
        .reset_index()
    )

    temp_chart = alt.Chart(grouped).mark_line().encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("avg_temperature:Q", title="Avg Temp (°C)"),
        color=alt.Color("plant_id:N", title="Plant ID"),
        tooltip=["plant_id", "date", "avg_temperature"]
    ).properties(
        title="🌡️ Daily Average Temperature per Plant",
        width=800,
        height=400
    )

    return temp_chart


def identify_outliers(df, temp_threshold=2.0, moisture_threshold=2.0):
    """Finds all the outliers depending on the z-score."""
    df_copy = df.copy()
    df_copy["temp_zscore"] = (df_copy["avg_temperature"] -
                              df_copy["avg_temperature"].mean()) / df_copy["avg_temperature"].std()
    df_copy["moisture_zscore"] = (df_copy["avg_soil_moisture"] -
                                  df_copy["avg_soil_moisture"].mean()) / df_copy["avg_soil_moisture"].std()

    outliers = df_copy[(df_copy["temp_zscore"].abs() > temp_threshold) |
                       (df_copy["moisture_zscore"].abs() > moisture_threshold)]
    return outliers[["plant_id", "date", "avg_temperature", "avg_soil_moisture",
                     "temp_zscore", "moisture_zscore"]]


@st.cache_data(ttl=3)
def get_moisture_levels_line_graph_archived(df, plant_id):
    """Line graph that shows the moisture level of a specific plant."""
    plant_df = df[df["plant_id"] == plant_id]
    chart = alt.Chart(plant_df).mark_line().encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("avg_soil_moisture:Q", title="Average Soil Moisture ( % )"),
        color=alt.value("lime"),
        tooltip=["date:T", "avg_soil_moisture:Q"]
    ).properties(title=f"Plant {plant_id}'s Soil Moisture Over Time", width=700)
    return chart


@st.cache_data(ttl=3)
def get_moisture_boxplot(df):
    """Creates a box plot of average soil moisture per plant."""
    moisture_boxplot = alt.Chart(df).mark_boxplot(extent='min-max').encode(
        x=alt.X("plant_id:N", title="Plant ID"),
        y=alt.Y("avg_soil_moisture:Q", title="Avg Soil Moisture (%)"),
        tooltip=["plant_id:N", "avg_soil_moisture:Q"]
    ).properties(
        width=700,
        height=400
    )
    return moisture_boxplot
