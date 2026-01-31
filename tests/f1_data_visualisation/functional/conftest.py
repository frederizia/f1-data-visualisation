from unittest import mock

import pytest
from fastapi.testclient import TestClient

from f1_data_visualisation.interfaces.api.main import app
from tests.f1_data_visualisation.fixtures.database import (  # noqa: F401
    db_connection,
    db_session,
    mock_get_session,
)


@pytest.fixture
def api_client(mock_get_session):  # noqa: F811
    # We need to mock the DB session here, so that we use the test DB in our calls in tests.
    # There is definitely a technically nicer way to do this using dependency injection but I'd prefer to use the
    # db session context manager in the end points.
    with mock.patch("f1_data_visualisation.data.database.get_session", mock_get_session):
        client = TestClient(app)
        yield client
