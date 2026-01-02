import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Season(Base):
    """
    Model for storing Formula 1 season information.
    """

    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column()

    rounds = relationship("Round", back_populates="season")

    def __repr__(self) -> str:
        return f"{self.year} season"


class Round(Base):
    """
    Store information about a round (race weekend).
    """

    __tablename__ = "rounds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Season this round is part of.
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    season = relationship("Season", back_populates="rounds")
    # Number between 1 and max(number of races in the season).
    number: Mapped[int] = mapped_column(nullable=False)

    country: Mapped[str] = mapped_column(nullable=False)
    location: Mapped[str] = mapped_column(nullable=False)
    # We want to store the conventional name, not the official name.
    name: Mapped[str] = mapped_column(nullable=False)
    # The last date is the date of the race itself.
    date_from: Mapped[datetime.date] = mapped_column(nullable=False)
    date_to: Mapped[datetime.date] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"{self.name} {self.season.year} (Round {self.number})"
