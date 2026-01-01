import factory

from f1_data_visualisation.data import models


class Season(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Season
        sqlalchemy_session_persistence = factory.alchemy.SESSION_PERSISTENCE_FLUSH

    id = factory.Sequence(lambda n: n + 1)
    year = factory.Sequence(lambda n: 2000 + n)
