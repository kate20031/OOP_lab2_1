"""
This is a module for loading bus tracking
 data and bus stations' coordinates.
"""
import time
from datetime import datetime

import pandas as pd
import requests

from BusTracker.config.constants import (
    BUS_TRACKER_API_RESOURCE_ID,
    API_KEY,
    BUS_TRACKER_API_URL,
    BUS_OUT1_FILE,
    EARLY_HOURS,
    LATE_HOURS,
    BUS_OUT2_FILE,
    BUS_STATION_API_PARAMS,
    DATE_FORMAT,
)

from BusTracker.utils import process_data, conect_to_api


def load_bus_tracking_data():
    """
    Function to load bus tracking data.
    """
    current_time = datetime.now()
    start_time = time.time()

    while True:
        if time.time() - start_time > 3600:
            break

        query_params = {
            "resource_id": BUS_TRACKER_API_RESOURCE_ID,
            "type": 1,
            "apikey": API_KEY,
        }

        r = requests.get(BUS_TRACKER_API_URL, params=query_params, timeout=5)

        if current_time.hour in EARLY_HOURS:
            output_file_path = BUS_OUT1_FILE
        elif current_time.hour in LATE_HOURS:
            output_file_path = BUS_OUT2_FILE
        else:
            return
        process_data(r, output_file_path)

        time.sleep(60)


def load_bus_stations_coord():
    """
    Function to load bus stations' coordinates.
    """
    output_file_path = "bus_station_output.csv"
    r = requests.get(
        "https://api.um.warszawa.pl/api/action/dbstore_get/",
        params=BUS_STATION_API_PARAMS,
        timeout=5,
    )

    process_data(r, output_file_path)


def load_bus_timetable_data(busstop_id, busstop_nr, line):
    """
    Fetches data from an API and saves it into a csv file.
    """

    api_key = "44c76d0d-4ca7-456a-a694-3b4dd63dd2d5"

    query_params = {
        "id": "e923fa0e-d96c-43f9-ae6e-60518c9f3238",
        "apikey": api_key,
        "busstopId": busstop_id,
        "busstopNr": busstop_nr,
        "line": line,
    }

    return conect_to_api(query_params)


def load_data(file_path):
    """
    This function loads data from a file and returns
     a processed pandas DataFrame
    for further processing.
    """

    return pd.read_csv(
        file_path,
        parse_dates=["Time"],
        date_parser=lambda x: datetime.strptime(x, DATE_FORMAT),
    )


def load_timetable_data(zespol, slupek, lines):
    """
    This function loads timetable data using
     identifiers like 'zespol', 'slupek' and 'lines'.
    """

    return load_bus_timetable_data(zespol, slupek, lines)
