"""
This module contains functions that are used to analyze,
including calculating speed, determining maximum speed,
finding violation coordinates,
formatting data, counting vehicles that are over speed limit
 and finding violations places.
"""
import csv
from itertools import groupby
from datetime import datetime
import pandas as pd

from BusTracker.data_loaders.bus_data_loader import load_data, load_timetable_data
from BusTracker.utils import convert_to_dict, haversine_distance
from BusTracker.config.constants import (
    SPEED_CONVERSION,
    DATE_FORMAT,
    CSV_DELIMITER,
    TIME_FORMAT,
    MAX_TIME_DIFF,
    MIN_TIME_DIFF,
)
from BusTracker.config.constants import EARLY_HOURS, LATE_HOURS, BUS_COUNT_THRESHOLD
from BusTracker.config.constants import BUS_OUT2_FILE, BUS_OUT1_FILE, CSV_ENCODING


def calculate_speed(vehicle, index):
    """
    Returns the calculated speed from coordinates.
    """

    time_diff = (
        datetime.strptime(vehicle[index]["Time"], DATE_FORMAT)
        - datetime.strptime(vehicle[index - 1]["Time"], DATE_FORMAT)
    ).total_seconds()

    lat1, lon1 = vehicle[index - 1]["Lat"], vehicle[index - 1]["Lon"]
    lat2, lon2 = vehicle[index]["Lat"], vehicle[index]["Lon"]
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    speed = distance / time_diff * SPEED_CONVERSION if time_diff > 0 else 0

    return speed


def calculate_max_speed(vehicle):
    """
    Returns the maximum speed for the vehicle.
    """

    max_speed = 0

    for i in range(1, len(vehicle)):
        speed = calculate_speed(vehicle, i)
        if speed > max_speed:
            max_speed = speed
    return max_speed


def get_violation_coordinates(json_data, max_speed):
    """
    Returns list of the coordinates of
     violations that exceed max speed.
    """

    violations_coordinates = []

    for _, vehicle in json_data.items():
        for i in range(1, len(vehicle)):
            speed = calculate_speed(vehicle, i)

            if speed > max_speed:
                lat = vehicle[i].get("Lat")
                lon = vehicle[i].get("Lon")
                vehicle_number = vehicle[i].get("VehicleNumber")
                violations_coordinates.append((lat, lon, vehicle_number))

    return violations_coordinates


def get_bus_data(file_path):
    """
    Parse and format the data in the file.
    Returns the grouped json data.
    """

    json_data = []

    with open(file_path, newline="", encoding=CSV_ENCODING) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=CSV_DELIMITER)

        next(csv_reader, None)
        for row in csv_reader:
            data_str = row[0]
            data_dict = convert_to_dict(data_str)
            time_str = data_dict["Time"]
            try:
                d = datetime.strptime(time_str, DATE_FORMAT)
            except ValueError:
                continue

            early_run = d.hour in EARLY_HOURS and d.day == 18
            rush_hours_run = d.hour in LATE_HOURS and d.day == 18

            if file_path == BUS_OUT1_FILE and early_run:
                json_data.append(data_dict)
            elif file_path == BUS_OUT2_FILE and rush_hours_run:
                json_data.append(data_dict)

    sorted_json_data = sorted(
        json_data, key=lambda x: (
            x["VehicleNumber"], x["Time"]))
    grouped_json_data = {
        key: list(group)
        for key, group in groupby(sorted_json_data, key=lambda x: x["VehicleNumber"])
    }

    return grouped_json_data


def get_data(file_path):
    """
    Reads a CSV file and converts it into a list of dictionaries.
    """

    json_data = []

    with open(file_path, newline="", encoding=CSV_ENCODING) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=CSV_DELIMITER)

        next(csv_reader, None)
        for row in csv_reader:
            data_str = row[0]
            data_dict = convert_to_dict(data_str)
            json_data.append(data_dict)

    return json_data


def count_vehicles_over_speed_limit(json_data, max_allowed_speed):
    """
    Count and return the number of vehicles
     that exceed the allowed maximum speed.
    """

    max_speeds = []

    for _, vehicle in json_data.items():
        max_sp = calculate_max_speed(vehicle)
        max_speeds.append(max_sp)

    count_grater_than_50 = sum(
        1 for speed in max_speeds if speed > max_allowed_speed)
    return count_grater_than_50


def find_violations_places(coordinates, max_dist, bus_count):
    """
    Find and return the list of violations
    that occurred within a specific distance.
    """

    violations_places = []
    result = []

    for value in coordinates:
        found = False
        for cluster in violations_places:
            for point in cluster:
                if (
                    haversine_distance(point[0], point[1], value[0], value[1])
                    <= max_dist
                ):
                    cluster.append(value)
                    found = True
                    break
        if not found:
            violations_places.append([value])

    for cluster in violations_places:
        if len(cluster) > bus_count * BUS_COUNT_THRESHOLD:
            result.append(cluster)

    return result


def find_stop(lat, lon, stops_data):
    """
    This function takes in latitude, longitude, and stop data.
    It then finds and returns the stop matching the input coordinates.
    """

    stop_lon, stop_lat, zespol, slupek = None, None, None, None
    for stop in stops_data:
        for item in stop["values"]:
            if item["key"] == "szer_geo":
                stop_lat = float(item.get("value"))
            elif item["key"] == "dlug_geo":
                stop_lon = float(item.get("value"))
            elif item["key"] == "zespol":
                zespol = item.get("value")
            elif item["key"] == "slupek":
                slupek = item.get("value")
        distance = haversine_distance(lat, lon, stop_lat, stop_lon)

        if distance <= 1:
            return zespol, slupek

    return None, None


def load_vehicle_accuracy(vehicle_json, stops_data, new_json_data):
    """
    This function loads vehicle accuracy data by finding
    stops for specific coordinates
    and updating new_json_data with these findings.
    """

    for i in range(1, len(vehicle_json)):
        lat = vehicle_json[i].get("Lat")
        lon = vehicle_json[i].get("Lon")

        zespol, slupek = find_stop(lat, lon, stops_data)

        if zespol is not None:
            vehicle_json[i]["Zespol"] = zespol
            vehicle_json[i]["Slupek"] = slupek
            new_json_data.append(vehicle_json[i])


def load_punctuality_accuracy(bus_data, stops_data, bus_data_output):
    """
    This function loads punctuality accuracy data.
    It creates a new data frame with
    the vehicle accuracy data calculated for all vehicles in bus_data
    and writes it to a CSV file.
    """
    new_json_data = []

    for _, vehicle in bus_data.items():
        load_vehicle_accuracy(vehicle, stops_data, new_json_data)
    df = pd.json_normalize(new_json_data)

    df.to_csv(bus_data_output, index=False)
    return new_json_data


def filter_timetable_times(timetable_data, real_time):
    """
    This function filters the timetable times
     based on the real_time value.
    """

    timetable_times = [
        datetime.strptime(
            "00" + entry["values"][5]["value"][2:]
            if entry["values"][5]["value"].startswith("24")
            else entry["values"][5]["value"],
            TIME_FORMAT,
        ).time()
        for entry in timetable_data
    ]

    filtered_timetable_times = [
        time_entry
        for time_entry in timetable_times
        if abs(real_time.hour - time_entry.hour) <= 1
    ]

    return filtered_timetable_times


def calculate_time_diff(timetable_time, real_time):
    """
    This function calculates and returns the
     absolute time difference between
    the timetable time and real time.
    """

    time_entry = datetime.combine(datetime.min, timetable_time)
    real_time_time = real_time.to_pydatetime().time()
    time_entry = time_entry.time()

    return abs(
        (
            datetime.combine(datetime.min, time_entry)
            - datetime.combine(datetime.min, real_time_time)
        ).total_seconds()
    )


def save_results(results_df, output_file):
    """
    This function saves the resulting DataFrame
    'results_df' into the 'output_file' CSV file.
    """

    results_df.to_csv(output_file, index=False)


def check_punctuality_accuracy(accuracy_csv, punctual_buses_csv):
    """
    This function checks the punctuality accuracy,
     does necessary processing and updates the CSV file.
    """

    prev_slupek, prev_lines = None, None

    results_df = pd.DataFrame(
        columns=["Zespol", "Slupek", "Lines", "RealTime", "TimeTable"]
    )

    df = load_data(accuracy_csv)
    df.sort_values(by=["Zespol", "Lines", "Slupek"], inplace=True)

    for _, row in df.iloc[1:].iterrows():
        zespol, slupek, lines = row["Zespol"], row["Slupek"], row["Lines"]
        real_time = row["Time"]
        if slupek < 10:
            slupek = "0" + str(slupek)

        if slupek != prev_slupek or lines != prev_lines:
            timetable_data = load_timetable_data(zespol, slupek, lines)

        if len(timetable_data) > 0:
            timetable_times = filter_timetable_times(timetable_data, real_time)

            for timetable_time in timetable_times:
                time_diff = calculate_time_diff(timetable_time, real_time)

                if MIN_TIME_DIFF < time_diff < MAX_TIME_DIFF:
                    results_df = results_df.append(
                        {
                            "Zespol": zespol,
                            "Slupek": slupek,
                            "Lines": lines,
                            "RealTime": real_time,
                            "TimeTable": timetable_time,
                        },
                        ignore_index=True,
                    )

        prev_slupek = slupek
        prev_lines = lines

    save_results(results_df, punctual_buses_csv)
