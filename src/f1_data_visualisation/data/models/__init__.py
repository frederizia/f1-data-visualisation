from .base import Base
from .f1 import Season


# We should load all our models here so that alembic can easily discover them when
# we import Base in the env.py file.
__all__ = ["Base", "Season"]
