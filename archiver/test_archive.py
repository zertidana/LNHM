# pylint: skip-file

"""Testing extract pipeline."""

import pytest
from pytest import mark
from unittest.mock import patch, mock_open
from archive_plant_reading import dataframe_daily_summary
from dotenv import load_dotenv
import pandas as pd
import datetime


load_dotenv()


def test_daily_summary_valid():
    """Tests daily summary function with correctly formatted columns.
    Covers errors, multiple plant readings, and most recent date formatting."""
    example_dataframe = pd.DataFrame({
        'temperature': [14.2348248, 18.24294824, 24.43248374234, 33.242424, 28.3323],
        'soil_moisture': [98.42424, 97.324325325, 96.324324324324, 99.242424, 99.55],
        'recording_taken': ['2025-06-05 14:33:09.103000+00:00', '2025-06-05 14:23:09.103000+00:00',
                            '2025-06-05 16:17:09.103000+00:00', '2025-06-05 14:44:09.103000+00:00',
                            '2025-06-02 14:44:09.103000+00:00'],
        'last_watered': ['2025-06-05 14:33:09.103000+00:00', '2025-06-05 14:23:09.103000+00:00',
                         '2025-06-05 16:17:09.103000+00:00', '2025-06-05 14:44:09.103000+00:00',
                         '2025-06-01 14:44:09.103000+00:00'],
        'error_msg': [None, None, None, 'high temperature error', None],
        'plant_id': [1, 1, 3, 4, 1]
    })
    date_value = datetime.datetime.strptime('2025-06-05', "%Y-%m-%d").date()

    expected_output = pd.DataFrame({
        'plant_id': [1, 3],
        'avg_temperature': [20.270024, 24.432484],
        'avg_soil_moisture': [98.432855, 96.324324],
        'recording_count': [3, 1],
        'last_watered': ['2025-06-05 14:33:09.103000+00:00', '2025-06-05 16:17:09.103000+00:00'],
        'date': ['2025-06-05', '2025-06-05']
    })

    summarised_data = dataframe_daily_summary(example_dataframe, date_value)

    print(type(expected_output))

    # more options can be specified also
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(summarised_data)
        print(expected_output)

    assert pd.testing.assert_frame_equal(
        summarised_data, expected_output) == None


def test_daily_summary_all_errors():
    """Tests daily summary function with all rows being errors. Test should return an empty dataframe."""
    example_dataframe = pd.DataFrame({
        'temperature': [14.2348248, 18.24294824, 24.43248374234, 33.242424, 28.3323],
        'soil_moisture': [98.42424, 97.324325325, 96.324324324324, 99.242424, 99.55],
        'recording_taken': ['2025-06-05 14:33:09.103000+00:00', '2025-06-05 14:23:09.103000+00:00',
                            '2025-06-05 16:17:09.103000+00:00', '2025-06-05 14:44:09.103000+00:00',
                            '2025-06-02 14:44:09.103000+00:00'],
        'last_watered': ['2025-06-05 14:33:09.103000+00:00', '2025-06-05 14:23:09.103000+00:00',
                         '2025-06-05 16:17:09.103000+00:00', '2025-06-05 14:44:09.103000+00:00',
                         '2025-06-01 14:44:09.103000+00:00'],
        'error_msg': ['error', 'error', 'error', 'high temperature error', 'error'],
        'plant_id': [1, 1, 3, 4, 1]
    })
    date_value = datetime.datetime.strptime('2025-06-05', "%Y-%m-%d").date()
    summarised_data = dataframe_daily_summary(example_dataframe, date_value)

    assert summarised_data.empty
