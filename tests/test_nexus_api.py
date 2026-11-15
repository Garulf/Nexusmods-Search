from nexus_api import NexusAPI


def test_bundled_games_listing_loads():
    nexus = NexusAPI()
    assert nexus.game_id("skyrimspecialedition") == 1704
    assert nexus.game(1704)["name"] == "Skyrim Special Edition"


def test_game_lookups(games_file):
    nexus = NexusAPI(games_file=games_file)
    assert nexus.game(1151)["domain_name"] == "fallout4"
    assert nexus.game(99999) is None
    assert nexus.game_id("fallout4") == 1151
    assert nexus.game_id("oblivion") == 0
