import datetime
import enum

import attrs

from f1_data_visualisation.domain.rounds import entities as round_entities


class SessionType(enum.Enum):
    PRACTICE_1 = "Practice 1"
    PRACTICE_2 = "Practice 2"
    PRACTICE_3 = "Practice 3"
    SPRINT_QUALIFYING = "Sprint Qualifying"
    SPRINT_RACE = "Sprint Race"
    QUALIFYING = "Qualifying"
    RACE = "Race"


@attrs.frozen
class Session:
    id: int
    round: round_entities.Round
    type: SessionType
    date: datetime.date
