import datetime
import enum

import attrs

from f1_data_visualisation.domain.seasons import entities as season_entities


class DriverSessionClassificationStatus(enum.Enum):
    CLASSIFIED = "Classified"
    RETIRED = "Retired"
    DISQUALIFIED = "Disqualified"
    EXCLUDED = "Excluded"
    WITHDRAWN = "Withdrawn"
    FAILED_TO_QUALIFY = "Failed to Qualify"
    NOT_CLASSIFIED = "Not Classified"


@attrs.frozen
class Constructor:
    id: int
    name: str


@attrs.frozen
class Driver:
    id: int
    first_name: str
    last_name: str
    display_name: str


@attrs.frozen
class DriverSeason:
    id: int
    number: int
    short_code: str


@attrs.frozen
class DriverSeasonWithSeason(DriverSeason):
    season: season_entities.Season


@attrs.frozen
class DriverSeasonWithDriverAndSeason(DriverSeason):
    driver: Driver
    season: season_entities.Season


@attrs.frozen
class DriverWithSeasons(Driver):
    seasons: list[DriverSeasonWithSeason]


@attrs.frozen
class BaseDriverSessionResult:
    id: int
    constructor: Constructor
    position: int


@attrs.frozen
class RaceDriverResult(BaseDriverSessionResult):
    laps_completed: int
    points: float
    status: DriverSessionClassificationStatus
    grid_position: int
    time: datetime.time | None


@attrs.frozen
class QualifyingDriverResult(BaseDriverSessionResult):
    q1_time: datetime.time | None
    q2_time: datetime.time | None
    q3_time: datetime.time | None
