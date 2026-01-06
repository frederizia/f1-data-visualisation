import datetime

from sqlalchemy import ForeignKey, UniqueConstraint
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

    drivers = relationship("DriverSeason", back_populates="season")

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

    sessions = relationship("Session", back_populates="round")

    def __repr__(self) -> str:
        return f"{self.name} {self.season.year} (Round {self.number})"


class Session(Base):
    """
    Store information about a session (practice, qualifying, race).
    """

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Round this session is part of.
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.id"), nullable=False)
    round = relationship("Round", back_populates="sessions")

    type: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[datetime.date] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"{self.type} - {self.date}"


class Driver(Base):
    """
    Store information about a driver.
    """

    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Name information
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    # Even though in principle a display name is not unique, in practice it should be and we should have _something_
    # as a unique identifier for drivers.
    display_name: Mapped[str] = mapped_column(nullable=False, unique=True)

    # There are a few things which might change by season, so should be recorded with a temporal
    # relationship.
    seasons = relationship("DriverSeason", back_populates="driver")


class DriverSeason(Base):
    """
    Store driver information that might change between seasons.

    Reasons are as follows:
    * number: drivers might change number after winning a championship, i.e. taking the number one
        (also in the past driver numbers were determined by championship standings of the constructors)
    * short_code: this doesn't change often but it can happen, e.g. Max Verstapped changed from VES to VER
    """

    __tablename__ = "driver_seasons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    number: Mapped[int] = mapped_column(nullable=False)
    short_code: Mapped[str] = mapped_column(nullable=False)

    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    driver = relationship("Driver", back_populates="seasons")

    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    season = relationship("Season", back_populates="drivers")

    # There can only be a single driver season entry for a given driver and season.
    __table_args__ = (UniqueConstraint("driver_id", "season_id", name="uq_driver_season"),)
