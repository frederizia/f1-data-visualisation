import datetime

import sqlalchemy
from sqlalchemy import orm

from f1_data_visualisation.data import models
from f1_data_visualisation.domain.drivers import entities
from f1_data_visualisation.domain.rounds import entities as round_entities
from f1_data_visualisation.domain.seasons import entities as season_entities
from f1_data_visualisation.domain.sessions import entities as session_entities


class UnsupportedSessionTypeError(Exception):
    pass


def get_driver_information_for_season(
    db_session: orm.Session, driver_id: int, year: int
) -> entities.DriverSeasonWithDriverAndSeason | None:
    """
    Retrieve a driver for a year for the given driver ID.

    This returns the information which would've been accurate for the driver for that specific
    season.
    """
    query = (
        sqlalchemy.select(models.DriverSeason)
        .join(models.Season)
        .join(models.Driver)
        .filter(models.Season.year == year, models.Driver.id == driver_id)
    )
    try:
        driver_season_model = db_session.execute(query).scalars().one()
    except sqlalchemy.exc.NoResultFound:  # type: ignore[possibly-missing-attribute]
        return None
    driver_model = driver_season_model.driver
    driver = entities.Driver(
        id=driver_model.id,
        first_name=driver_model.first_name,
        last_name=driver_model.last_name,
        display_name=driver_model.display_name,
    )
    season = season_entities.Season(
        year=driver_season_model.season.year, id=driver_season_model.season.id
    )

    return entities.DriverSeasonWithDriverAndSeason(
        id=driver_season_model.id,
        number=driver_season_model.number,
        short_code=driver_season_model.short_code,
        driver=driver,
        season=season,
    )


def get_driver_with_season_info(
    db_session: orm.Session, display_name: str
) -> entities.DriverWithSeasons | None:
    """
    Retrieve a driver with all its available season information.

    This returns the driver and all the season information we have stored.
    """
    query = (
        sqlalchemy.select(models.Driver)
        .join(models.DriverSeason)
        .filter(models.Driver.display_name == display_name)
    )
    try:
        driver_model = db_session.execute(query).scalars().one()
    except sqlalchemy.exc.NoResultFound:  # type: ignore[possibly-missing-attribute]
        return None
    seasons = [
        entities.DriverSeasonWithSeason(
            id=season_model.id,
            number=season_model.number,
            short_code=season_model.short_code,
            season=season_entities.Season(
                id=season_model.season.id, year=season_model.season.year
            ),
        )
        for season_model in driver_model.seasons
    ]
    return entities.DriverWithSeasons(
        id=driver_model.id,
        first_name=driver_model.first_name,
        last_name=driver_model.last_name,
        display_name=driver_model.display_name,
        seasons=seasons,
    )


def get_driver(db_session: orm.Session, display_name: str) -> entities.Driver | None:
    """
    Retrieve a driver using the display name as identifier.

    This does not return any information about the seasons.
    """
    query = sqlalchemy.select(models.Driver).filter(models.Driver.display_name == display_name)
    try:
        driver_model = db_session.execute(query).scalars().one()
    except sqlalchemy.exc.NoResultFound:  # type: ignore[possibly-missing-attribute]
        return None
    return entities.Driver(
        id=driver_model.id,
        first_name=driver_model.first_name,
        last_name=driver_model.last_name,
        display_name=driver_model.display_name,
    )


def get_driver_by_id(db_session: orm.Session, database_id: int) -> entities.Driver | None:
    """
    Retrieve a driver using the database ID.
    """
    query = sqlalchemy.select(models.Driver).filter(models.Driver.id == database_id)
    try:
        driver_model = db_session.execute(query).scalars().one()
    except sqlalchemy.exc.NoResultFound:  # type: ignore[possibly-missing-attribute]
        return None
    return entities.Driver(
        id=driver_model.id,
        first_name=driver_model.first_name,
        last_name=driver_model.last_name,
        display_name=driver_model.display_name,
    )


def get_constructor(db_session: orm.Session, name: str) -> entities.Constructor | None:
    """
    Retrieve a constructor using the name as identifier.
    """
    query = sqlalchemy.select(models.Constructor).filter(models.Constructor.name == name)
    try:
        constructor_model = db_session.execute(query).scalars().one()
    except sqlalchemy.exc.NoResultFound:  # type: ignore[possibly-missing-attribute]
        return None
    return entities.Constructor(
        id=constructor_model.id,
        name=constructor_model.name,
    )


def get_session_result_for_driver(
    db_session: orm.Session,
    driver_id: int,
    session_id: int,
) -> entities.RaceDriverResult | entities.QualifyingDriverResult | None:
    """
    Retrieve a driver session result for a given driver and session.

    We only support qualifying and races as the other sessions do not have meaningful results.
    """
    query = sqlalchemy.select(models.DriverSessionResult).filter(
        models.DriverSessionResult.driver_id == driver_id,
        models.DriverSessionResult.session_id == session_id,
    )
    try:
        result_model = db_session.execute(query).scalars().one()
    except sqlalchemy.exc.NoResultFound:  # type: ignore[possibly-missing-attribute]
        return None
    if result_model.session.type in (
        session_entities.SessionType.RACE.value,
        session_entities.SessionType.SPRINT_RACE.value,
    ):
        return entities.RaceDriverResult(
            id=result_model.id,
            constructor=_get_constructor_from_result(result_model),
            position=result_model.position,
            laps_completed=result_model.laps_completed,
            points=result_model.points,
            status=entities.DriverSessionClassificationStatus(result_model.classification_status),
            grid_position=result_model.grid_position,
            time=datetime.timedelta(seconds=result_model.time) if result_model.time else None,
        )
    if result_model.session.type in (
        session_entities.SessionType.QUALIFYING.value,
        session_entities.SessionType.SPRINT_QUALIFYING,
    ):
        return entities.QualifyingDriverResult(
            id=result_model.id,
            constructor=_get_constructor_from_result(result_model),
            position=result_model.position,
            q1_time=datetime.timedelta(seconds=result_model.q1_time)
            if result_model.q1_time
            else None,
            q2_time=datetime.timedelta(seconds=result_model.q2_time)
            if result_model.q2_time
            else None,
            q3_time=datetime.timedelta(seconds=result_model.q3_time)
            if result_model.q3_time
            else None,
        )
    raise UnsupportedSessionTypeError(
        f"Session type {result_model.session.type} is not supported for driver results."
    )


def get_driver_race_results_for_season(
    db_session: orm.Session, driver_id: int, year: int
) -> list[entities.RaceDriverResultWithSession]:
    """
    Retrieve all race results for a given driver in a given season.
    """
    query = (
        sqlalchemy.select(models.DriverSessionResult)
        .join(models.Session)
        .join(models.Round)
        .join(models.Season)
        .filter(
            models.DriverSessionResult.driver_id == driver_id,
            models.Season.year == year,
            models.Session.type.in_(
                [
                    session_entities.SessionType.RACE.value,
                    session_entities.SessionType.SPRINT_RACE.value,
                ]
            ),
        )
    )
    results = db_session.execute(query).scalars().all()
    return [
        entities.RaceDriverResultWithSession(
            id=result_model.id,
            constructor=_get_constructor_from_result(result_model),
            position=result_model.position,
            laps_completed=result_model.laps_completed,
            points=result_model.points,
            status=entities.DriverSessionClassificationStatus(result_model.classification_status),
            grid_position=result_model.grid_position,
            time=datetime.timedelta(seconds=result_model.time) if result_model.time else None,
            session=session_entities.SessionWithRound(
                id=result_model.session.id,
                type=session_entities.SessionType(result_model.session.type),
                date=result_model.session.date,
                round=round_entities.RoundWithSeason(
                    id=result_model.session.round.id,
                    number=result_model.session.round.number,
                    name=result_model.session.round.name,
                    country=result_model.session.round.country,
                    location=result_model.session.round.location,
                    date_from=result_model.session.round.date_from,
                    date_to=result_model.session.round.date_to,
                    season=season_entities.Season(
                        id=result_model.session.round.season.id,
                        year=result_model.session.round.season.year,
                    ),
                ),
            ),
        )
        for result_model in results
    ]


def _get_constructor_from_result(result_model: models.DriverSessionResult) -> entities.Constructor:
    return entities.Constructor(
        id=result_model.constructor.id,
        name=result_model.constructor.name,
    )
