import invoke

from f1_data_visualisation.application import download


@invoke.task(help={"year": "The season year to download results for."})
def season_results(
    ctx: invoke.Context,
    year: str,  # If we set this to int, it still won't be parsed as an int.
) -> None:
    """
    Download season results data and store it in the database.
    """
    try:
        download.download_all_results_for_season(int(year))
    except Exception as e:
        raise invoke.Exit(
            f"⚠️ Failed to download results for season {year}: {e} ({type(e).__name__})"
        ) from e
