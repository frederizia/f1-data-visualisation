import invoke

from f1_data_visualisation.application import season_stats
from f1_data_visualisation.utils import logs


@invoke.task(help={"year": "The season year to store overall driver standings for."})
def store_driver_standings(
    ctx: invoke.Context,
    year: str,  # If we set this to int, it still won't be parsed as an int.
) -> None:
    """
    Store overall driver standings for a given season.

    This assumes the corresponding season results have already been downloaded.
    """
    try:
        season_stats.store_season_standings(int(year))
    except Exception as e:
        raw_error_message = f"{e} ({type(e).__name__})"
        logs.error(raw_error_message)
        if isinstance(e, season_stats.NoSeasonStandingsAvailableError):
            prefix = "No season standings are available. Have you downloaded the season results?"
        elif isinstance(e, season_stats.UnableToUpdateDriverSeasonError):
            prefix = "Couldn't store all driver standings."
        else:
            prefix = "An unexpected error occurred."
        raise invoke.Exit(f"⚠️ {prefix} -- {raw_error_message}") from e
