from sqlalchemy import orm

from f1_data_visualisation.data import database
from f1_data_visualisation.domain.drivers import (
    entities as driver_entities,
)
from f1_data_visualisation.domain.drivers import (
    operations as driver_operations,
)
from f1_data_visualisation.domain.rounds import entities as round_entities
from f1_data_visualisation.domain.rounds import operations as round_operations
from f1_data_visualisation.domain.seasons import operations as season_operations
from f1_data_visualisation.domain.sessions import operations as session_operations
from f1_data_visualisation.domain.vendor_adapters import fastf1


class UnableToStoreResultsError(Exception):
    pass


def download_all_results_for_season(year: int) -> None:
    """
    Download and store data for all competitive sessions in a given F1 season.

    We use fastf1 to download the data and then store it. If data already exists, it is skipped (we don't check for
    changes).

    We catch some errors which are _highly_ unlikely to occur as we're just making sure all the required objects exist
    but it's good practice.
    """
    fastf1_adapter = fastf1.FastF1()
    with database.get_session() as db_session:
        # Store the season.
        season_operations.get_or_create_season(year=year, db_session=db_session)
        # Get all rounds for the given season.
        rounds = fastf1_adapter.get_all_rounds_for_season(year)

        for round_info in rounds:
            # Store the round.
            round_object = round_operations.get_or_create_round(
                db_session=db_session,
                year=year,
                number=round_info.number,
                country=round_info.country,
                location=round_info.location,
                name=round_info.name,
                date_from=round_info.date_from,
                date_to=round_info.date_to,
            )
            # We only get quali and race results.
            sessions = fastf1_adapter.get_competitive_sessions_for_round(
                year=year, round_number=round_info.number
            )
            for session_summary in sessions:
                _store_session_data_and_results(
                    db_session=db_session,
                    round_object=round_object,
                    session_summary=session_summary,
                    year=year,
                )
        # Finally, commit the data.
        db_session.commit()


def _store_session_data_and_results(
    db_session: orm.Session,
    round_object: round_entities.Round,
    session_summary: fastf1.SessionInformation,
    year: int,
) -> None:
    """
    Store all session data and results for a given session summary.

    This includes the session itself, results for all drivers, and additional driver information.
    """
    session_info = session_summary.session
    session = session_operations.get_or_create_session(
        db_session=db_session,
        round_number=round_object.number,
        year=year,
        date=session_info.date,
        session_type=session_info.type,
    )
    for driver_summary in session_summary.results:
        # We store all the driver information, if it doesn't already exist.
        driver_info = driver_summary.driver
        driver_season_info = driver_summary.driver_season
        driver_result_info = driver_summary.result
        driver = driver_operations.get_or_create_driver(
            db_session=db_session,
            first_name=driver_info.first_name,
            last_name=driver_info.last_name,
            display_name=driver_info.display_name,
        )
        assert driver.id is not None, "Driver ID should be set after creation."
        try:
            driver_operations.get_or_create_driver_season(
                db_session=db_session,
                driver_id=driver.id,
                year=year,
                number=driver_season_info.number,
                short_code=driver_season_info.short_code,
            )
        except driver_operations.UnableToCreateDriverSeasonError as e:
            raise UnableToStoreResultsError(
                f"Unable to create season info for driver {driver.display_name} for year {year}"
            ) from e
        try:
            if isinstance(driver_result_info, driver_entities.RaceDriverResult):
                driver_operations.get_or_create_race_result(
                    db_session=db_session,
                    driver_id=driver.id,
                    session_id=session.id,
                    position=driver_result_info.position,
                    points=driver_result_info.points,
                    grid_position=driver_result_info.grid_position,
                    laps_completed=driver_result_info.laps_completed,
                    status=driver_result_info.status,
                    constructor_name=driver_result_info.constructor.name,
                    time=driver_result_info.time,
                )
            elif isinstance(driver_result_info, driver_entities.QualifyingDriverResult):
                driver_operations.get_or_create_qualifying_result(
                    db_session=db_session,
                    driver_id=driver.id,
                    session_id=session.id,
                    position=driver_result_info.position,
                    q1_time=driver_result_info.q1_time,
                    q2_time=driver_result_info.q2_time,
                    q3_time=driver_result_info.q3_time,
                    constructor_name=driver_result_info.constructor.name,
                )
        except driver_operations.UnableToCreateDriverResultError as e:
            raise UnableToStoreResultsError(
                f"Unable to create session result for driver {driver.display_name} for session {session.id}"
            ) from e
