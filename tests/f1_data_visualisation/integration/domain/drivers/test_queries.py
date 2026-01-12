import pytest

from f1_data_visualisation.domain.drivers import entities, queries
from f1_data_visualisation.domain.sessions import entities as session_entities
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


class TestGetSessionResultForDriver:
    def test_returns_race_result_for_driver_if_exists(self, db_session):
        existing_result = factories.DriverRaceResult()

        result = queries.get_session_result_for_driver(
            db_session=db_session,
            session_id=existing_result.session.id,
            driver_id=existing_result.driver.id,
        )

        assert result.id == existing_result.id
        assert result.position == existing_result.position
        assert isinstance(result, entities.RaceDriverResult)

    def test_returns_qualifying_result_for_driver_if_exists(self, db_session):
        existing_result = factories.DriverQualifyingResult()

        result = queries.get_session_result_for_driver(
            db_session=db_session,
            session_id=existing_result.session.id,
            driver_id=existing_result.driver.id,
        )

        assert result.id == existing_result.id
        assert result.position == existing_result.position
        assert isinstance(result, entities.QualifyingDriverResult)

    def test_returns_none_if_session_result_for_driver_does_not_exist(self, db_session):
        driver = factories.Driver()
        session = factories.Session()

        result = queries.get_session_result_for_driver(
            db_session=db_session,
            session_id=session.id,
            driver_id=driver.id,
        )

        assert result is None

    @pytest.mark.parametrize(
        "session_type",
        [
            session_entities.SessionType.PRACTICE_1.value,
            session_entities.SessionType.PRACTICE_2.value,
            session_entities.SessionType.PRACTICE_3.value,
        ],
    )
    def test_raises_error_for_invalid_session_type(self, session_type, db_session):
        existing_session_result = factories.DriverRaceResult()
        existing_session_result.session.type = session_type

        with pytest.raises(
            queries.UnsupportedSessionTypeError,
            match=f"Session type {session_type} is not supported for driver results.",
        ):
            queries.get_session_result_for_driver(
                db_session=db_session,
                session_id=existing_session_result.session.id,
                driver_id=existing_session_result.driver.id,
            )


class TestGetDriverRaceResultsForSeason:
    def test_returns_all_race_results(self, db_session):
        driver = factories.Driver()
        season = factories.Season()
        for i in range(3):
            factories.DriverRaceResult(
                driver=driver,
                session__round__season=season,
                session__round__number=i + 1,
            )

        race_results = queries.get_driver_race_results_for_season(
            db_session=db_session, year=season.year, driver_id=driver.id
        )

        assert len(race_results) == 3

    def test_irrelevant_results_are_excluded(self, db_session):
        driver = factories.Driver()
        other_driver = factories.Driver()
        season = factories.Season(year=2022)
        other_season = factories.Season(year=2021)

        # Relevant results.
        for i in range(2):
            factories.DriverRaceResult(
                driver=driver,
                session__round__season=season,
                session__round__number=i + 1,
            )

        # Irrelevant results:
        # Results for right season but different driver.
        factories.DriverRaceResult(
            driver=other_driver,
            session__round__season=season,
        )
        # Results for right driver but different season.
        factories.DriverRaceResult(
            driver=driver,
            session__round__season=other_season,
        )
        # Result for wrong driver and wrong season.
        factories.DriverRaceResult(
            driver=other_driver,
            session__round__season=other_season,
        )
        # Quali session result for right driver and season.
        factories.DriverQualifyingResult(
            driver=driver,
            session__round__season=season,
        )

        race_results = queries.get_driver_race_results_for_season(
            db_session=db_session, year=season.year, driver_id=driver.id
        )

        assert len(race_results) == 2
