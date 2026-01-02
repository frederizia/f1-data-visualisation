from f1_data_visualisation.domain.rounds import queries
from tests.f1_data_visualisation import factories


class TestGetRound:
    def test_returns_round_if_exists(self, db_session):
        year = 2021
        number = 3
        existing_round = factories.Round(
            number=number,
            season__year=year,
        )

        round_entity = queries.get_round(
            db_session=db_session,
            year=year,
            number=number,
        )

        assert round_entity.id == existing_round.id
        assert round_entity.number == existing_round.number
        assert round_entity.season.year == existing_round.season.year

    def test_returns_none_if_round_does_not_exist(self, db_session):
        year = 1999
        number = 1

        round_entity = queries.get_round(
            db_session=db_session,
            year=year,
            number=number,
        )

        assert round_entity is None

    def test_returns_none_if_only_year_matches(self, db_session):
        year = 2021
        factories.Round(number=1, season__year=year)

        round_entity = queries.get_round(
            db_session=db_session,
            year=year,
            number=2,
        )

        assert round_entity is None
