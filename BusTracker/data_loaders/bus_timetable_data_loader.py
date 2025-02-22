"""
This module loads the bus timetable data.
"""

from BusTracker.config.constants import API_KEY
from BusTracker.utils import conect_to_api


def load_bus_timetable_data(bus_stop_id, bus_stop_nr, line):
    """
    Fetches data from an API and saves it into a csv file.
    """

    id_1 = "e923fa0e-d96c-43f9-ae6e-60518c9f3238"

    query_params = {
        "id": id_1,
        "apikey": API_KEY,
        "busstopId": bus_stop_id,
        "busstopNr": str(bus_stop_nr),
        "line": line,
    }

    return conect_to_api(query_params)
