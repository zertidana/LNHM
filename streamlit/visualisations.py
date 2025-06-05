"""Altair graphs used to model the data."""

import altair as alt
import pandas as pd
import streamlit as st

# pylint: disable=no-member


def show_plant_info(df, plant_name):
    plant_df = df[df["plant_name"] == plant_name]

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
    plant_df = df[df["plant_name"] == plant_name]
    chart = alt.Chart(plant_df).mark_line().encode(
        x="recording_taken:T",
        y="temperature:Q",
        tooltip=["recording_taken:T", "temperature:Q"]
    ).properties(title=f"Temperature Over Time - {plant_name}", width=700)
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
        x=alt.X("avg_temp:Q", title="Average Temperature"),
        tooltip=["plant_name:N", "avg_temp:Q"]
    ).properties(title=f"Top {top_n} Plants by Average Temperature", width=700)

    return chart


@st.cache_data(ttl=3)
def get_moisture_levels_line_graph(df, plant_name):
    """Line graph that shows the moisture level of a specific plant."""
    plant_df = df[df["plant_name"] == plant_name]
    chart = alt.Chart(plant_df).mark_line().encode(
        x="recording_taken:T",
        y="soil_moisture:Q",
        tooltip=["recording_taken:T", "soil_moisture:Q"]
    ).properties(title=f"Soil Moisture Over Time - {plant_name}", width=700)
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
        y=alt.Y("plant_name:N", title="Plant ID", sort="-x"),
        x=alt.X("avg_moisture:Q", title="Average Soil Moisture"),
        tooltip=["plant_name:N", "avg_moisture:Q"]
    ).properties(title=f"Top {top_n} Plants by Average Soil Moisture", width=700)

    return chart


# This to be implemented when working with the historical data
@st.cache_data(ttl=3)
def get_temperature_per_hour_heatmap(df):
    """Heatmap of temperature in a day."""
    df['recording_taken'] = pd.to_datetime(
        df['recording_taken'], errors='coerce')
    df['hour'] = df['recording_taken'].dt.hour

    df['weekday'] = df['recording_taken'].dt.day_name()

    heatmap_data = df.groupby(
        ['weekday', 'hour']).size().reset_index(name='temperature')

    weekday_order = ['Monday', 'Tuesday', 'Wednesday',
                     'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data['weekday'] = pd.Categorical(
        heatmap_data['weekday'], categories=weekday_order, ordered=True)

    heatmap = alt.Chart(heatmap_data).mark_rect().encode(
        x=alt.X('hour:O', title='Hour of Day'),
        y=alt.Y('weekday:O', title='Day of Week'),
        color=alt.Color('temperature:Q', scale=alt.Scale(scheme='blues')),
        tooltip=['weekday', 'hour', 'temperature']
    )
    return heatmap
