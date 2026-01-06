import sqlalchemy
from sqlalchemy import orm

from f1_data_visualisation.data import models
from f1_data_visualisation.domain.drivers import entities
from f1_data_visualisation.domain.seasons import entities as season_entities


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
