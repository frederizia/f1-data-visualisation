import datetime
import random

import factory

from f1_data_visualisation.data import models
from f1_data_visualisation.domain.drivers.entities import DriverSessionClassificationStatus
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


class Constructor(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Constructor
        sqlalchemy_session_persistence = factory.alchemy.SESSION_PERSISTENCE_FLUSH

    id = factory.Sequence(lambda n: n + 1)

    name = factory.LazyAttribute(lambda o: f"{factory.Faker('last_name')} Racing")


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


class DriverRaceResult(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.DriverSessionResult
        sqlalchemy_session_persistence = factory.alchemy.SESSION_PERSISTENCE_FLUSH

    id = factory.Sequence(lambda n: n + 1)

    session = factory.SubFactory(Session, type=SessionType.RACE.value)
    driver = factory.SubFactory(Driver)
    constructor = factory.SubFactory(Constructor)

    position = factory.LazyFunction(lambda: random.randint(1, 20))
    laps_completed = factory.LazyFunction(lambda: random.randint(0, 70))
    points = factory.LazyFunction(lambda: float(random.randint(0, 25)))
    classification_status = factory.LazyFunction(
        lambda: DriverSessionClassificationStatus.CLASSIFIED.value
    )
    grid_position = factory.LazyFunction(lambda: random.randint(1, 20))
    time = factory.LazyFunction(
        lambda: datetime.timedelta(
            hours=random.randint(0, 1),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
            microseconds=random.randint(0, 999999),
        ).total_seconds()
    )


class DriverQualifyingResult(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.DriverSessionResult
        sqlalchemy_session_persistence = factory.alchemy.SESSION_PERSISTENCE_FLUSH

    id = factory.Sequence(lambda n: n + 1)

    session = factory.SubFactory(Session, type=SessionType.QUALIFYING.value)
    driver = factory.SubFactory(Driver)
    constructor = factory.SubFactory(Constructor)

    position = factory.LazyFunction(lambda: random.randint(1, 20))
    q1_time = factory.LazyFunction(
        lambda: datetime.timedelta(
            hours=0,
            minutes=random.randint(0, 1),
            seconds=random.randint(0, 59),
            microseconds=random.randint(0, 999999),
        ).total_seconds()
    )
    q2_time = factory.LazyFunction(
        lambda: datetime.timedelta(
            hours=0,
            minutes=random.randint(0, 1),
            seconds=random.randint(0, 59),
            microseconds=random.randint(0, 999999),
        ).total_seconds()
    )
    q3_time = factory.LazyFunction(
        lambda: datetime.timedelta(
            hours=0,
            minutes=random.randint(0, 1),
            seconds=random.randint(0, 59),
            microseconds=random.randint(0, 999999),
        ).total_seconds()
    )
