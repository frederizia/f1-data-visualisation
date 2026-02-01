from tests.f1_data_visualisation import factories


def test_get_season_standings(api_client):
    season = factories.Season(year=2022)

    # Create 3 drivers with different points.
    first_place_driver = factories.Driver()
    second_place_driver = factories.Driver()
    third_place_driver = factories.Driver()

    # Create some rounds for the season.
    round1 = factories.Round(number=1, season=season)
    round2 = factories.Round(number=2, season=season)
    round3 = factories.Round(number=3, season=season)
    rounds = [round1, round2, round3]

    _create_race_results(driver=first_place_driver, rounds=rounds, points_multiplier=3)
    _create_race_results(driver=second_place_driver, rounds=rounds, points_multiplier=2)
    _create_race_results(driver=third_place_driver, rounds=rounds, points_multiplier=1)

    response = api_client.get("/seasons/2022/standings")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["year"] == 2022
    standings = response_data["standings"]

    assert len(standings) == 3
    assert standings[0]["position"] == 1
    assert standings[0]["points"] == 18
    assert standings[1]["position"] == 2
    assert standings[1]["points"] == 12
    assert standings[2]["position"] == 3
    assert standings[2]["points"] == 6


def _create_race_results(driver, rounds, points_multiplier: int) -> None:
    for i, round_ in enumerate(rounds):
        factories.DriverRaceResult(
            driver=driver,
            session__round=round_,
            points=(i + 1) * points_multiplier,
        )


class TestGetPointsPerRound:
    def test_get_points_per_round_only(self, api_client):
        driver = factories.Driver()
        season = factories.Season(year=2022)
        driver_season = factories.DriverSeason(driver=driver, season=season)

        for i in range(5):
            factories.DriverRaceResult(
                driver=driver,
                session__round__season=season,
                session__round__number=i + 1,
                points=i + 1,
            )

        response = api_client.get(
            f"/seasons/2022/points/{driver_season.number}?points_type=per_round"
        )

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 5
        for i, point_entry in enumerate(response_data):
            assert point_entry["round_number"] == i + 1
            assert point_entry["points"] == i + 1
            assert point_entry["accumulated_points"] is None

    def test_get_accumulative_points_only(self, api_client):
        driver = factories.Driver()
        season = factories.Season(year=2022)
        driver_season = factories.DriverSeason(driver=driver, season=season)

        for i in range(5):
            factories.DriverRaceResult(
                driver=driver,
                session__round__season=season,
                session__round__number=i + 1,
                points=i + 1,
            )

        response = api_client.get(
            f"/seasons/2022/points/{driver_season.number}?points_type=accumulative"
        )

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 5
        total_points = 0
        for i, point_entry in enumerate(response_data):
            total_points += i + 1
            assert point_entry["round_number"] == i + 1
            assert point_entry["points"] is None
            assert point_entry["accumulated_points"] == total_points

    def test_get_all_points(self, api_client):
        driver = factories.Driver()
        season = factories.Season(year=2022)
        driver_season = factories.DriverSeason(driver=driver, season=season)

        for i in range(5):
            factories.DriverRaceResult(
                driver=driver,
                session__round__season=season,
                session__round__number=i + 1,
                points=i + 1,
            )

        response = api_client.get(f"/seasons/2022/points/{driver_season.number}?points_type=all")

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 5
        total_points = 0
        for i, point_entry in enumerate(response_data):
            total_points += i + 1
            assert point_entry["round_number"] == i + 1
            assert point_entry["points"] == i + 1
            assert point_entry["accumulated_points"] == total_points

    def test_defaults_to_all_points(self, api_client):
        driver = factories.Driver()
        season = factories.Season(year=2022)
        driver_season = factories.DriverSeason(driver=driver, season=season)

        for i in range(5):
            factories.DriverRaceResult(
                driver=driver,
                session__round__season=season,
                session__round__number=i + 1,
                points=i + 1,
            )

        response = api_client.get(f"/seasons/2022/points/{driver_season.number}")

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 5
        total_points = 0
        for i, point_entry in enumerate(response_data):
            total_points += i + 1
            assert point_entry["round_number"] == i + 1
            assert point_entry["points"] == i + 1
            assert point_entry["accumulated_points"] == total_points

    def test_returns_empty_list_for_driver_with_no_results(self, api_client):
        driver = factories.Driver()
        season = factories.Season(year=2022)
        driver_season = factories.DriverSeason(driver=driver, season=season)

        response = api_client.get(f"/seasons/2022/points/{driver_season.number}")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data == []

    def test_raises_404_for_non_existent_driver(self, api_client):
        response = api_client.get("/seasons/2022/points/1")

        assert response.status_code == 404
        response_data = response.json()
        assert response_data["detail"] == "Driver not found."
