from fastapi import APIRouter
from pydantic import BaseModel

from f1_data_visualisation.data import database
from f1_data_visualisation.domain.driver_stats import queries as driver_stat_queries


router = APIRouter()


class Driver(BaseModel):
    first_name: str
    last_name: str
    display_name: str


class DriverSeasonStanding(BaseModel):
    driver: Driver
    position: int
    points: float


class SeasonStandings(BaseModel):
    year: int
    standings: list[DriverSeasonStanding]


@router.get("/{year}/standings")
def get_season_standings(year: int) -> SeasonStandings:
    """
    Get the standings for a given season year.
    """
    with database.get_session() as db_session:
        standings = driver_stat_queries.get_season_standings(db_session=db_session, year=year)
    return SeasonStandings(
        year=year,
        standings=[
            DriverSeasonStanding(
                driver=Driver(
                    first_name=standing.driver.first_name,
                    last_name=standing.driver.last_name,
                    display_name=standing.driver.display_name,
                ),
                position=standing.position,
                points=standing.points,
            )
            for standing in standings
        ],
    )
