import datetime

from f1_data_visualisation.domain.drivers import entities as driver_entities
from f1_data_visualisation.domain.rounds import entities as round_entities
from f1_data_visualisation.domain.sessions import entities as session_entities
from f1_data_visualisation.domain.vendor_adapters import fastf1


class FakeSuccessfulFastF1(fastf1.FastF1):
    def get_all_rounds_for_season(
        self,
        year: int,
    ) -> list[round_entities.Round]:
        return [
            round_entities.Round(
                number=1,
                country="Australia",
                location="Melbourne",
                name="Australian Grand Prix",
                date_from=datetime.date(2025, 3, 14),
                date_to=datetime.date(2025, 3, 16),
            )
        ]

    def get_competitive_sessions_for_round(
        self,
        year: int,
        round_number: int,
    ) -> list[fastf1.SessionInformation]:
        # Return a sample qualifying and race with 2 drivers each. One polestting/winning driver and
        # one last-placed/retired driver.
        # Not real results again, forgive me Lance.
        return [
            fastf1.SessionInformation(
                session=session_entities.Session(
                    type=session_entities.SessionType.QUALIFYING,
                    date=datetime.date(2025, 3, 15),
                ),
                results=[
                    fastf1.DriverSessionResult(
                        driver_season=driver_entities.DriverSeason(
                            id=None,
                            number=4,
                            short_code="NOR",
                            position=None,
                            points=None,
                        ),
                        driver=driver_entities.Driver(
                            id=None,
                            first_name="Lando",
                            last_name="Norris",
                            display_name="Lando Norris",
                        ),
                        result=driver_entities.QualifyingDriverResult(
                            id=None,
                            constructor=driver_entities.Constructor(
                                id=None,
                                name="McLaren",
                            ),
                            position=1,
                            q1_time=datetime.timedelta(minutes=1, seconds=20),
                            q2_time=datetime.timedelta(minutes=1, seconds=19),
                            q3_time=datetime.timedelta(minutes=1, seconds=18),
                        ),
                    ),
                    fastf1.DriverSessionResult(
                        driver_season=driver_entities.DriverSeason(
                            id=None,
                            number=18,
                            short_code="STR",
                            position=None,
                            points=None,
                        ),
                        driver=driver_entities.Driver(
                            id=None,
                            first_name="Lance",
                            last_name="Stroll",
                            display_name="Lance Stroll",
                        ),
                        result=driver_entities.QualifyingDriverResult(
                            id=None,
                            constructor=driver_entities.Constructor(
                                id=None,
                                name="Aston Martin",
                            ),
                            position=20,
                            q1_time=datetime.timedelta(minutes=1, seconds=30),
                            q2_time=None,
                            q3_time=None,
                        ),
                    ),
                ],
            ),
            fastf1.SessionInformation(
                session=session_entities.Session(
                    type=session_entities.SessionType.RACE,
                    date=datetime.date(2025, 3, 16),
                ),
                results=[
                    fastf1.DriverSessionResult(
                        driver_season=driver_entities.DriverSeason(
                            id=None,
                            number=4,
                            short_code="NOR",
                            position=None,
                            points=None,
                        ),
                        driver=driver_entities.Driver(
                            id=None,
                            first_name="Lando",
                            last_name="Norris",
                            display_name="Lando Norris",
                        ),
                        result=driver_entities.RaceDriverResult(
                            id=None,
                            constructor=driver_entities.Constructor(
                                id=None,
                                name="McLaren",
                            ),
                            position=1,
                            laps_completed=58,
                            points=25.0,
                            status=driver_entities.DriverSessionClassificationStatus.CLASSIFIED,
                            grid_position=1,
                            time=datetime.timedelta(hours=1, minutes=30, seconds=0),
                        ),
                    ),
                    fastf1.DriverSessionResult(
                        driver_season=driver_entities.DriverSeason(
                            id=None,
                            number=18,
                            short_code="STR",
                            position=None,
                            points=None,
                        ),
                        driver=driver_entities.Driver(
                            id=None,
                            first_name="Lance",
                            last_name="Stroll",
                            display_name="Lance Stroll",
                        ),
                        result=driver_entities.RaceDriverResult(
                            id=None,
                            constructor=driver_entities.Constructor(
                                id=None,
                                name="Aston Martin",
                            ),
                            position=20,
                            laps_completed=45,
                            points=0.0,
                            status=driver_entities.DriverSessionClassificationStatus.RETIRED,
                            grid_position=20,
                            time=None,
                        ),
                    ),
                ],
            ),
        ]


class FakeFailingFastF1(fastf1.FastF1):
    def get_all_rounds_for_season(
        self,
        year: int,
    ) -> list[round_entities.Round]:
        return [
            round_entities.Round(
                number=1,
                country="Australia",
                location="Melbourne",
                name="Australian Grand Prix",
                date_from=datetime.date(2025, 3, 14),
                date_to=datetime.date(2025, 3, 16),
            )
        ]

    def get_competitive_sessions_for_round(
        self,
        year: int,
        round_number: int,
    ) -> list[fastf1.SessionInformation]:
        raise Exception("Parsing error")  # noqa: TRY002
