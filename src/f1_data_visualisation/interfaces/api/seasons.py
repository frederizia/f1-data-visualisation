import enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from f1_data_visualisation.data import database
from f1_data_visualisation.domain.driver_stats import queries as driver_stat_queries
from f1_data_visualisation.domain.drivers import queries as driver_queries


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


class PointsPerRound(BaseModel):
    round_number: int
    points: float | None
    accumulated_points: float | None


class PointsType(enum.Enum):
    ACCUMULATIVE = "accumulative"
    PER_ROUND = "per_round"
    ALL = "all"


@router.get("/{year}/points/{driver_number}")
def get_driver_points(
    year: int, driver_number: int, points_type: PointsType = PointsType.ALL
) -> list[PointsPerRound]:
    with database.get_session() as db_session:
        driver = driver_queries.get_driver_by_number_for_season(
            db_session=db_session, number=driver_number, year=year
        )
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found.")
        assert driver.id is not None
        points_per_round = driver_stat_queries.get_accumulative_points_per_round_for_driver(
            db_session=db_session, driver_id=driver.id, year=year
        )
        if points_type == PointsType.ACCUMULATIVE:
            return [
                PointsPerRound(
                    round_number=round_point.round_number,
                    points=None,
                    accumulated_points=round_point.accumulated_points,
                )
                for round_point in points_per_round
            ]
        if points_type == PointsType.PER_ROUND:
            return [
                PointsPerRound(
                    round_number=round_point.round_number,
                    points=round_point.points,
                    accumulated_points=None,
                )
                for round_point in points_per_round
            ]
        return [
            PointsPerRound(
                round_number=round_point.round_number,
                points=round_point.points,
                accumulated_points=round_point.accumulated_points,
            )
            for round_point in points_per_round
        ]
