import asyncio

import nexusmods
from launcher import KEEP_OPEN

SEARCH = "https://search.nexusmods.com/mods"
BLOCKED = "blocked_tags=1429&blocked_tags=1073&blocked_tags=1428&blocked_tags=1040&blocked_tags=1068"


def titles(results):
    return [result.title for result in results]


def test_search_sends_the_query_to_nexus(nexus, session):
    nexusmods.search("Sky UI")
    assert session.calls == [f"{SEARCH}?terms=sky%2Cui&game_id=0&{BLOCKED}&include_adult=1"]


def test_mod_results_keep_api_order_and_open_the_mod_page(nexus, keyword):
    results = nexusmods.search("skyui")
    assert titles(results) == ["SkyUI", "SkyUI"]
    first = results[0].to_json()
    assert first["SubTitle"] == "Skyrim Special Edition - Downloads: 32000000"
    assert first["AutoCompleteText"] == "nx SkyUI"
    assert first["IcoPath"] == nexusmods.ICON
    assert first["JsonRPCAction"] == {
        "Method": "Flow.Launcher.OpenUrl",
        "Parameters": ["https://www.nexusmods.com/skyrimspecialedition/mods/12604", False],
        "DontHideAfterAction": False,
    }


def test_game_filter_limits_the_search_to_that_game(nexus, session):
    nexusmods.search("skyrimspecialedition:skyui")
    assert session.calls == [f"{SEARCH}?terms=skyui&game_id=1704&{BLOCKED}&include_adult=1"]


def test_unknown_game_filter_searches_every_game(nexus, session):
    nexusmods.search("oblivion:skyui")
    assert "game_id=0" in session.calls[0]


def test_empty_query_lists_every_game(nexus, session):
    assert titles(nexusmods.search("")) == ["Skyrim", "Skyrim Special Edition", "Fallout 4", "Cyberpunk 2077"]
    assert session.calls == []


def test_filter_key_lists_matching_games(nexus, session):
    results = nexusmods.search("sse:")
    assert titles(results) == ["Skyrim Special Edition"]
    assert results[0].subtitle == "Filter Search for Skyrim Special Edition only."
    assert session.calls == []


def test_game_result_applies_the_filter(nexus, keyword):
    action = nexusmods.search("fo4:")[0].json_rpc_action
    assert action == {"Method": "apply_filter", "Parameters": ["fallout4"], "DontHideAfterAction": False}


def test_apply_filter_changes_the_query_and_keeps_the_window_open(keyword, monkeypatch):
    sent = []

    async def invoke(command):
        sent.append(command)

    monkeypatch.setattr(keyword.api, "invoke", invoke)
    assert asyncio.run(nexusmods.apply_filter("fallout4")) == KEEP_OPEN
    assert sent == [{"Method": "Flow.Launcher.ChangeQuery", "Parameters": ["nx fallout4:", True]}]


def test_query_handler_returns_results(nexus):
    response = asyncio.run(nexusmods.plugin._event_handler.trigger_event("query", "skyui"))
    assert [result["Title"] for result in response["Result"]] == ["SkyUI", "SkyUI"]
