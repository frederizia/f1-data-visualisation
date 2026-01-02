import datetime

from f1_data_visualisation.domain.sessions import entities, operations
from tests.f1_data_visualisation.factories import f1 as factories


class TestGetOrCreateSession:
    def test_creates_new_session_if_not_exists(self, db_session):
        round_model = factories.Round()
        date = datetime.date(2023, 5, 25)
        session_type = entities.SessionType.PRACTICE_1

        session_entity = operations.get_or_create_session(
            session=db_session,
            round_number=round_model.number,
            year=round_model.season.year,
            session_type=session_type,
            date=date,
        )

        assert session_entity.type == session_type
        assert session_entity.date == date
        assert session_entity.round.number == round_model.number

    def test_returns_existing_session_if_exists(self, db_session):
        date = datetime.date(2023, 5, 25)
        existing_session = factories.Session(date=date)

        session_entity = operations.get_or_create_session(
            session=db_session,
            round_number=existing_session.round.number,
            year=existing_session.round.season.year,
            session_type=entities.SessionType(existing_session.type),
            date=date,
        )

        assert session_entity.id == existing_session.id
