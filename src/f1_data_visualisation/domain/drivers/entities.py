import attrs

from f1_data_visualisation.domain.seasons import entities as season_entities


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
