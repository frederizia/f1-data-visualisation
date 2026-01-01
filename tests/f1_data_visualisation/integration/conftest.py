import inspect

import factory.alchemy
import pytest
import sqlalchemy
from sqlalchemy import orm

from f1_data_visualisation import config
from f1_data_visualisation.data.models import Base
from tests.f1_data_visualisation import factories


# Engine that is used for all tests.
engine = sqlalchemy.create_engine(
    url=config.DATABASE_URL,
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

    session.close()
