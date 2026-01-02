import datetime

from sqlalchemy import orm

from f1_data_visualisation.data import models
from f1_data_visualisation.domain.rounds import entities, queries
from f1_data_visualisation.domain.seasons import (
    entities as season_entities,
)
from f1_data_visualisation.domain.seasons import (
    operations as season_operations,
)


def get_or_create_round(
    session: orm.Session,
    year: int,
    number: int,
    country: str,
    location: str,
    name: str,
    date_from: datetime.date,
    date_to: datetime.date,
) -> entities.Round:
    """
    Create a new round entry in the database, if it doesn't exist yet.
    """
    existing_round = queries.get_round(session=session, year=year, number=number)
    if existing_round:
        return existing_round
    season = season_operations.get_or_create_season(session=session, year=year)
    # TODO: maybe check if there are any field mismatches with existing data.
    #   At the moment we can assume we would only create each round once when we know the data is complete.
    round_model = models.Round(
        season_id=season.id,
        number=number,
        country=country,
        location=location,
        name=name,
        date_from=date_from,
        date_to=date_to,
    )
    session.add(round_model)
    session.flush()
    season_entity = season_entities.Season(id=season.id, year=season.year)
    return entities.Round(
        id=round_model.id,
        season=season_entity,
        number=round_model.number,
        country=round_model.country,
        location=round_model.location,
        name=round_model.name,
        date_from=round_model.date_from,
        date_to=round_model.date_to,
    )
