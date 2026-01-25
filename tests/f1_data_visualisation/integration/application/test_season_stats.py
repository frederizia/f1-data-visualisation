from unittest import mock

import pytest

from f1_data_visualisation.application import season_stats
from tests.f1_data_visualisation import factories


class TestStoreSeasonStandings:
    def test_successfully_stores_all_drivers_results(self, db_session, mock_get_session):
        season = factories.Season(year=2022)

        # Create 3 drivers and their associated driver season objects with different points.
        first_place_driver = factories.Driver()
        first_place_driver_season = factories.DriverSeason(
            driver=first_place_driver, season=season, position=None, points=0.0
        )
        second_place_driver = factories.Driver()
        second_place_driver_season = factories.DriverSeason(
            driver=second_place_driver, season=season, position=None, points=0.0
        )
        third_place_driver = factories.Driver()
        third_place_driver_season = factories.DriverSeason(
            driver=third_place_driver, season=season, position=None, points=0.0
        )

        # Create some rounds for the season.
        round1 = factories.Round(number=1, season=season)
        round2 = factories.Round(number=2, season=season)
        round3 = factories.Round(number=3, season=season)
        rounds = [round1, round2, round3]

        self._create_race_results(driver=first_place_driver, rounds=rounds, points_multiplier=3)
        self._create_race_results(driver=second_place_driver, rounds=rounds, points_multiplier=2)
        self._create_race_results(driver=third_place_driver, rounds=rounds, points_multiplier=1)
        with mock.patch(
            "f1_data_visualisation.data.database.get_session", side_effect=mock_get_session
        ):
            season_stats.store_season_standings(year=2022)

        # Check that the driver seasons have been updated with correct points and positions.
        assert first_place_driver_season.points == 18
        assert first_place_driver_season.position == 1
        assert second_place_driver_season.points == 12
        assert second_place_driver_season.position == 2
        assert third_place_driver_season.points == 6
        assert third_place_driver_season.position == 3

    def test_raises_when_no_standings_can_be_determined(self, db_session, mock_get_session):
        factories.Season(year=2023)
        with (
            mock.patch(
                "f1_data_visualisation.data.database.get_session", side_effect=mock_get_session
            ),
            pytest.raises(season_stats.NoSeasonStandingsAvailableError),
        ):
            season_stats.store_season_standings(year=2023)

    def test_raises_when_driver_season_cannot_be_updated(self, db_session, mock_get_session):
        season = factories.Season(year=2022)
        # Let's simplify this test by only creating a single driver, but no driver season.
        driver = factories.Driver()

        # Create some rounds for the season.
        round1 = factories.Round(number=1, season=season)
        round2 = factories.Round(number=2, season=season)
        round3 = factories.Round(number=3, season=season)
        rounds = [round1, round2, round3]

        self._create_race_results(driver=driver, rounds=rounds, points_multiplier=3)
        with (
            mock.patch(
                "f1_data_visualisation.data.database.get_session", side_effect=mock_get_session
            ),
            pytest.raises(season_stats.UnableToUpdateDriverSeasonError),
        ):
            season_stats.store_season_standings(year=2022)

    def _create_race_results(self, driver, rounds, points_multiplier: int) -> None:
        for i, round_ in enumerate(rounds):
            factories.DriverRaceResult(
                driver=driver,
                session__round=round_,
                points=(i + 1) * points_multiplier,
            )
