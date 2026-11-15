from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

BASE_URL = "https://www.nexusmods.com"
SEARCH_URL = "https://search.nexusmods.com/mods"
GAMES_FILE = Path(__file__).resolve().parent / "games.json"
BLOCKED_TAGS = [1429, 1073, 1428, 1040, 1068]
TIMEOUT = 10


class NexusAPI:

    def __init__(self, session: Optional[requests.Session] = None, games_file: Path = GAMES_FILE) -> None:
        self._session = session or requests.Session()
        self._games_file = games_file
        self._games: Optional[List[Dict[str, Any]]] = None

    @property
    def games(self) -> List[Dict[str, Any]]:
        if self._games is None:
            self._games = json.loads(self._games_file.read_text(encoding="utf-8"))
        return self._games

    def game(self, game_id: int) -> Optional[Dict[str, Any]]:
        for game in self.games:
            if game["id"] == game_id:
                return game
        return None

    def game_id(self, domain_name: str) -> int:
        for game in self.games:
            if game["domain_name"] == domain_name:
                return game["id"]
        return 0

    def search(self, terms: str, game_id: int = 0) -> Dict[str, Any]:
        params = (
            ("terms", terms.replace(" ", ",")),
            ("game_id", game_id),
            ("blocked_tags", BLOCKED_TAGS),
            ("blocked_authors", None),
            ("include_adult", 1),
        )
        response = self._session.request("get", SEARCH_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
