from f1_data_visualisation.domain.seasons import queries
from tests.f1_data_visualisation import factories


class TestGetSeasonByYear:
    def test_returns_season_if_exists(self, db_session):
        year = 2021
        existing_season = factories.Season(year=year)

        season = queries.get_season_by_year(
            db_session=db_session,
            year=year,
        )

        assert season.year == existing_season.year

    def test_returns_none_if_season_does_not_exist(self, db_session):
        year = 1999

        season = queries.get_season_by_year(
            db_session=db_session,
            year=year,
        )

        assert season is None
