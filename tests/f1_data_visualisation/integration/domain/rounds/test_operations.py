import datetime

from f1_data_visualisation.domain.rounds import operations
from tests.f1_data_visualisation.factories import f1 as factories


class TestGetOrCreateRound:
    def test_creates_new_round_if_not_exists(self, db_session):
        year = 2023
        number = 1
        country = "Monaco"
        location = "Monte Carlo"
        name = "Monaco Grand Prix"
        date_from = datetime.date(2023, 5, 25)
        date_to = datetime.date(2023, 5, 28)

        round_entity = operations.get_or_create_round(
            db_session=db_session,
            year=year,
            number=number,
            country=country,
            location=location,
            name=name,
            date_from=date_from,
            date_to=date_to,
        )

        assert round_entity.number == number
        assert round_entity.country == country
        assert round_entity.location == location
        assert round_entity.name == name
        assert round_entity.date_from == date_from
        assert round_entity.date_to == date_to
        assert round_entity.season.year == year

    def test_returns_existing_round_if_exists(self, db_session):
        year = 2022
        number = 5
        existing_round = factories.Round(
            number=number,
            season__year=year,
        )

        round_entity = operations.get_or_create_round(
            db_session=db_session,
            year=year,
            number=number,
            country="Test",
            location="Test",
            name="Test",
            date_from=datetime.datetime.now(datetime.UTC).date(),
            date_to=datetime.datetime.now(datetime.UTC).date(),
        )

        assert round_entity.id == existing_round.id
