import os
import sys
import json

import requests

GAMES_JSON = "./plugin/games.json"
API_URL = "https://api.nexusmods.com/v1/games.json"

def retrieve_games(api_key):
    headers = {
    'accept': 'application/json',
    'apikey': api_key,
    }

    params = (
        ('include_unapproved', 'false'),
    )
    print("Requesting external list...")
    response = requests.get(API_URL, headers=headers, params=params)
    response.raise_for_status()
    return response

def load_games(file=GAMES_JSON):
    with open(file, "r") as f:
        return json.load(f)

def save_games(data):
    with open(GAMES_JSON, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)

def main():
    nexus_key = os.environ.get("NEXUS_KEY")
    # new_games = load_games("./scripts/test.json")
    new_games = retrieve_games(nexus_key).json()
    old_games = load_games()
    changes = 0
    for old_game in old_games:
        for new_game in new_games:
            if old_game["name"] == new_game["name"]:
                if old_game["id"] != new_game["id"] or old_game["id"] != new_game["id"]:
                    changes = changes + 1
                    print(f'[Changed] {old_game["name"]}')
                break
            removed = old_game["name"]
        else:
            changes = changes + 1
            print(f'[Removed] {removed}')
    for new_game in new_games:
        for old_game in old_games:
            if new_game["name"] == old_game["name"]:
                break
            added = new_game["name"]
        else:
            changes = changes + 1
            print(f'[Added] {added}')
    print(f'{changes} change(s) found!')
    if changes > 0:
        print("Saving changes..")
        save_games(new_games)
        sys.exit(1)
    else:
        print("Exiting...")
        sys.exit(0)





if __name__ == '__main__':
    main()