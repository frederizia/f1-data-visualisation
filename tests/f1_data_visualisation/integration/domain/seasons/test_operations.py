from f1_data_visualisation.domain.seasons import operations
from tests.f1_data_visualisation.factories import f1 as factories


class TestGetOrCreateSeason:
    def test_creates_new_season_if_not_exists(self, db_session):
        year = 2023

        season, created = operations.get_or_create_season(
            db_session=db_session,
            year=year,
        )

        assert created
        assert season.year == year

    def test_returns_existing_season_if_exists(self, db_session):
        year = 2022
        existing_season = factories.Season(year=year)

        season, created = operations.get_or_create_season(
            db_session=db_session,
            year=year,
        )

        assert not created
        assert season.id == existing_season.id
