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
    id: int | None
    name: str


@attrs.frozen
class Driver:
    id: int | None
    first_name: str
    last_name: str
    display_name: str


@attrs.frozen
class DriverSeason:
    id: int | None
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
    id: int | None
    constructor: Constructor


@attrs.frozen
class RaceDriverResult(BaseDriverSessionResult):
    position: int
    laps_completed: int
    points: float
    status: DriverSessionClassificationStatus
    grid_position: int
    time: datetime.timedelta | None


@attrs.frozen
class QualifyingDriverResult(BaseDriverSessionResult):
    # Sometimes (rarely) no position is assigned, e.g. when a driver does not participate in
    # qualifying.
    position: int | None
    q1_time: datetime.timedelta | None
    q2_time: datetime.timedelta | None
    q3_time: datetime.timedelta | None
