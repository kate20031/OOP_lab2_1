"""
This module performs bus data analysis
by calculating the count of vehicles
over the speed limit and the count of violations in vicinity.
"""
import pandas as pd

from BusTracker.config.constants import (
    BUS_OUT1_FILE,
    BUS_OUT2_FILE,
    STOPS_COORD_FILE,
    PUNCTUAL_BUSES_FILE1,
    PUNCTUAL_BUSES_FILE2,
)
from BusTracker.config.constants import MAX_SPEED, MAX_DISTANCE
from BusTracker.src.bus_data_calculations import (
    get_bus_data,
    get_data,
    count_vehicles_over_speed_limit,
    get_violation_coordinates,
    find_violations_places,
    # load_punctuality_accuracy,
    # check_punctuality_accuracy,
)

bus_json1 = get_bus_data(BUS_OUT1_FILE)
bus_json2 = get_bus_data(BUS_OUT2_FILE)
stops_json = get_data(STOPS_COORD_FILE)
bus_count_data1 = len(bus_json1.items())
bus_count_data2 = len(bus_json2.items())


def print_vehicles_over_speed_limit():
    """
    Prints the count of vehicles that are over the speed limit.
    """
    count1 = count_vehicles_over_speed_limit(bus_json1, MAX_SPEED)
    count2 = count_vehicles_over_speed_limit(bus_json2, MAX_SPEED)
    print(f"Vehicles over speed limit during non rush hours: {count1}")
    print(f"Vehicles over speed limit during rush hours: {count2}")


def print_violations_in_vicinity():
    """
    Prints the count of violations that
     occurred, using a specific distance.
    """
    violations1 = get_violation_coordinates(bus_json1, MAX_SPEED)
    count1 = len(
        find_violations_places(
            violations1,
            MAX_DISTANCE,
            bus_count_data1))
    print(f"Violations places in vicinity during non rush hours: {count1}")

    violations2 = get_violation_coordinates(bus_json2, MAX_SPEED)
    count2 = len(
        find_violations_places(
            violations2,
            MAX_DISTANCE,
            bus_count_data2))
    print(f"Violations places in vicinity during rush hours: {count2}")


def print_punctuality_accuracy():
    """
    Prints the count of buses that were punctual
    during rush hours and non-rush hours.
    """

    # load_punctuality_accuracy(bus_json1, stops_json, ACCURACY_FILE1)
    # check_punctuality_accuracy(ACCURACY_FILE1, PUNCTUAL_BUSES_FILE1)
    # load_punctuality_accuracy(bus_json2, stops_json, ACCURACY_FILE2)
    # check_punctuality_accuracy(ACCURACY_FILE2, PUNCTUAL_BUSES_FILE2)

    df1 = pd.read_csv(PUNCTUAL_BUSES_FILE1)
    df2 = pd.read_csv(PUNCTUAL_BUSES_FILE2)

    non_puct_rush_count = df1.groupby(
        ["Zespol", "Slupek", "Lines"]).size().shape[0]
    non_puct_nrush_count = df2.groupby(
        ["Zespol", "Slupek", "Lines"]).size().shape[0]

    print(
        f"Number of non punctual buses during non rush hours: {non_puct_nrush_count}")
    print(
        f"Number of non punctual buses during rush hours: {non_puct_rush_count}")
