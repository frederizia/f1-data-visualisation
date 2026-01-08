from pathlib import Path

import fastf1

from f1_data_visualisation.domain.rounds import entities as round_entities


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
        for idx, round_info in schedule.iterrows():
            if idx == 0:
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
