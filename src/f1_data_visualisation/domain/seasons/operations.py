from sqlalchemy import orm

from f1_data_visualisation.data import models
from f1_data_visualisation.domain.seasons import entities, queries


def get_or_create_season(session: orm.Session, year: int) -> entities.Season:
    """
    Create a new season entry in the database, if it doesn't exist yet.
    """
    existing_season = queries.get_season_by_year(session=session, year=year)
    if existing_season:
        return existing_season
    season = models.Season(year=year)
    session.add(season)
    session.flush()
    return entities.Season(id=season.id, year=season.year)
