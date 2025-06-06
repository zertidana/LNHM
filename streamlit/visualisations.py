"""Visualisations of Real-Time Live Data for Streamlit."""


import altair as alt
import pandas as pd
import streamlit as st

# pylint: disable=no-member, line-too-long


def show_plant_info(df, plant_name):
    """Shows the plant information."""
    plant_df = df[df["plant_name"] == plant_name]

    if plant_df.empty:
        st.warning("No data available for this plant...")
        return

    avg_temp = plant_df["temperature"].mean()
    avg_moisture = plant_df["soil_moisture"].mean()
    last_updated = plant_df["recording_taken"].max()

    st.markdown(f"""
    ### 🌱 Plant Information
    - **Plant Name:** `{plant_name}`
    - **Average Temperature:** `{avg_temp:.2f} °C`
    - **Average Soil Moisture:** `{avg_moisture:.2f}%`
    - **Last Updated:** `{last_updated.strftime('%Y-%m-%d %H:%M:%S')}`
    """)


@st.cache_data(ttl=3)
def get_temperature_line_graph(df, plant_name):
    """Line graph that shows the temperature of a specific plant."""
    plant_df = df[df["plant_name"] == plant_name]
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
        df.groupby("plant_name")["temperature"]
        .mean()
        .reset_index()
        .rename(columns={'temperature': 'avg_temp'})
        .sort_values(by="avg_temp", ascending=False)
        .head(top_n)
    )

    chart = alt.Chart(avg_temperatures).mark_bar().encode(
        y=alt.Y("plant_name:N", title="Plant Name", sort="-x"),
        x=alt.X("avg_temp:Q", title="Average Temperature(°C)"),
        color=alt.Color('avg_temp:Q', scale=alt.Scale(scheme='greens')),
        tooltip=["plant_name:N", "avg_temp:Q"]
    ).properties(title=f"Top {top_n} Plants by Average Temperature", width=700)

    return chart


@st.cache_data(ttl=3)
def get_moisture_levels_line_graph(df, plant_name):
    """Line graph that shows the moisture level of a specific plant."""
    plant_df = df[df["plant_name"] == plant_name]
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
        df.groupby("plant_name")["soil_moisture"]
        .mean()
        .reset_index()
        .rename(columns={'soil_moisture': 'avg_moisture'})
        .sort_values(by="avg_moisture", ascending=False)
        .head(top_n)
    )

    chart = alt.Chart(avg_moistures).mark_bar().encode(
        y=alt.Y("plant_name:N", title="Plant Name", sort="-x"),
        x=alt.X("avg_moisture:Q", title="Average Soil Moisture (%)"),
        color=alt.Color('avg_moisture:Q', scale=alt.Scale(scheme='greens')),
        tooltip=["plant_name:N", "avg_moisture:Q"]
    ).properties(title=f"Top {top_n} Plants by Average Soil Moisture", width=700)

    return chart


def get_average_temperature_per_city_bar_chart(df, top_n=5):
    """Bar chart showing average temperature by city, colored by country."""
    avg_temp_city = (
        df.groupby(["city", "country_name"])["temperature"]
        .mean()
        .reset_index()
        .rename(columns={"temperature": "avg_temp"})
        .sort_values(by="avg_temp", ascending=False)
        .head(top_n)
    )

    chart = alt.Chart(avg_temp_city).mark_bar().encode(
        y=alt.Y("city:N", title="City", sort="-x"),
        x=alt.X("avg_temp:Q", title="Average Temperature (°C)"),
        color=alt.Color("country_name:N", title="Country",
                        scale=alt.Scale(scheme='greens')),
        tooltip=["city:N", "country_name:N", "avg_temp:Q"]
    ).properties(title=f"Top {top_n} Cities by Average Temperature", width=700)

    return chart


@st.cache_data(ttl=3)
def get_moisture_level_per_botanist_bar_chart(df, top_n=10):
    """Bar chart showing average soil moisture per botanist."""
    avg_moisture_botanist = (
        df.groupby("botanist_name")["soil_moisture"]
        .mean()
        .reset_index()
        .rename(columns={"soil_moisture": "avg_moisture"})
        .sort_values(by="avg_moisture", ascending=False)
        .head(top_n)
    )

    chart = alt.Chart(avg_moisture_botanist).mark_bar().encode(
        y=alt.Y("botanist_name:N", title="Botanist", sort="-x"),
        x=alt.X("avg_moisture:Q", title="Average Soil Moisture (%)"),
        color=alt.Color("avg_moisture:Q", scale=alt.Scale(scheme="greens")),
        tooltip=["botanist_name:N", "avg_moisture:Q"]
    ).properties(title=f"Top {top_n} Botanists by Avg Soil Moisture", width=700)

    return chart


def get_avg_temp_area_chart(df):
    """Area chart showing average temperature trend over time."""
    df_time = df.copy()
    df_time["recording_taken"] = pd.to_datetime(df_time["recording_taken"])
    trend = df_time.groupby("recording_taken")[
        "temperature"].mean().reset_index()

    chart = alt.Chart(trend).mark_area(opacity=0.5).encode(
        x=alt.X("recording_taken:T", title="Time"),
        y=alt.Y("temperature:Q", title="Average Temperature (°C)"),
        color=alt.value("lime"),
        tooltip=["recording_taken:T", "temperature:Q"]
    ).properties(title="Average Temperature Over Time", width=700)

    return chart
