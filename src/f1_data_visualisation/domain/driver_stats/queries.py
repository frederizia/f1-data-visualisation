import attrs
from sqlalchemy import orm

from f1_data_visualisation.domain.drivers import queries as driver_queries


@attrs.frozen
class AccumulativePointsPerRound:
    round_number: int
    points: float
    accumulated_points: float


def get_accumulative_points_per_round_for_driver(
    db_session: orm.Session,
    driver_id: int,
    year: int,
) -> list[AccumulativePointsPerRound]:
    """
    Get the accumulative points per round for a driver in a given season.
    """
    # We need to get all the driver race results for the given driver and season, ordered by round number.
    driver_results = driver_queries.get_driver_race_results_for_season(
        year=year, driver_id=driver_id, db_session=db_session
    )
    # Sort the results by round number to ensure correct accumulation.
    driver_results.sort(key=lambda result: result.session.round.number)
    total_points = 0.0
    accumulative_points_per_round: list[AccumulativePointsPerRound] = []
    for result in driver_results:
        total_points += result.points
        round_number = result.session.round.number
        accumulative_points_per_round.append(
            AccumulativePointsPerRound(
                round_number=round_number,
                points=result.points,
                accumulated_points=total_points,
            )
        )
    return accumulative_points_per_round
