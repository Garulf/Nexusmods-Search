from __future__ import annotations

import asyncio
import re
from functools import partial
from pathlib import Path
from typing import List

import requests
from pyflowlauncher import Plugin, Result, api

from launcher import KEEP_OPEN, NexusLauncher
from nexus_api import BASE_URL, NexusAPI

FILTER_KEY = ":"
ICON = str(Path(__file__).resolve().parent.parent / "icon.png")

plugin = Plugin(launcher=NexusLauncher())
nexus = NexusAPI()


def full_query(text: str) -> str:
    keyword = plugin.launcher.action_keyword
    return f"{keyword} {text}" if keyword else text


def mod_subtitle(mod: dict) -> str:
    downloads = f"Downloads: {mod['downloads']}"
    game = nexus.game(mod["game_id"])
    return f"{game['name']} - {downloads}" if game else downloads


def mod_results(terms: str, game_id: int) -> List[Result]:
    results = []
    for mod in nexus.search(terms, game_id=game_id)["results"]:
        results.append(
            Result(
                title=mod["name"],
                subtitle=mod_subtitle(mod),
                icon=ICON,
                auto_complete_text=full_query(mod["name"]),
            ).add_action(plugin.launcher.api.open_url(f"{BASE_URL}{mod['url']}"))
        )
    return results


def game_results(text: str) -> List[Result]:
    regex = re.compile(".*?".join(re.escape(char) for char in text.replace(FILTER_KEY, "").lower()))
    return [
        Result(
            title=game["name"],
            subtitle=f"Filter Search for {game['name']} only.",
            icon=ICON,
            auto_complete_text=full_query(game["name"]),
        ).add_action(apply_filter, [game["domain_name"]])
        for game in nexus.games
        if regex.search(game["name"].lower())
    ]


def search(text: str) -> List[Result]:
    terms = text.lower()
    game_id = 0
    if FILTER_KEY in terms:
        domain_name, terms = terms.split(FILTER_KEY)[:2]
        game_id = nexus.game_id(domain_name)
    if terms:
        return mod_results(terms, game_id)
    return game_results(text)


@plugin.on_method
async def query(query: str):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(search, query))


@plugin.on_except(requests.RequestException)
def search_failed(error: requests.RequestException) -> Result:
    return Result(title="Nexus Mods search failed", subtitle=str(error), icon=ICON)


@plugin.on_method
async def apply_filter(domain_name: str):
    await plugin.launcher.api.invoke(api.change_query(full_query(f"{domain_name}{FILTER_KEY}"), True))
    return KEEP_OPEN
