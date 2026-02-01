import inspect
from contextlib import contextmanager

import factory.alchemy
import pytest
import sqlalchemy
from sqlalchemy import orm

from f1_data_visualisation.data.models import Base
from tests.f1_data_visualisation import factories


TEST_DATABASE_URL = "postgresql://postgres@localhost/f1data-test"

# Engine that is used for all tests.
engine = sqlalchemy.create_engine(
    url=TEST_DATABASE_URL,
    echo=False,
    poolclass=sqlalchemy.NullPool,
)


@pytest.fixture(scope="function")
def db_connection():
    """
    Create a single connection with a transaction for the entire test.
    """
    connection = engine.connect()

    # Start a transaction and create tables.
    transaction = connection.begin()
    Base.metadata.create_all(connection)

    yield connection

    # Clean up the connection.
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function", autouse=True)
def db_session(db_connection):
    """
    DB session for each test.

    SQLAlchemy factories need to explicitly have a session set, so we need to set it. All factories used in the same
    test need to use the same session.
    """
    session_maker = orm.sessionmaker(
        bind=db_connection,
        expire_on_commit=False,
    )
    session = session_maker()

    for _, class_ in inspect.getmembers(factories, inspect.isclass):
        if issubclass(class_, factory.alchemy.SQLAlchemyModelFactory):
            class_._meta.sqlalchemy_session = session

    yield session

    session.expire_all()
    session.close()


def _create_mock_get_session(db_session):
    @contextmanager
    def mock_get_session_impl():
        try:
            yield db_session
        except Exception:
            db_session.rollback()
            raise

    return mock_get_session_impl


@pytest.fixture(scope="function")
def mock_get_session(db_session):
    return _create_mock_get_session(db_session)
