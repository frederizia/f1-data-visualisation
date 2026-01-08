import datetime

import attrs

from f1_data_visualisation.domain.seasons import entities as season_entities


@attrs.frozen
class Round:
    number: int
    country: str
    location: str
    name: str
    date_from: datetime.date
    date_to: datetime.date


@attrs.frozen
class RoundWithSeason(Round):
    # Database ID.
    id: int
    season: season_entities.Season
