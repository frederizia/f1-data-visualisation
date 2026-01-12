from f1_data_visualisation.domain.driver_stats import queries
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
