from f1_data_visualisation.data import database
from f1_data_visualisation.domain.driver_stats import queries as driver_stat_queries
from f1_data_visualisation.domain.drivers import operations as driver_operations
from f1_data_visualisation.utils import event_types, logs


class UnableToUpdateDriverSeasonError(Exception):
    pass


class NoSeasonStandingsAvailableError(Exception):
    pass


def store_season_standings(
    year: int,
) -> None:
    """
    Store the total points and position for a driver in a given season.

    We retrieve all the positions and points for drivers and add them to the existing driver season records.
    """
    logs.log_event(
        event_type=event_types.STORE_DRIVER_SEASON_RESULTS_STARTED,
        year=year,
    )
    with database.get_session() as db_session:
        # Get the results for the season.
        driver_season_results = driver_stat_queries.get_season_standings(
            db_session=db_session,
            year=year,
        )
        if not driver_season_results:
            logs.log_event(
                event_type=event_types.STORE_DRIVER_SEASON_RESULTS_ERRORED,
                year=year,
            )
            raise NoSeasonStandingsAvailableError(
                f"Driver standings could not be determined for season {year}."
            )
        for result in driver_season_results:
            # Appease the type checker.
            assert result.driver.id
            try:
                driver_operations.add_points_and_positions_to_driver_season(
                    db_session=db_session,
                    year=year,
                    driver_id=result.driver.id,
                    points=result.points,
                    position=result.position,
                )
                logs.log_event(
                    event_type=event_types.STORE_DRIVER_SEASON_RESULTS_DRIVER_SAVED,
                    year=year,
                    driver=result.driver.display_name,
                    points=result.points,
                    position=result.position,
                )
            except driver_operations.UnableToUpdateDriverSeasonError as e:
                logs.log_event(
                    event_type=event_types.STORE_DRIVER_SEASON_RESULTS_DRIVER_ERRORED,
                    year=year,
                    driver=result.driver.display_name,
                )
                raise UnableToUpdateDriverSeasonError(
                    f"Failed to update driver season for driver ID {result.driver.id} in year {year}: {e}."
                ) from e
        db_session.commit()
        logs.log_event(
            event_type=event_types.STORE_DRIVER_SEASON_RESULTS_COMPLETED,
            year=year,
        )
