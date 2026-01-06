from f1_data_visualisation.domain.drivers import queries
from tests.f1_data_visualisation import factories


class TestGetDriverInformationForSeason:
    def test_returns_driver_information_for_season_if_exists(self, db_session):
        existing_driver_season = factories.DriverSeason()

        driver_season = queries.get_driver_information_for_season(
            db_session=db_session,
            driver_id=existing_driver_season.driver.id,
            year=existing_driver_season.season.year,
        )

        assert driver_season.id == existing_driver_season.id
        assert driver_season.driver.id == existing_driver_season.driver.id
        assert driver_season.season.year == existing_driver_season.season.year

    def test_returns_none_if_driver_information_for_season_does_not_exist(self, db_session):
        driver = factories.Driver()
        factories.Season(year=2021)

        driver_season = queries.get_driver_information_for_season(
            db_session=db_session,
            driver_id=driver.id,
            year=2021,
        )

        assert driver_season is None


class TestGetDriverWithSeasonInfo:
    def test_returns_driver_with_season_info_if_exists(self, db_session):
        existing_driver_season = factories.DriverSeason()

        driver_with_seasons = queries.get_driver_with_season_info(
            db_session=db_session,
            display_name=existing_driver_season.driver.display_name,
        )

        assert driver_with_seasons.id == existing_driver_season.driver.id
        assert len(driver_with_seasons.seasons) == 1
        driver_season = driver_with_seasons.seasons[0]
        assert driver_season.id == existing_driver_season.id

    def test_returns_none_if_driver_with_season_info_does_not_exist(self, db_session):
        driver = factories.Driver()

        driver_with_seasons = queries.get_driver_with_season_info(
            db_session=db_session,
            display_name=driver.display_name,
        )

        assert driver_with_seasons is None


class TestGetDriver:
    def test_returns_driver_if_exists(self, db_session):
        existing_driver = factories.Driver()

        driver = queries.get_driver(
            db_session=db_session,
            display_name=existing_driver.display_name,
        )

        assert driver.id == existing_driver.id
        assert driver.display_name == existing_driver.display_name

    def test_returns_none_if_driver_does_not_exist(self, db_session):
        driver = queries.get_driver(
            db_session=db_session,
            display_name="Non Existent Driver",
        )

        assert driver is None


class TestGetDriverById:
    def test_returns_driver_if_exists(self, db_session):
        existing_driver = factories.Driver()

        driver = queries.get_driver_by_id(
            db_session=db_session,
            database_id=existing_driver.id,
        )

        assert driver.id == existing_driver.id
        assert driver.display_name == existing_driver.display_name

    def test_returns_none_if_driver_does_not_exist(self, db_session):
        driver = queries.get_driver_by_id(
            db_session=db_session,
            database_id=9999,
        )

        assert driver is None


class TestGetConstructor:
    def test_returns_constructor_if_exists(self, db_session):
        existing_constructor = factories.Constructor()

        constructor = queries.get_constructor(
            db_session=db_session,
            name=existing_constructor.name,
        )

        assert constructor.id == existing_constructor.id
        assert constructor.name == existing_constructor.name

    def test_returns_none_if_constructor_does_not_exist(self, db_session):
        constructor = queries.get_constructor(
            db_session=db_session,
            name="Non Existent Constructor",
        )

        assert constructor is None
