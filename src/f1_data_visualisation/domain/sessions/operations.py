import datetime

from sqlalchemy import orm

from f1_data_visualisation.data import models
from f1_data_visualisation.domain.rounds import queries as round_queries
from f1_data_visualisation.domain.sessions import entities, queries


class CannotCreateSessionError(Exception):
    pass


def get_or_create_session(
    session: orm.Session,
    round_number: int,
    year: int,
    session_type: entities.SessionType,
    date: datetime.date,
) -> entities.Session:
    """
    Create a new session entry in the database, if it doesn't exist yet.
    """
    round_entity = round_queries.get_round(
        session=session,
        number=round_number,
        year=year,
    )
    if not round_entity:
        raise CannotCreateSessionError(f"Round {round_number} in {year} not found")

    existing_session = queries.get_session_by_type(
        session=session,
        round_number=round_number,
        year=year,
        session_type=session_type,
    )
    if existing_session:
        return existing_session
    session_model = models.Session(
        round_id=round_entity.id,
        type=session_type.value,
        date=date,
    )
    session.add(session_model)
    session.flush()
    return entities.Session(
        id=session_model.id,
        round=round_entity,
        type=session_type,
        date=session_model.date,
    )
