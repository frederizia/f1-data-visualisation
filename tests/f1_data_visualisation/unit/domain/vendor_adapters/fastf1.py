import datetime
from unittest import mock

import pandas as pd

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
