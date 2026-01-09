import datetime

from sqlalchemy import orm

from f1_data_visualisation.data import models
from f1_data_visualisation.domain.drivers import entities, queries
from f1_data_visualisation.domain.seasons import queries as season_queries
from f1_data_visualisation.domain.sessions import queries as session_queries


class UnableToCreateDriverSeasonError(Exception):
    pass


class UnableToCreateDriverResultError(Exception):
    pass


def get_or_create_driver(
    db_session: orm.Session, first_name: str, last_name: str, display_name: str
) -> entities.Driver:
    """
    Create a new driver entry in the database, if it doesn't exist yet.

    This does not create any information about a season.
    """
    existing_driver = queries.get_driver(db_session=db_session, display_name=display_name)
    if existing_driver:
        return existing_driver
    driver_model = models.Driver(
        first_name=first_name,
        last_name=last_name,
        display_name=display_name,
    )
    db_session.add(driver_model)
    db_session.flush()
    return entities.Driver(
        id=driver_model.id,
        first_name=driver_model.first_name,
        last_name=driver_model.last_name,
        display_name=driver_model.display_name,
    )


def get_or_create_constructor(db_session: orm.Session, name: str) -> entities.Constructor:
    """
    Create a new constructor entry in the database, if it doesn't exist yet.
    """
    existing_constructor = queries.get_constructor(db_session=db_session, name=name)
    if existing_constructor:
        return existing_constructor
    constructor_model = models.Constructor(name=name)
    db_session.add(constructor_model)
    db_session.flush()
    return entities.Constructor(
        id=constructor_model.id,
        name=constructor_model.name,
    )


def get_or_create_driver_season(
    db_session: orm.Session,
    driver_id: int,
    number: int,
    short_code: str,
    year: int,
) -> entities.DriverSeasonWithDriverAndSeason:
    """
    Create a new driver season entry in the database, if it doesn't exist yet.
    """
    existing_driver_season = queries.get_driver_information_for_season(
        db_session=db_session,
        driver_id=driver_id,
        year=year,
    )
    if existing_driver_season:
        return existing_driver_season
    driver = queries.get_driver_by_id(db_session=db_session, database_id=driver_id)
    if not driver:
        raise UnableToCreateDriverSeasonError(f"Driver matching ID {driver_id} does not exist.")
    season = season_queries.get_season_by_year(db_session=db_session, year=year)
    if not season:
        raise UnableToCreateDriverSeasonError(f"Season matching year {year} does not exist.")
    driver_season_model = models.DriverSeason(
        driver_id=driver_id,
        season_id=season.id,
        number=number,
        short_code=short_code,
    )
    db_session.add(driver_season_model)
    db_session.flush()
    return entities.DriverSeasonWithDriverAndSeason(
        id=driver_season_model.id,
        number=driver_season_model.number,
        short_code=driver_season_model.short_code,
        driver=driver,
        season=season,
    )


def get_or_create_race_result(
    db_session: orm.Session,
    driver_id: int,
    session_id: int,
    position: int,
    constructor_name: str,
    laps_completed: int,
    points: float,
    status: entities.DriverSessionClassificationStatus,
    grid_position: int,
    time: datetime.timedelta | None,
) -> entities.RaceDriverResult:
    """
    Create a new driver race result entry in the database, if it doesn't exist yet.
    """
    existing_result = queries.get_session_result_for_driver(
        db_session=db_session, driver_id=driver_id, session_id=session_id
    )
    if existing_result:
        assert isinstance(existing_result, entities.RaceDriverResult)
        return existing_result
    if not queries.get_driver_by_id(db_session=db_session, database_id=driver_id):
        raise UnableToCreateDriverResultError(f"Driver matching ID {driver_id} does not exist.")
    if not session_queries.get_session_by_id(db_session=db_session, database_id=session_id):
        raise UnableToCreateDriverResultError(f"Session matching ID {session_id} does not exist.")
    constructor = get_or_create_constructor(db_session=db_session, name=constructor_name)
    result_model = models.DriverSessionResult(
        driver_id=driver_id,
        session_id=session_id,
        constructor_id=constructor.id,
        position=position,
        laps_completed=laps_completed,
        points=points,
        classification_status=status.value,
        grid_position=grid_position,
        time=time.total_seconds() if time else None,
    )
    db_session.add(result_model)
    db_session.flush()
    return entities.RaceDriverResult(
        id=result_model.id,
        constructor=constructor,
        position=result_model.position,
        laps_completed=result_model.laps_completed,
        points=result_model.points,
        status=status,
        grid_position=result_model.grid_position,
        time=time,
    )


def get_or_create_qualifying_result(
    db_session: orm.Session,
    driver_id: int,
    session_id: int,
    position: int,
    constructor_name: str,
    q1_time: datetime.timedelta | None,
    q2_time: datetime.timedelta | None,
    q3_time: datetime.timedelta | None,
) -> entities.QualifyingDriverResult:
    """
    Create a new driver qualifying result entry in the database, if it doesn't exist yet.
    """
    existing_result = queries.get_session_result_for_driver(
        db_session=db_session, driver_id=driver_id, session_id=session_id
    )
    if existing_result:
        assert isinstance(existing_result, entities.QualifyingDriverResult)
        return existing_result
    if not queries.get_driver_by_id(db_session=db_session, database_id=driver_id):
        raise UnableToCreateDriverResultError(f"Driver matching ID {driver_id} does not exist.")
    if not session_queries.get_session_by_id(db_session=db_session, database_id=session_id):
        raise UnableToCreateDriverResultError(f"Session matching ID {session_id} does not exist.")
    constructor = get_or_create_constructor(db_session=db_session, name=constructor_name)
    result_model = models.DriverSessionResult(
        driver_id=driver_id,
        session_id=session_id,
        constructor_id=constructor.id,
        position=position,
        q1_time=q1_time.total_seconds() if q1_time else None,
        q2_time=q2_time.total_seconds() if q2_time else None,
        q3_time=q3_time.total_seconds() if q3_time else None,
    )
    db_session.add(result_model)
    db_session.flush()
    return entities.QualifyingDriverResult(
        id=result_model.id,
        constructor=constructor,
        position=result_model.position,
        q1_time=q1_time,
        q2_time=q2_time,
        q3_time=q3_time,
    )
