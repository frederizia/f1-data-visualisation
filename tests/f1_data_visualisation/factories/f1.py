import datetime

import factory

from f1_data_visualisation.data import models


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
