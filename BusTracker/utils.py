import csv

import requests

from cmath import sin, cos, sqrt, asin
from math import radians

from BusTracker.config.constants import KM_TO_M_CONVERSION, EARTH_RADIUS


def process_data(response, output_file_path):
    data = response.json()
    records = data["result"]

    if records != "Błędna metoda lub parametry wywołania":
        with open(output_file_path, "a", newline="") as file:
            writer = csv.writer(file)
            for record in records:
                writer.writerow([record])


def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    distance = EARTH_RADIUS * c * KM_TO_M_CONVERSION

    return int(distance.real)


def convert_to_dict(str_dict):
    return eval(str_dict)

def conect_to_api(query_params):
    r = requests.get(
        "https://api.um.warszawa.pl/api/action/dbtimetable_get/",
        params=query_params,
        timeout=5,
    )

    data = r.json()
    records = data["result"]

    return records