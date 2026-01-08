import datetime
from unittest import mock

import pandas as pd
import pytest

from f1_data_visualisation.domain.drivers import entities as driver_entities
from f1_data_visualisation.domain.vendor_adapters import fastf1 as adapter


class TestFast1:
    def test_get_all_rounds_for_season_parses_correctly(self):
        fastf1_adapter = adapter.FastF1()
        with mock.patch.object(
            adapter.fastf1,
            "get_event_schedule",
        ) as mock_get_event_schedule:
            mock_get_event_schedule.return_value = adapter.fastf1.events.EventSchedule(
                data={
                    "RoundNumber": [0, 1, 2],
                    "Country": ["", "Bahrain", "Saudi Arabia"],
                    "Location": ["", "Sakhir", "Jeddah"],
                    "EventName": ["", "Bahrain Grand Prix", "Saudi Arabian Grand Prix"],
                    "Session1Date": [
                        pd.NaT,
                        pd.Timestamp("2023-03-05 15:00:00"),
                        pd.Timestamp("2023-03-19 15:00:00"),
                    ],
                    "Session5Date": [
                        pd.NaT,
                        pd.Timestamp("2023-03-07 15:00:00"),
                        pd.Timestamp("2023-04-02 15:00:00"),
                    ],
                }
            )
            rounds = fastf1_adapter.get_all_rounds_for_season(2023)

        assert len(rounds) == 2

        first_round = rounds[0]
        assert first_round.number == 1
        assert first_round.country == "Bahrain"
        assert first_round.location == "Sakhir"
        assert first_round.name == "Bahrain Grand Prix"
        assert first_round.date_from == datetime.date(2023, 3, 5)
        assert first_round.date_to == datetime.date(2023, 3, 7)

    @pytest.mark.parametrize(
        ("classified_position", "expected_status"),
        [
            (1, driver_entities.DriverSessionClassificationStatus.CLASSIFIED),
            ("R", driver_entities.DriverSessionClassificationStatus.RETIRED),
            ("D", driver_entities.DriverSessionClassificationStatus.DISQUALIFIED),
            ("E", driver_entities.DriverSessionClassificationStatus.EXCLUDED),
            ("W", driver_entities.DriverSessionClassificationStatus.WITHDRAWN),
            ("N", driver_entities.DriverSessionClassificationStatus.NOT_CLASSIFIED),
            ("F", driver_entities.DriverSessionClassificationStatus.FAILED_TO_QUALIFY),
            (None, driver_entities.DriverSessionClassificationStatus.RETIRED),
        ],
    )
    def test_derives_classification_status_correctly(self, classified_position, expected_status):
        fastf1_adapter = adapter.FastF1()

        actual_status = fastf1_adapter._derive_classification_status(classified_position)

        assert actual_status == expected_status

    def test_get_driver_session_results_parses_correctly_for_qualifying(
        self, fastf1_quali_result_for_last_place, fastf1_quali_result_for_pole_driver
    ):
        fastf1_adapter = adapter.FastF1()
        with mock.patch.object(
            adapter.fastf1,
            "get_session",
        ) as mock_get_session:
            mock_session = mock.MagicMock(date=pd.Timestamp("2023-03-05 15:00:00"))
            mock_get_session.load.return_value = mock_session
            # No, these are not real results.
            mock_session.drivers = ["1", "6"]
            mock_session.get_driver.side_effect = [
                fastf1_quali_result_for_pole_driver,
                fastf1_quali_result_for_last_place,
            ]

            mock_get_session.side_effect = [
                mock_session,
                ValueError,
                ValueError,
                ValueError,
                ValueError,
            ]

            sessions = fastf1_adapter.get_competitive_sessions_for_round(
                year=2023,
                round_number=1,
            )

        assert len(sessions) == 1
        qualifying_info = sessions[0]
        assert len(qualifying_info.results) == 2

        first_qualifying_result = qualifying_info.results[0]
        assert first_qualifying_result.driver.display_name == "Max Verstappen"
        assert first_qualifying_result.result.constructor.name == "Red Bull"
        assert first_qualifying_result.result.position == 1
        assert first_qualifying_result.result.q3_time == datetime.timedelta(
            minutes=1, seconds=28, milliseconds=500
        )

        second_qualifying_result = qualifying_info.results[1]
        assert second_qualifying_result.driver.display_name == "Nicholas Latifi"
        assert second_qualifying_result.result.constructor.name == "Williams"
        assert second_qualifying_result.result.position == 20
        assert not second_qualifying_result.result.q3_time

    def test_get_driver_session_results_parses_correctly_for_race(
        self, fastf1_race_result_for_winning_driver, fastf1_race_result_for_non_finishing_driver
    ):
        fastf1_adapter = adapter.FastF1()
        with mock.patch.object(
            adapter.fastf1,
            "get_session",
        ) as mock_get_session:
            mock_session = mock.MagicMock(date=pd.Timestamp("2023-03-04 15:00:00"))
            mock_get_session.load.return_value = mock_session
            # No, these are not real results.

            mock_session.drivers = ["1", "6"]
            mock_session.get_driver.side_effect = [
                fastf1_race_result_for_winning_driver,
                fastf1_race_result_for_non_finishing_driver,
            ]

            mock_get_session.side_effect = [
                ValueError,
                ValueError,
                ValueError,
                mock_session,
                ValueError,
            ]

            sessions = fastf1_adapter.get_competitive_sessions_for_round(
                year=2023,
                round_number=1,
            )

        assert len(sessions) == 1
        race_info = sessions[0]

        first_race_result = race_info.results[0]
        assert first_race_result.driver.display_name == "Max Verstappen"
        assert first_race_result.result.constructor.name == "Red Bull"
        assert first_race_result.result.position == 1
        assert first_race_result.result.laps_completed == 56
        assert first_race_result.result.points == 25.0
        assert (
            first_race_result.result.status
            == driver_entities.DriverSessionClassificationStatus.CLASSIFIED
        )
        assert first_race_result.result.grid_position == 1
        assert first_race_result.result.time == datetime.timedelta(hours=1, minutes=30, seconds=15)

        second_race_result = race_info.results[1]
        assert second_race_result.driver.display_name == "Nicholas Latifi"
        assert second_race_result.result.constructor.name == "Williams"
        assert second_race_result.result.position == 20
        assert second_race_result.result.laps_completed == 0
        assert second_race_result.result.points == 0.0
        assert (
            second_race_result.result.status
            == driver_entities.DriverSessionClassificationStatus.RETIRED
        )
