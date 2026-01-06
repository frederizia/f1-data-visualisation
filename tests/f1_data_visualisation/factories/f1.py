import datetime
import random

import factory

from f1_data_visualisation.data import models
from f1_data_visualisation.domain.sessions.entities import SessionType


class Season(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Season
        sqlalchemy_session_persistence = factory.alchemy.SESSION_PERSISTENCE_FLUSH

    id = factory.Sequence(lambda n: n + 1)
    year = factory.Sequence(lambda n: 2000 + n)


class Round(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Round
        sqlalchemy_session_persistence = factory.alchemy.SESSION_PERSISTENCE_FLUSH

    id = factory.Sequence(lambda n: n + 1)
    season = factory.SubFactory(Season)
    number = factory.Sequence(lambda n: n + 1)
    country = factory.Faker("country")
    location = factory.Faker("city")
    name = factory.LazyAttribute(lambda o: f"{o.country} Grand Prix")
    date_from = factory.LazyFunction(
        lambda: datetime.datetime.now(datetime.UTC).date() - datetime.timedelta(days=2)
    )
    date_to = factory.LazyFunction(lambda: datetime.datetime.now(datetime.UTC).date())


class Session(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Session
        sqlalchemy_session_persistence = factory.alchemy.SESSION_PERSISTENCE_FLUSH

    id = factory.Sequence(lambda n: n + 1)
    round = factory.SubFactory(Round)
    type = factory.LazyFunction(lambda: random.choice(list(SessionType)).value)
    date = factory.LazyFunction(lambda: datetime.datetime.now(datetime.UTC).date())


class Driver(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Driver
        sqlalchemy_session_persistence = factory.alchemy.SESSION_PERSISTENCE_FLUSH

    id = factory.Sequence(lambda n: n + 1)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    display_name = factory.LazyAttribute(lambda o: o.first_name + o.last_name[:3])


class DriverSeason(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.DriverSeason
        sqlalchemy_session_persistence = factory.alchemy.SESSION_PERSISTENCE_FLUSH

    id = factory.Sequence(lambda n: n + 1)

    number = factory.Sequence(lambda n: n + 1)
    short_code = factory.LazyAttribute(lambda o: o.driver.last_name[:3].upper())

    driver = factory.SubFactory(Driver)

    season = factory.SubFactory(Season)
