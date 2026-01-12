import enum
from pathlib import Path

import attrs
import fastf1
import pandas as pd

from f1_data_visualisation.domain.drivers import entities as driver_entities
from f1_data_visualisation.domain.rounds import entities as round_entities
from f1_data_visualisation.domain.sessions import entities as session_entities


class FastF1SessionType(enum.Enum):
    PRACTICE_1 = "FP1"
    PRACTICE_2 = "FP2"
    PRACTICE_3 = "FP3"
    SPRINT_QUALIFYING = "SQ"
    SPRINT_SHOOTOUT = "SS"
    SPRINT_RACE = "S"
    QUALIFYING = "Q"
    RACE = "R"


QUALIFYING_SESSION_TYPES: tuple[FastF1SessionType, ...] = (
    FastF1SessionType.QUALIFYING,
    FastF1SessionType.SPRINT_QUALIFYING,
    FastF1SessionType.SPRINT_SHOOTOUT,
)

RACE_SESSION_TYPES: tuple[FastF1SessionType, ...] = (
    FastF1SessionType.RACE,
    FastF1SessionType.SPRINT_RACE,
)

COMPETITIVE_SESSION_TYPES: tuple[FastF1SessionType, ...] = (
    QUALIFYING_SESSION_TYPES + RACE_SESSION_TYPES
)

SESSION_TYPE_MAPPING = {
    FastF1SessionType.PRACTICE_1: session_entities.SessionType.PRACTICE_1,
    FastF1SessionType.PRACTICE_2: session_entities.SessionType.PRACTICE_2,
    FastF1SessionType.PRACTICE_3: session_entities.SessionType.PRACTICE_3,
    FastF1SessionType.SPRINT_QUALIFYING: session_entities.SessionType.SPRINT_QUALIFYING,
    # We consider Sprint Shootout and Sprint Qualifying to be the same type of session for our purposes.
    FastF1SessionType.SPRINT_SHOOTOUT: session_entities.SessionType.SPRINT_QUALIFYING,
    FastF1SessionType.SPRINT_RACE: session_entities.SessionType.SPRINT_RACE,
    FastF1SessionType.QUALIFYING: session_entities.SessionType.QUALIFYING,
    FastF1SessionType.RACE: session_entities.SessionType.RACE,
}


@attrs.frozen
class DriverSessionResult:
    driver_season: driver_entities.DriverSeason
    driver: driver_entities.Driver
    result: driver_entities.QualifyingDriverResult | driver_entities.RaceDriverResult


@attrs.frozen
class SessionInformation:
    session: session_entities.Session
    results: list[DriverSessionResult]


class FastF1:
    def __init__(self):
        # Add some caching in case it's useful.
        cache_dir = Path(__file__).parent.parent.parent.parent.parent / ".fastf1_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Enable local cache
        fastf1.Cache.enable_cache(str(cache_dir))

    def get_all_rounds_for_season(self, year: int) -> list[round_entities.Round]:
        """
        Parse all rounds for a season from the given schedule.

        This assumes that each weekend will have 5 sessions, which is a valid assumption for recent F1 seasons.
        """
        schedule: fastf1.events.EventSchedule = fastf1.get_event_schedule(year)
        rounds = []
        for _, round_info in schedule.iterrows():
            if round_info["RoundNumber"] == 0:
                continue
            rounds.append(
                round_entities.Round(
                    number=round_info["RoundNumber"],
                    country=round_info["Country"],
                    location=round_info["Location"],
                    name=round_info["EventName"],
                    date_from=round_info["Session1Date"].date(),
                    date_to=round_info["Session5Date"].date(),
                )
            )
        return rounds

    def get_competitive_sessions_for_round(
        self, year: int, round_number: int
    ) -> list[SessionInformation]:
        """
        Get the competitive sessions for a round.

        This is where we also collect information on the driver more generally and specifically for that session and
        season.
        """
        sessions = []
        for session_type in COMPETITIVE_SESSION_TYPES:
            try:
                session = fastf1.get_session(year, round_number, session_type.value)
            except ValueError:
                # Value errors are raised for session types that don't exist for a given round (or for entirely invalid
                # session types).
                continue

            # In this project we only care about results, so we can skip loading messages and laps. We do need to load
            # telemetry as some results are not supported by the underlying APIs and are then derived from other data.
            session.load(telemetry=False)
            session_info = session_entities.Session(
                type=SESSION_TYPE_MAPPING[session_type],
                date=session.date.date(),
            )
            driver_results = []
            for driver_number in session.drivers:
                driver_session_result = session.get_driver(driver_number)
                driver = driver_entities.Driver(
                    id=None,
                    first_name=driver_session_result["FirstName"],
                    last_name=driver_session_result["LastName"],
                    display_name=driver_session_result["FullName"],
                )
                driver_season = driver_entities.DriverSeason(
                    id=None,
                    number=driver_number,
                    short_code=driver_session_result["Abbreviation"],
                )
                position = (
                    int(driver_session_result["Position"])
                    if pd.notna(driver_session_result["Position"])
                    else None
                )
                if session_type in QUALIFYING_SESSION_TYPES:
                    parsed_driver_session_result = driver_entities.QualifyingDriverResult(
                        id=None,
                        constructor=driver_entities.Constructor(
                            id=None,
                            name=driver_session_result["TeamName"],
                        ),
                        # The position is returned as a float for some reason.
                        position=position,
                        q1_time=driver_session_result["Q1"].to_pytimedelta()
                        if pd.notna(driver_session_result["Q1"])
                        else None,
                        q2_time=driver_session_result["Q2"].to_pytimedelta()
                        if pd.notna(driver_session_result["Q2"])
                        else None,
                        q3_time=driver_session_result["Q3"].to_pytimedelta()
                        if pd.notna(driver_session_result["Q3"])
                        else None,
                    )
                else:
                    parsed_driver_session_result = driver_entities.RaceDriverResult(
                        id=None,
                        constructor=driver_entities.Constructor(
                            id=None,
                            name=driver_session_result["TeamName"],
                        ),
                        position=position,
                        # Laps are returned as a float.
                        laps_completed=int(driver_session_result["Laps"]),
                        # This is a numpy.float64 so needs to converted to an inbuilt float.
                        points=float(driver_session_result["Points"]),
                        status=self._derive_classification_status(
                            driver_session_result["ClassifiedPosition"]
                        ),
                        grid_position=int(driver_session_result["GridPosition"]),
                        time=(
                            driver_session_result["Time"].to_pytimedelta()
                            if pd.notna(driver_session_result["Time"])
                            else None
                        ),
                    )
                driver_results.append(
                    DriverSessionResult(
                        driver_season=driver_season,
                        driver=driver,
                        result=parsed_driver_session_result,
                    )
                )
            sessions.append(
                SessionInformation(
                    session=session_info,
                    results=driver_results,
                )
            )

        return sessions

    def _derive_classification_status(
        self, classified_position: str
    ) -> driver_entities.DriverSessionClassificationStatus:
        """
        Derive the classification status from the classified position string.

        The classified position can either be a number (indicating the driver was classified) or a letter code.
        """
        try:
            # Any number indicates the driver was classified.
            int(classified_position)
            return driver_entities.DriverSessionClassificationStatus.CLASSIFIED  # noqa: TRY300
        except (ValueError, TypeError):
            # The classified position is not a number, so we need to map it to a status.
            status_mapping = {
                "R": driver_entities.DriverSessionClassificationStatus.RETIRED,
                "D": driver_entities.DriverSessionClassificationStatus.DISQUALIFIED,
                "N": driver_entities.DriverSessionClassificationStatus.NOT_CLASSIFIED,
                "W": driver_entities.DriverSessionClassificationStatus.WITHDRAWN,
                "E": driver_entities.DriverSessionClassificationStatus.EXCLUDED,
                "F": driver_entities.DriverSessionClassificationStatus.FAILED_TO_QUALIFY,
            }
            # As far as we know these are the only options but let's fall back to RETIRED for any unknown codes.
            return status_mapping.get(
                classified_position,
                driver_entities.DriverSessionClassificationStatus.RETIRED,
            )
