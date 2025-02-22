"""
Module Docstring: test_bus_data_calculations

This module contains includes tests for
 functions for calculating bus data,
such as speed calculation, violation coordinates extraction,
and results saving.
"""
import os
import unittest
from unittest.mock import patch, MagicMock

import pandas as pd

from BusTracker.src.bus_data_calculations import (
    calculate_speed,
    get_violation_coordinates,
    save_results,
)
from BusTracker.utils import conect_to_api


class TestYourModule(unittest.TestCase):
    """Test cases for functions in the bus_data_calculations module."""

    def setUp(self):
        """Set up any necessary data or configuration for your tests."""
        self.test_output_file = "test_output.csv"
        self.test_results_df = pd.DataFrame(
            {"Column1": [1, 2, 3], "Column2": ["A", "B", "C"]}
        )

    def tearDown(self):
        """Clean up any resources or data created during the tests."""
        if os.path.exists(self.test_output_file):
            os.remove(self.test_output_file)

    def test_calculate_speed(self):
        """Test the calculate_speed function."""
        vehicle = [
            {"Time": "2022-01-01 12:00:00", "Lat": 0, "Lon": 0},
            {"Time": "2022-01-01 12:01:00", "Lat": 0.008994, "Lon": 0},
        ]

        speed = calculate_speed(vehicle, 1)
        self.assertEqual(round(speed), 60.0)

    def test_get_violation_coordinates(self):
        """Test the get_violation_coordinates function."""
        json_data = {
            "vehicle1": [
                {"Time": "2022-01-01 12:00:00", "Lat": 0, "Lon": 0},
                {"Time": "2022-01-01 12:01:00", "Lat": 0.008994, "Lon": 0},
            ],
            "vehicle2": [
                {"Time": "2022-01-01 12:00:00", "Lat": 0, "Lon": 0},
                {"Time": "2022-01-01 12:01:00", "Lat": 0, "Lon": 0.001},
            ],
        }

        violations_coordinates = get_violation_coordinates(
            json_data, max_speed=50.0)
        expected_coordinates = [(0.008994, 0, None)]
        self.assertEqual(violations_coordinates, expected_coordinates)

    def test_save_results(self):
        """Test the save_results function."""
        save_results(self.test_results_df, self.test_output_file)

        self.assertTrue(os.path.exists(self.test_output_file))
        saved_df = pd.read_csv(self.test_output_file)
        pd.testing.assert_frame_equal(self.test_results_df, saved_df)

    @patch("utils.requests.get")
    def test_conect_to_api(self, mock_get):
        """Test the conect_to_api function."""
        query_params = {"your": "query", "parameters": "here"}
        mock_records = [{"field1": "value1", "field2": "value2"}]
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": mock_records}
        mock_get.return_value = mock_response
        records = conect_to_api(query_params)

        mock_get.assert_called_once_with(
            "https://api.um.warszawa.pl/api/action/dbtimetable_get/",
            params=query_params,
            timeout=5,
        )

        self.assertEqual(records, mock_records)


if __name__ == "__main__":
    unittest.main()
