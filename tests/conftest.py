import json

import pytest
import requests

import nexusmods
from nexus_api import NexusAPI

GAMES = [
    {"id": 110, "domain_name": "skyrim", "name": "Skyrim"},
    {"id": 1704, "domain_name": "skyrimspecialedition", "name": "Skyrim Special Edition"},
    {"id": 1151, "domain_name": "fallout4", "name": "Fallout 4"},
    {"id": 3333, "domain_name": "cyberpunk2077", "name": "Cyberpunk 2077"},
]
MODS = {
    "results": [
        {"name": "SkyUI", "game_id": 1704, "downloads": 32000000, "url": "/skyrimspecialedition/mods/12604"},
        {"name": "SkyUI", "game_id": 110, "downloads": 21000000, "url": "/skyrim/mods/3863"},
    ]
}


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Server Error", response=self)


class FakeSession:
    def __init__(self, payload=None, status_code=200, error=None):
        self.payload = MODS if payload is None else payload
        self.status_code = status_code
        self.error = error
        self.calls = []

    def request(self, method, url, params=None, timeout=None):
        self.calls.append(requests.Request(method.upper(), url, params=params).prepare().url)
        if self.error is not None:
            raise self.error
        return FakeResponse(json.loads(json.dumps(self.payload)), self.status_code)


@pytest.fixture
def games_file(tmp_path):
    path = tmp_path / "games.json"
    path.write_text(json.dumps(GAMES), encoding="utf-8")
    return path


@pytest.fixture
def session():
    return FakeSession()


@pytest.fixture
def nexus(monkeypatch, session, games_file):
    fake = NexusAPI(session=session, games_file=games_file)
    monkeypatch.setattr(nexusmods, "nexus", fake)
    return fake


@pytest.fixture
def keyword():
    launcher = nexusmods.plugin.launcher
    launcher.action_keyword = "nx"
    yield launcher
    launcher.action_keyword = ""
