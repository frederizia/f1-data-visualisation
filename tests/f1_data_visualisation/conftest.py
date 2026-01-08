import fastf1
import numpy as np
import pandas as pd
import pytest


# FastF1 fake data


@pytest.fixture
def fastf1_race_result_for_winning_driver():
    # Simplified.
    return fastf1.core.DriverResult(
        {
            "Abbreviation": "VER",
            "FirstName": "Max",
            "LastName": "Verstappen",
            "FullName": "Max Verstappen",
            "TeamName": "Red Bull",
            "Position": np.float64(1),
            "GridPosition": np.float64(1),
            "Laps": np.float64(56),
            "Points": np.float64(25.0),
            "ClassifiedPosition": 1,
            "Time": pd.Timedelta(hours=1, minutes=30, seconds=15),
        }
    )


@pytest.fixture
def fastf1_race_result_for_non_finishing_driver():
    # Simplified.
    return fastf1.core.DriverResult(
        {
            "Abbreviation": "LAT",
            "FirstName": "Nicholas",
            "LastName": "Latifi",
            "FullName": "Nicholas Latifi",
            "TeamName": "Williams",
            "Position": np.float64(20),
            "GridPosition": np.float64(20),
            "Laps": np.float64(0),
            "Points": np.float64(0.0),
            "ClassifiedPosition": "R",
            "Time": pd.NaT,
        }
    )


@pytest.fixture
def fastf1_quali_result_for_pole_driver():
    # Simplified.
    return fastf1.core.DriverResult(
        {
            "Abbreviation": "VER",
            "FirstName": "Max",
            "LastName": "Verstappen",
            "FullName": "Max Verstappen",
            "TeamName": "Red Bull",
            "Position": np.float64(1),
            "Q1": pd.Timedelta(minutes=1, seconds=30, milliseconds=500),
            "Q2": pd.Timedelta(minutes=1, seconds=29, milliseconds=500),
            "Q3": pd.Timedelta(minutes=1, seconds=28, milliseconds=500),
        }
    )


@pytest.fixture
def fastf1_quali_result_for_last_place():
    # Simplified.
    return fastf1.core.DriverResult(
        {
            "Abbreviation": "LAT",
            "FirstName": "Nicholas",
            "LastName": "Latifi",
            "FullName": "Nicholas Latifi",
            "TeamName": "Williams",
            "Position": np.float64(20),
            "Q1": pd.Timedelta(minutes=1, seconds=31, milliseconds=500),
            "Q2": pd.NaT,
            "Q3": pd.NaT,
        }
    )
