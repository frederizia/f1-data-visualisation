import datetime
from unittest import mock

import pytest
import sqlalchemy

from f1_data_visualisation.application import download
from f1_data_visualisation.data import models
from tests.f1_data_visualisation import factories
from tests.f1_data_visualisation.stubs import fastf1 as fastf1_stubs


class TestDownloadAllResultsForSeason:
    def test_successfully_stores_data_in_database(
        self,
        db_session,
        mock_get_session,
    ):
        # To make the mocking a little easier, we just mock the whole fastf1 adapter.
        with mock.patch.object(download.fastf1, "FastF1") as fastf1_adapter_mock:
            fastf1_adapter_mock.return_value = fastf1_stubs.FakeSuccessfulFastF1()
            # We also need to make sure the right DB session is used in the test.
            with mock.patch(
                "f1_data_visualisation.data.database.get_session", side_effect=mock_get_session
            ):
                download.download_all_results_for_season(2025)

        # We should've created 1 season, 1 round, 2 sessions, 2 drivers, and their results.
        seasons = db_session.execute(sqlalchemy.select(models.Season)).scalars().all()
        assert len(seasons) == 1

        rounds = db_session.execute(sqlalchemy.select(models.Round)).scalars().all()
        assert len(rounds) == 1

        sessions = db_session.execute(sqlalchemy.select(models.Session)).scalars().all()
        assert len(sessions) == 2

        drivers = db_session.execute(sqlalchemy.select(models.Driver)).scalars().all()
        assert len(drivers) == 2

        results = db_session.execute(sqlalchemy.select(models.DriverSessionResult)).scalars().all()
        assert len(results) == 4

    def test_no_data_stored_if_fastf1_fails(self, db_session, mock_get_session):
        # To make the mocking a little easier, we just mock the whole fastf1 adapter.
        with mock.patch.object(download.fastf1, "FastF1") as fastf1_adapter_mock:
            fastf1_adapter_mock.return_value = fastf1_stubs.FakeFailingFastF1()
            # We also need to make sure the right DB session is used in the test.
            # Use a context manager that returns the test session but triggers a rollback on exit.
            with (
                mock.patch(
                    "f1_data_visualisation.data.database.get_session", side_effect=mock_get_session
                ),
                pytest.raises(Exception, match="Parsing error"),
            ):
                download.download_all_results_for_season(2025)

        # No data season or round data should've been stored even though the error is raised
        # in the session fetching phase.
        seasons = db_session.execute(sqlalchemy.select(models.Season)).scalars().all()
        assert len(seasons) == 0
        rounds = db_session.execute(sqlalchemy.select(models.Round)).scalars().all()
        assert len(rounds) == 0

    def test_skips_existing_rounds(self, db_session, mock_get_session):
        # Pre-create a season and round to simulate existing data.
        existing_round = factories.Round(
            number=1,
            country="Australia",
            location="Melbourne",
            name="Australian Grand Prix",
            date_from=datetime.date(2025, 3, 14),
            date_to=datetime.date(2025, 3, 16),
            season__year=2025,
        )
        existing_session = factories.Session(round=existing_round)

        # To make the mocking a little easier, we just mock the whole fastf1 adapter.
        with mock.patch.object(download.fastf1, "FastF1") as fastf1_adapter_mock:
            fastf1_adapter_mock.return_value = fastf1_stubs.FakeSuccessfulFastF1()
            # We also need to make sure the right DB session is used in the test.
            with mock.patch(
                "f1_data_visualisation.data.database.get_session", side_effect=mock_get_session
            ):
                download.download_all_results_for_season(2025)

        # We should still have only 1 season and 1 round, as the existing round should be skipped.
        seasons = db_session.execute(sqlalchemy.select(models.Season)).scalars().all()
        assert len(seasons) == 1

        rounds = db_session.execute(sqlalchemy.select(models.Round)).scalars().all()
        assert len(rounds) == 1

        # We won't have retrieved the sessions and drivers, so we should only have the pre-existing session.
        sessions = db_session.execute(sqlalchemy.select(models.Session)).scalars().all()
        assert len(sessions) == 1
        assert sessions[0].id == existing_session.id

        drivers = db_session.execute(sqlalchemy.select(models.Driver)).scalars().all()
        assert len(drivers) == 0

        results = db_session.execute(sqlalchemy.select(models.DriverSessionResult)).scalars().all()
        assert len(results) == 0
