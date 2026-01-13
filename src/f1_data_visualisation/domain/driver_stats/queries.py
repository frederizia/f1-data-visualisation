import attrs
from sqlalchemy import orm

from f1_data_visualisation.domain.drivers import (
    entities as driver_entities,
)
from f1_data_visualisation.domain.drivers import (
    queries as driver_queries,
)


class CannotCalculatePointsForSeasonError(Exception):
    pass


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


@attrs.frozen
class DriverSeasonPoints:
    year: int
    points_per_round: list[AccumulativePointsPerRound]
    total_points: float


@attrs.frozen
class DriverPointsPerSeason:
    driver: driver_entities.Driver
    seasons: list[DriverSeasonPoints]
    total_points: float


def get_total_points_for_driver_across_seasons(
    db_session: orm.Session, driver_id: int, years: list[int]
) -> DriverPointsPerSeason:
    """
    Get the total points for a driver across multiple seasons.
    """
    driver = driver_queries.get_driver_by_id(db_session=db_session, database_id=driver_id)
    if not driver:
        raise CannotCalculatePointsForSeasonError("Driver {driver_id} not found.")
    total_points = 0.0
    season_points_summary: list[DriverSeasonPoints] = []
    for year in years:
        driver_results = get_accumulative_points_per_round_for_driver(
            db_session=db_session, driver_id=driver_id, year=year
        )
        season_points = sum(result.points for result in driver_results)
        total_points += season_points
        season_points_summary.append(
            DriverSeasonPoints(
                year=year,
                points_per_round=driver_results,
                total_points=season_points,
            )
        )
    return DriverPointsPerSeason(
        driver=driver, seasons=season_points_summary, total_points=total_points
    )
