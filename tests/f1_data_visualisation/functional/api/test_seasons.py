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
