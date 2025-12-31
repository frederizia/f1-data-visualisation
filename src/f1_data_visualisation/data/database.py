import sqlalchemy
from sqlalchemy import orm

from f1_data_visualisation import config


engine = sqlalchemy.create_engine(
    config.DATABASE_URL,
    echo=False,
)


def get_session() -> orm.Session:
    session_maker = orm.sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
    return session_maker()
