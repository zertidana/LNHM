"""Altair graphs used to model the data."""

import altair as alt
import pandas as pd
import streamlit as st

# pylint: disable=no-member, line-too-long

##################### Real-Time Data Graphs #####################


def show_plant_info(df, plant_name):
    """Shows the plant information."""
    plant_df = df[df["plant_id"] == plant_name]

    if plant_df.empty:
        st.warning("No data available for this plant...")
        return

    avg_temp = plant_df["temperature"].mean()
    avg_moisture = plant_df["soil_moisture"].mean()
    last_updated = plant_df["recording_taken"].max()

    st.markdown(f"""
    ### 🌱 Plant Information
    - **Plant ID:** `{plant_name}`
    - **Avg Temperature:** `{avg_temp:.2f} °C`
    - **Avg Soil Moisture:** `{avg_moisture:.2f}%`
    - **Last Updated:** `{last_updated.strftime('%Y-%m-%d %H:%M:%S')}`
    """)


@st.cache_data(ttl=3)
def get_temperature_line_graph(df, plant_name):
    """Line graph that shows the temperature of a specific plant."""
    plant_df = df[df["plant_id"] == plant_name]
    chart = alt.Chart(plant_df).mark_line().encode(
        x=alt.X("recording_taken:T", title="Recording Taken"),
        y=alt.Y("temperature:Q", title="Temperature (°C)"),
        color=alt.value("lime"),
        tooltip=["recording_taken:T", "temperature:Q"]
    ).properties(title=f"{plant_name}'s Temperature Over Time", width=700)
    return chart


@st.cache_data(ttl=3)
def get_average_temperature_per_plant_bar_chart(df, top_n=5):
    """Bar chart that shows the top N plants by average temp."""
    avg_temperatures = (
        df.groupby("plant_id")["temperature"]
        .mean()
        .reset_index()
        .rename(columns={'temperature': 'avg_temp'})
        .sort_values(by="avg_temp", ascending=False)
        .head(top_n)
    )

    chart = alt.Chart(avg_temperatures).mark_bar().encode(
        y=alt.Y("plant_id:N", title="Plant ID", sort="-x"),
        x=alt.X("avg_temp:Q", title="Average Temperature(°C)"),
        color=alt.Color('avg_temp:Q', scale=alt.Scale(scheme='greens')),
        tooltip=["plant_id:N", "avg_temp:Q"]
    ).properties(title=f"Top {top_n} Plants by Average Temperature", width=700)

    return chart


@st.cache_data(ttl=3)
def get_moisture_levels_line_graph(df, plant_name):
    """Line graph that shows the moisture level of a specific plant."""
    plant_df = df[df["plant_id"] == plant_name]
    chart = alt.Chart(plant_df).mark_line().encode(
        x=alt.X("recording_taken:T", title="Recording Taken"),
        y=alt.Y("soil_moisture:Q", title="Soil Moisture (%)"),
        color=alt.value("lime"),
        tooltip=["recording_taken:T", "soil_moisture:Q"]
    ).properties(title=f"{plant_name}'s Soil Moisture Over Time", width=700)
    return chart


@st.cache_data(ttl=3)
def get_average_moisture_level_per_plant_bar_chart(df, top_n=5):
    """Bar chart that shows the top N plants by average moisture."""
    avg_moistures = (
        df.groupby("plant_id")["soil_moisture"]
        .mean()
        .reset_index()
        .rename(columns={'soil_moisture': 'avg_moisture'})
        .sort_values(by="avg_moisture", ascending=False)
        .head(top_n)
    )

    chart = alt.Chart(avg_moistures).mark_bar().encode(
        y=alt.Y("plant_id:N", title="Plant ID", sort="-x"),
        x=alt.X("avg_moisture:Q", title="Average Soil Moisture (%)"),
        color=alt.Color('avg_moisture:Q', scale=alt.Scale(scheme='greens')),
        tooltip=["plant_id:N", "avg_moisture:Q"]
    ).properties(title=f"Top {top_n} Plants by Average Soil Moisture", width=700)

    return chart

##################### Historical Data Graphs #####################


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
        y=alt.Y("avg_temperature:Q", title="Avg Temperature (°C)"),
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
def get_moisture_levels_line_graph_archived(df, plant_name):
    """Line graph that shows the moisture level of a specific plant."""
    plant_df = df[df["plant_id"] == plant_name]
    chart = alt.Chart(plant_df).mark_line().encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("avg_soil_moisture:Q", title="Average Soil Moisture ( % )"),
        color=alt.value("lime"),
        tooltip=["date:T", "avg_soil_moisture:Q"]
    ).properties(title=f"Plant {plant_name}'s Soil Moisture Over Time", width=700)
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
