import pytest

from f1_data_visualisation.domain.driver_stats import queries
from f1_data_visualisation.domain.sessions import entities as session_entities
from tests.f1_data_visualisation import factories


class TestGetAccumulativePointsPerRoundForDriver:
    def test_correctly_accumulates_points_per_round(self, db_session):
        driver = factories.Driver()
        season = factories.Season(year=2022)

        for i in range(5):
            factories.DriverRaceResult(
                driver=driver,
                session__round__season=season,
                session__round__number=i + 1,
                points=i + 1,
            )

        accumulative_points = queries.get_accumulative_points_per_round_for_driver(
            db_session=db_session,
            driver_id=driver.id,
            year=season.year,
        )

        assert len(accumulative_points) == 5
        assert accumulative_points == [
            queries.AccumulativePointsPerRound(round_number=1, points=1.0, accumulated_points=1.0),
            queries.AccumulativePointsPerRound(round_number=2, points=2.0, accumulated_points=3.0),
            queries.AccumulativePointsPerRound(round_number=3, points=3.0, accumulated_points=6.0),
            queries.AccumulativePointsPerRound(
                round_number=4, points=4.0, accumulated_points=10.0
            ),
            queries.AccumulativePointsPerRound(
                round_number=5, points=5.0, accumulated_points=15.0
            ),
        ]


class TestGetTotalPointsForDriverAcrossSeasons:
    def test_correctly_calculates_total_points_across_seasons(self, db_session):
        driver = factories.Driver()

        seasons = [factories.Season(year=year) for year in [2020, 2021, 2022]]

        # To keep it simple, let's create 2 rounds per season with fixed points.
        # This means we will have:
        # 2020: 1 + 2 = 3 points
        # 2021: 2 + 3 = 5 points
        # 2022: 3 + 4 = 7 points
        # Total points = 3 + 5 + 7 = 15 points
        for i, season in enumerate(seasons):
            for j in range(2):
                factories.DriverRaceResult(
                    driver=driver,
                    session__round__season=season,
                    session__round__number=j + 1,
                    points=i + j + 1,
                )

        points_breakdown = queries.get_total_points_for_driver_across_seasons(
            db_session=db_session,
            driver_id=driver.id,
            years=[2020, 2021, 2022],
        )

        assert points_breakdown.total_points == 15
        total_points_by_season = {season.total_points for season in points_breakdown.seasons}
        assert total_points_by_season == {3.0, 5.0, 7.0}

    def test_no_data_existing_is_handled_gracefully(self, db_session):
        driver = factories.Driver()

        points_breakdown = queries.get_total_points_for_driver_across_seasons(
            db_session=db_session,
            driver_id=driver.id,
            years=[2019, 2020],
        )

        assert points_breakdown.total_points == 0
        assert all(season.total_points == 0 for season in points_breakdown.seasons)

    def test_non_existent_driver_raises_error(self, db_session):
        non_existent_driver_id = 9999
        with pytest.raises(queries.CannotCalculatePointsForSeasonError):
            queries.get_total_points_for_driver_across_seasons(
                db_session=db_session,
                driver_id=non_existent_driver_id,
                years=[2020],
            )


class TestGetDriverPositionsPerRound:
    def test_correctly_retrieves_driver_positions_per_round(self, db_session):
        driver = factories.Driver()
        season = factories.Season(year=2022)

        # Create 2 rounds, one with just a main race, one with a sprint and main race.
        round1 = factories.Round(number=1, season=season)
        quali_rd1 = factories.Session(
            round=round1, type=session_entities.SessionType.QUALIFYING.value
        )
        main_race_rd1 = factories.Session(
            round=round1, type=session_entities.SessionType.RACE.value
        )
        # Driver results: quali=2, grid=3, position=1
        factories.DriverQualifyingResult(driver=driver, session=quali_rd1, position=2)
        factories.DriverRaceResult(
            driver=driver, session=main_race_rd1, grid_position=3, position=1
        )

        round2 = factories.Round(number=2, season=season)
        quali_sprint_rd2 = factories.Session(
            round=round2, type=session_entities.SessionType.SPRINT_QUALIFYING.value
        )
        sprint_rd2 = factories.Session(
            round=round2, type=session_entities.SessionType.SPRINT_RACE.value
        )
        quali_rd2 = factories.Session(
            round=round2, type=session_entities.SessionType.QUALIFYING.value
        )
        main_race_rd2 = factories.Session(
            round=round2, type=session_entities.SessionType.RACE.value
        )
        # Driver results: sprint quali=1, sprint grid=2, sprint position=3
        factories.DriverQualifyingResult(driver=driver, session=quali_sprint_rd2, position=1)
        factories.DriverRaceResult(driver=driver, session=sprint_rd2, grid_position=2, position=3)
        # Driver results: quali=4, grid=5, position=2
        factories.DriverQualifyingResult(driver=driver, session=quali_rd2, position=4)
        factories.DriverRaceResult(
            driver=driver, session=main_race_rd2, grid_position=5, position=2
        )

        driver_positions = queries.get_driver_positions_per_round(
            db_session=db_session, driver_id=driver.id, year=2022
        )

        # Check if the positions are correctly retrieved.
        assert len(driver_positions) == 2
        assert driver_positions == [
            queries.DriverPositionsForRound(
                round_number=1,
                main_race=queries.RaceInRound(
                    qualifying_position=2,
                    grid_position=3,
                    position=1,
                ),
                sprint_race=None,
            ),
            queries.DriverPositionsForRound(
                round_number=2,
                main_race=queries.RaceInRound(
                    qualifying_position=4,
                    grid_position=5,
                    position=2,
                ),
                sprint_race=queries.RaceInRound(
                    qualifying_position=1,
                    grid_position=2,
                    position=3,
                ),
            ),
        ]

    def test_returns_empty_list_if_no_data(self, db_session):
        driver = factories.Driver()

        driver_positions = queries.get_driver_positions_per_round(
            db_session=db_session, driver_id=driver.id, year=2022
        )

        assert driver_positions == []

    def test_sessions_exist_but_driver_has_no_results(self, db_session):
        driver = factories.Driver()
        season = factories.Season(year=2022)

        round1 = factories.Round(number=1, season=season)
        # Create sprint and main race sessions without driver results.
        factories.Session(round=round1, type=session_entities.SessionType.SPRINT_QUALIFYING.value)
        factories.Session(round=round1, type=session_entities.SessionType.SPRINT_RACE.value)
        factories.Session(round=round1, type=session_entities.SessionType.QUALIFYING.value)
        factories.Session(round=round1, type=session_entities.SessionType.RACE.value)

        driver_positions = queries.get_driver_positions_per_round(
            db_session=db_session, driver_id=driver.id, year=2022
        )

        assert driver_positions == [
            queries.DriverPositionsForRound(
                round_number=1,
                sprint_race=None,
                main_race=None,
            )
        ]

    def test_race_weekend_without_a_sprint_race_is_handled(self, db_session):
        driver = factories.Driver()
        season = factories.Season(year=2022)

        round1 = factories.Round(number=1, season=season)
        quali_rd1 = factories.Session(
            round=round1, type=session_entities.SessionType.QUALIFYING.value
        )
        main_race_rd1 = factories.Session(
            round=round1, type=session_entities.SessionType.RACE.value
        )
        # Driver results: quali=1, grid=1, position=1 (what a weekend!)
        factories.DriverQualifyingResult(driver=driver, session=quali_rd1, position=1)
        factories.DriverRaceResult(
            driver=driver, session=main_race_rd1, grid_position=1, position=1
        )

        driver_positions = queries.get_driver_positions_per_round(
            db_session=db_session, driver_id=driver.id, year=2022
        )
        assert driver_positions == [
            queries.DriverPositionsForRound(
                round_number=1,
                main_race=queries.RaceInRound(
                    qualifying_position=1,
                    grid_position=1,
                    position=1,
                ),
                sprint_race=None,
            )
        ]
