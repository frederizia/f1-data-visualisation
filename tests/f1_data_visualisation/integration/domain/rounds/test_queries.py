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


class TestGetRoundsForSeason:
    def test_returns_rounds_in_order_for_season(self, db_session):
        year = 2020
        # Create rounds out of order.
        round_2 = factories.Round(number=2, season__year=year)
        round_1 = factories.Round(number=1, season__year=year)
        round_3 = factories.Round(number=3, season__year=year)

        rounds = queries.get_rounds_for_season(db_session=db_session, year=year)

        assert len(rounds) == 3
        assert rounds[0].number == round_1.number
        assert rounds[1].number == round_2.number
        assert rounds[2].number == round_3.number

    def test_returns_empty_list_if_no_rounds_for_season(self, db_session):
        year = 1995

        rounds = queries.get_rounds_for_season(db_session=db_session, year=year)

        assert rounds == []
