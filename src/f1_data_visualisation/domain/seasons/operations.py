from sqlalchemy import orm

from f1_data_visualisation.data import models
from f1_data_visualisation.domain.seasons import entities, queries


def get_or_create_season(db_session: orm.Session, year: int) -> tuple[entities.Season, bool]:
    """
    Create a new season entry in the database, if it doesn't exist yet.

    Returns whether the season was created or already existed.
    """
    existing_season = queries.get_season_by_year(db_session=db_session, year=year)
    if existing_season:
        return existing_season, False
    season = models.Season(year=year)
    db_session.add(season)
    db_session.flush()
    return entities.Season(id=season.id, year=season.year), True
