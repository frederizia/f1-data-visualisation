import attrs
from sqlalchemy import orm

from f1_data_visualisation.domain.drivers import (
    entities as driver_entities,
)
from f1_data_visualisation.domain.drivers import (
    queries as driver_queries,
)
from f1_data_visualisation.domain.rounds import (
    queries as round_queries,
)
from f1_data_visualisation.domain.sessions import (
    entities as session_entities,
)
from f1_data_visualisation.domain.sessions import (
    queries as session_queries,
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


@attrs.frozen
class RaceInRound:
    """
    A race type, e.g. main race or sprint race, and its associated positions.
    """

    qualifying_position: int | None
    grid_position: int | None
    position: int | None


@attrs.frozen
class DriverPositionsForRound:
    round_number: int
    # The race types are both optional as a driver may not have participated in either.
    main_race: RaceInRound | None
    sprint_race: RaceInRound | None


def get_driver_positions_per_round(
    db_session: orm.Session, driver_id: int, year: int
) -> list[DriverPositionsForRound]:
    """
    Get the positions across the competitive sessions per round for a driver.

    This includes both sprints and main races and all relevant positions:
    * qualifying: result at the end of qualifying before penalties
    * grid_position: starting position on the grid after penalties
    * position: finishing position at the end of the race after penalties
    """
    rounds_in_season = round_queries.get_rounds_for_season(db_session=db_session, year=year)
    driver_positions_per_round: list[DriverPositionsForRound] = []

    for round_ in rounds_in_season:
        sprint_race_positions = _get_sprint_race_positions(
            db_session=db_session,
            driver_id=driver_id,
            round_number=round_.number,
            year=year,
        )
        main_race_positions = _get_main_race_positions(
            db_session=db_session,
            driver_id=driver_id,
            round_number=round_.number,
            year=year,
        )
        driver_positions_per_round.append(
            DriverPositionsForRound(
                round_number=round_.number,
                main_race=main_race_positions,
                sprint_race=sprint_race_positions,
            )
        )
    return driver_positions_per_round


def _get_sprint_race_positions(
    db_session: orm.Session, driver_id: int, round_number: int, year: int
) -> RaceInRound | None:
    """
    Retrieve the positions for a sprint race.

    If the round doesn't have a sprint, return None.
    """
    quali_session = session_queries.get_session_by_type(
        db_session=db_session,
        round_number=round_number,
        session_type=session_entities.SessionType.SPRINT_QUALIFYING,
        year=year,
    )
    if not quali_session:
        # We can assume this means there was no sprint race that round.
        return None
    sprint_session = session_queries.get_session_by_type(
        db_session=db_session,
        round_number=round_number,
        session_type=session_entities.SessionType.SPRINT_RACE,
        year=year,
    )
    # This will always exist if there's a quali session, so we do an assert.
    assert sprint_session
    # Now retrieve the driver results for both sessions.
    quali_result = driver_queries.get_session_result_for_driver(
        db_session=db_session,
        session_id=quali_session.id,
        driver_id=driver_id,
    )
    sprint_result = driver_queries.get_session_result_for_driver(
        db_session=db_session,
        session_id=sprint_session.id,
        driver_id=driver_id,
    )
    if not quali_result or not sprint_result:
        # The round may have had a sprint but the driver didn't participate.
        return None
    assert isinstance(quali_result, driver_entities.QualifyingDriverResult)
    assert isinstance(sprint_result, driver_entities.RaceDriverResult)
    return RaceInRound(
        qualifying_position=quali_result.position,
        grid_position=sprint_result.grid_position,
        position=sprint_result.position,
    )


def _get_main_race_positions(
    db_session: orm.Session, driver_id: int, round_number: int, year: int
) -> RaceInRound | None:
    """
    Retrieve the positions for the main race.

    The main race will always exist in any round, though the driver may not have participated.
    """
    quali_session = session_queries.get_session_by_type(
        db_session=db_session,
        round_number=round_number,
        session_type=session_entities.SessionType.QUALIFYING,
        year=year,
    )
    race_session = session_queries.get_session_by_type(
        db_session=db_session,
        round_number=round_number,
        session_type=session_entities.SessionType.RACE,
        year=year,
    )
    # These will always exist so we do an assert.
    assert quali_session
    assert race_session
    # Now get the results.
    quali_result = driver_queries.get_session_result_for_driver(
        db_session=db_session,
        session_id=quali_session.id,
        driver_id=driver_id,
    )
    race_result = driver_queries.get_session_result_for_driver(
        db_session=db_session,
        session_id=race_session.id,
        driver_id=driver_id,
    )
    if not quali_result or not race_result:
        # The driver may not have participated.
        return None
    assert isinstance(quali_result, driver_entities.QualifyingDriverResult)
    assert isinstance(race_result, driver_entities.RaceDriverResult)
    return RaceInRound(
        qualifying_position=quali_result.position,
        grid_position=race_result.grid_position,
        position=race_result.position,
    )


@attrs.frozen
class DriverSeasonStanding:
    driver: driver_entities.Driver
    position: int
    points: float


def get_season_standings(db_session: orm.Session, year: int) -> list[DriverSeasonStanding]:
    """
    Retrieve the driver standings for a given season.
    """
    # Loop over all drivers who participated in the season and get their total points.
    drivers_in_season = driver_queries.get_drivers_per_season(db_session=db_session, year=year)
    # Get the total points per driver.
    driver_points: dict[driver_entities.Driver, float] = {}
    for driver in drivers_in_season:
        # Appease the type checker.
        assert driver.id is not None
        accumulated_points_per_round = get_accumulative_points_per_round_for_driver(
            db_session=db_session, driver_id=driver.id, year=year
        )
        if not accumulated_points_per_round:
            continue
        total_points = accumulated_points_per_round[-1].accumulated_points
        driver_points[driver] = total_points
    # Now sort the drivers by points to get the standings.
    sorted_drivers = sorted(driver_points.items(), key=lambda item: item[1], reverse=True)
    standings: list[DriverSeasonStanding] = []
    for position, (driver, points) in enumerate(sorted_drivers, start=1):
        standings.append(
            DriverSeasonStanding(
                driver=driver,
                position=position,
                points=points,
            )
        )
    return standings
