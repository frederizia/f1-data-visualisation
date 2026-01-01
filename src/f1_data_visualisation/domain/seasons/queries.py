import sqlalchemy
from sqlalchemy import orm

from f1_data_visualisation.data import models
from f1_data_visualisation.domain.seasons import entities


def get_season_by_year(session: orm.Session, year: int) -> entities.Season | None:
    """
    Retrieve a season by its year.
    """
    query = sqlalchemy.select(models.Season).filter(models.Season.year == year)
    try:
        season = session.execute(query).scalars().one()
    except sqlalchemy.exc.NoResultFound:  # type: ignore[possibly-missing-attribute]
        return None
    return entities.Season(id=season.id, year=season.year)
