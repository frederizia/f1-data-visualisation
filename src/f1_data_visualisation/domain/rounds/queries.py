import sqlalchemy
from sqlalchemy import orm

from f1_data_visualisation.data import models
from f1_data_visualisation.domain.rounds import entities
from f1_data_visualisation.domain.seasons import entities as season_entities


def get_round(db_session: orm.Session, number: int, year: int) -> entities.RoundWithSeason | None:
    """
    Retrieve a round for a year by its number.
    """
    query = (
        sqlalchemy.select(models.Round)
        .join(models.Season)
        .filter(models.Season.year == year, models.Round.number == number)
    )
    try:
        round_model = db_session.execute(query).scalars().one()
    except sqlalchemy.exc.NoResultFound:  # type: ignore[possibly-missing-attribute]
        return None
    season = season_entities.Season(id=round_model.season.id, year=round_model.season.year)
    return entities.RoundWithSeason(
        id=round_model.id,
        season=season,
        number=round_model.number,
        country=round_model.country,
        location=round_model.location,
        name=round_model.name,
        date_from=round_model.date_from,
        date_to=round_model.date_to,
    )
