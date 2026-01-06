import pytest

from f1_data_visualisation.domain.drivers import operations
from tests.f1_data_visualisation import factories


class TestGetOrCreateDriverSeason:
    def test_creates_driver_season_if_not_exists(self, db_session):
        year = 2023
        number = 4
        driver = factories.Driver()
        factories.Season(year=year)

        driver_season = operations.get_or_create_driver_season(
            db_session=db_session,
            driver_id=driver.id,
            number=number,
            short_code="NOR",
            year=year,
        )

        assert driver_season.driver.id == driver.id
        assert driver_season.season.year == year

    def test_returns_existing_driver_season(self, db_session):
        existing_driver_season = factories.DriverSeason()

        driver_season = operations.get_or_create_driver_season(
            db_session=db_session,
            driver_id=existing_driver_season.driver.id,
            year=existing_driver_season.season.year,
            number=1,
            short_code="XYZ",
        )

        assert driver_season.id == existing_driver_season.id
        assert driver_season.driver.id == existing_driver_season.driver.id
        assert driver_season.season.year == existing_driver_season.season.year

    def test_raises_error_if_driver_does_not_exist(self, db_session):
        factories.Season(year=2022)
        non_existent_driver_id = 9999

        with pytest.raises(
            operations.UnableToCreateDriverSeasonError,
            match=f"Driver matching ID {non_existent_driver_id} does not exist.",
        ):
            operations.get_or_create_driver_season(
                db_session=db_session,
                driver_id=9999,
                number=7,
                short_code="ABC",
                year=2022,
            )

    def test_raises_error_if_season_does_not_exist(self, db_session):
        driver = factories.Driver()
        non_existent_year = 1999

        with pytest.raises(
            operations.UnableToCreateDriverSeasonError,
            match=f"Season matching year {non_existent_year} does not exist.",
        ):
            operations.get_or_create_driver_season(
                db_session=db_session,
                driver_id=driver.id,
                number=10,
                short_code="DEF",
                year=non_existent_year,
            )


class TestGetOrCreateDriver:
    def test_creates_driver_if_not_exists(self, db_session):
        first_name = "Lewis"
        last_name = "Hamilton"
        display_name = "Lewis Hamilton"

        driver = operations.get_or_create_driver(
            db_session=db_session,
            first_name=first_name,
            last_name=last_name,
            display_name=display_name,
        )

        assert driver.first_name == first_name
        assert driver.last_name == last_name
        assert driver.display_name == display_name

    def test_returns_existing_driver(self, db_session):
        existing_driver = factories.Driver()

        driver = operations.get_or_create_driver(
            db_session=db_session,
            first_name=existing_driver.first_name,
            last_name=existing_driver.last_name,
            display_name=existing_driver.display_name,
        )

        assert driver.id == existing_driver.id
        assert driver.first_name == existing_driver.first_name
        assert driver.last_name == existing_driver.last_name
        assert driver.display_name == existing_driver.display_name


class TestGetOrCreateConstructor:
    def test_returns_existing_constructor_if_exists(self, db_session):
        existing_constructor = factories.Constructor()

        constructor = operations.get_or_create_constructor(
            db_session=db_session,
            name=existing_constructor.name,
        )

        assert constructor.id == existing_constructor.id
        assert constructor.name == existing_constructor.name

    def test_creates_new_constructor_if_not_exists(self, db_session):
        constructor = operations.get_or_create_constructor(
            db_session=db_session,
            name="New Constructor",
        )

        assert constructor.id is not None
        assert constructor.name == "New Constructor"
