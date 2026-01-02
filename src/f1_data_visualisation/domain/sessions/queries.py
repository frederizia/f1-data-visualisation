import sqlalchemy
from sqlalchemy import orm

from f1_data_visualisation.data import models
from f1_data_visualisation.domain.rounds import entities as round_entities
from f1_data_visualisation.domain.seasons import entities as season_entities
from f1_data_visualisation.domain.sessions import entities


def get_session_by_type(
    db_session: orm.Session,
    round_number: int,
    year: int,
    session_type: entities.SessionType,
) -> entities.Session | None:
    """
    Retrieve a session by round, year, and type.

    There is only ever one session of each type per round.
    """
    query = (
        sqlalchemy.select(models.Session)
        .join(models.Round)
        .join(models.Season)
        .filter(
            models.Round.number == round_number,
            models.Season.year == year,
            models.Session.type == session_type.value,
        )
    )
    try:
        session_model = db_session.execute(query).scalars().one()
    except sqlalchemy.exc.NoResultFound:  # type: ignore[possibly-missing-attribute]
        return None
    round_entity = round_entities.Round(
        id=session_model.round.id,
        season=season_entities.Season(
            id=session_model.round.season.id, year=session_model.round.season.year
        ),
        number=session_model.round.number,
        country=session_model.round.country,
        location=session_model.round.location,
        name=session_model.round.name,
        date_from=session_model.round.date_from,
        date_to=session_model.round.date_to,
    )
    return entities.Session(
        id=session_model.id,
        round=round_entity,
        type=entities.SessionType(session_model.type),
        date=session_model.date,
    )


def get_sessions_by_type_and_year(
    db_session: orm.Session,
    session_type: str,
    year: int,
) -> list[entities.Session]:
    """
    Retrieve all sessions of a given type for a given year.
    """
    query = (
        sqlalchemy.select(models.Session)
        .join(models.Round)
        .join(models.Season)
        .filter(
            models.Session.type == session_type,
            models.Season.year == year,
        )
        .order_by(models.Round.number)
    )
    session_models = db_session.execute(query).scalars().all()
    return [
        entities.Session(
            id=session_model.id,
            round=round_entities.Round(
                id=session_model.round.id,
                season=season_entities.Season(
                    id=session_model.round.season.id,
                    year=session_model.round.season.year,
                ),
                number=session_model.round.number,
                country=session_model.round.country,
                location=session_model.round.location,
                name=session_model.round.name,
                date_from=session_model.round.date_from,
                date_to=session_model.round.date_to,
            ),
            type=entities.SessionType(session_model.type),
            date=session_model.date,
        )
        for session_model in session_models
    ]
