import datetime

import attrs

from f1_data_visualisation.domain.seasons import entities as season_entities


@attrs.frozen
class Round:
    # Database ID.
    id: int
    season: season_entities.Season
    number: int
    country: str
    location: str
    name: str
    date_from: datetime.date
    date_to: datetime.date
