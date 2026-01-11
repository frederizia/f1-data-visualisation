import pytest

from f1_data_visualisation.domain.sessions import entities, queries
from tests.f1_data_visualisation import factories


class TestGetSessionByType:
    def test_returns_session_if_exists(self, db_session):
        existing_session = factories.Session()

        session_entity = queries.get_session_by_type(
            db_session=db_session,
            round_number=existing_session.round.number,
            year=existing_session.round.season.year,
            session_type=entities.SessionType(existing_session.type),
        )

        assert session_entity.type.value == existing_session.type
        assert session_entity.round.id == existing_session.round.id

    def test_returns_none_if_session_does_not_exist(self, db_session):
        round_model = factories.Round()
        session_type = entities.SessionType.RACE

        session_entity = queries.get_session_by_type(
            db_session=db_session,
            round_number=round_model.number,
            year=round_model.season.year,
            session_type=session_type,
        )

        assert session_entity is None

    def test_returns_none_if_type_does_not_match(self, db_session):
        existing_session = factories.Session(type=entities.SessionType.PRACTICE_1.value)
        different_type = entities.SessionType.QUALIFYING

        session_entity = queries.get_session_by_type(
            db_session=db_session,
            round_number=existing_session.round.number,
            year=existing_session.round.season.year,
            session_type=different_type,
        )

        assert session_entity is None


class TestGetSessionsByTypeAndYear:
    def test_returns_all_sessions_of_type_for_year(self, db_session):
        year = 2023
        session_type = entities.SessionType.PRACTICE_1

        # Create multiple rounds in the same season
        round1 = factories.Round(
            number=1,
            season__year=year,
        )
        round2 = factories.Round(
            number=2,
            season__year=year,
        )

        # Create sessions with the same type for both rounds
        factories.Session(
            round=round1,
            type=session_type.value,
        )
        factories.Session(
            round=round2,
            type=session_type.value,
        )

        sessions = queries.get_sessions_by_type_and_year(
            db_session=db_session,
            session_type=session_type.value,
            year=year,
        )

        assert len(sessions) == 2
        # The sessions are sorted by round.
        assert sessions[0].round.number == round1.number
        assert sessions[1].round.number == round2.number

    def test_returns_empty_list_if_no_sessions_found(self, db_session):
        year = 2023
        session_type = entities.SessionType.RACE

        sessions = queries.get_sessions_by_type_and_year(
            db_session=db_session,
            session_type=session_type.value,
            year=year,
        )

        assert sessions == []

    def test_returns_only_sessions_of_specified_type(self, db_session):
        year = 2023
        round_model = factories.Round(
            number=1,
            season__year=year,
        )

        # Create sessions with different types
        factories.Session(
            round=round_model,
            type=entities.SessionType.PRACTICE_1.value,
        )
        factories.Session(
            round=round_model,
            type=entities.SessionType.QUALIFYING.value,
        )

        sessions = queries.get_sessions_by_type_and_year(
            db_session=db_session,
            session_type=entities.SessionType.PRACTICE_1.value,
            year=year,
        )

        assert len(sessions) == 1
        assert sessions[0].type == entities.SessionType.PRACTICE_1


class TestGetSessionById:
    def test_returns_session_if_exists(self, db_session):
        existing_session = factories.Session()

        session_entity = queries.get_session_by_id(
            db_session=db_session,
            database_id=existing_session.id,
        )

        assert session_entity.id == existing_session.id
        assert session_entity.type.value == existing_session.type

    def test_returns_none_if_session_does_not_exist(self, db_session):
        session_entity = queries.get_session_by_id(
            db_session=db_session,
            database_id=9999,
        )

        assert session_entity is None


class TestIsSprintWeekend:
    @pytest.mark.parametrize(
        "session_type",
        [entities.SessionType.SPRINT_QUALIFYING, entities.SessionType.SPRINT_RACE],
    )
    def test_returns_true_if_there_are_sprint_sessions(self, session_type, db_session):
        # Create session and associated round and season.
        year = 2024
        round_number = 23
        factories.Session(
            type=session_type.value, round__number=round_number, round__season__year=year
        )
        is_sprint = queries.is_sprint_weekend(
            db_session=db_session, year=year, round_number=round_number
        )
        assert is_sprint

    @pytest.mark.parametrize(
        "session_type",
        [
            entities.SessionType.PRACTICE_1,
            entities.SessionType.PRACTICE_2,
            entities.SessionType.PRACTICE_3,
            entities.SessionType.QUALIFYING,
            entities.SessionType.RACE,
        ],
    )
    def test_returns_false_if_only_non_sprint_sessions(self, session_type, db_session):
        # Create session and associated round and season.
        year = 2024
        round_number = 23
        factories.Session(
            type=session_type.value, round__number=round_number, round__season__year=year
        )
        is_sprint = queries.is_sprint_weekend(
            db_session=db_session, year=year, round_number=round_number
        )
        assert not is_sprint


class TestHasSessions:
    def test_returns_true_if_sessions_exist(self, db_session):
        year = 2024
        round_number = 5
        round_model = factories.Round(
            number=round_number,
            season__year=year,
        )
        # Create two sessions.
        factories.Session(round=round_model)
        factories.Session(
            round=round_model,
        )

        has_sessions = queries.has_sessions(
            db_session=db_session, year=year, round_number=round_number
        )
        assert has_sessions

    def test_returns_false_if_no_sessions_exist(self, db_session):
        year = 2024
        round_number = 5
        # Create a round without sessions.
        factories.Round(
            number=round_number,
            season__year=year,
        )

        has_sessions = queries.has_sessions(
            db_session=db_session, year=year, round_number=round_number
        )
        assert not has_sessions

    def test_returns_false_if_round_does_not_exist(self, db_session):
        year = 2024
        round_number = 5

        has_sessions = queries.has_sessions(
            db_session=db_session, year=year, round_number=round_number
        )
        assert not has_sessions
