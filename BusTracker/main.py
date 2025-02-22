"""
This module runs the bus analytics process,
including loading data and performing the data analysis.
"""

from src.bus_analytics import (
    print_vehicles_over_speed_limit,
    print_violations_in_vicinity,
    print_punctuality_accuracy,
)

from data_loaders.bus_data_loader import (
    load_bus_tracking_data,
    load_bus_stations_coord,
)


def load_data():
    """
    Calls functions to load bus tracking data and bus stations coordinates.
    """
    load_bus_tracking_data()
    load_bus_stations_coord()


def analyse_data():
    """
    Calls functions to print vehicles over
     speed limit and violations in vicinity.
    """
    print_vehicles_over_speed_limit()
    print_violations_in_vicinity()
    print_punctuality_accuracy()


def main():
    """
    Main function.
    """
    # Data initiation
    # load_data()

    # Data analysis
    analyse_data()


if __name__ == "__main__":
    main()
