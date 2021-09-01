import webbrowser
import re
import os
import tempfile
from flox import Flox
from nexus_api import NexusAPI, BASE_URL

FILTER_KEY = ":"

class NexusmodsSearch(Flox):

    def __init__(self):
        self.NXAPI = NexusAPI()
        super().__init__()

    def get_icon(self, url, file_name):
        file_name = f"{file_name}.jpg"
        temp_path = os.path.join(tempfile.gettempdir(), "nexusmods_search")
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)
        full_path = os.path.join(temp_path, file_name)
        if not os.path.exists(full_path):
            self.NXAPI.grab_image(url, file_name, temp_path)
        return full_path

    def query(self, query):
        q = query.lower()
        game_id = 0
        if FILTER_KEY in q:
            filtered = q.split(FILTER_KEY)
            for game in self.NXAPI.games_data:
                if filtered[0] == game["domain_name"]:
                    game_id = game["id"]
            q = filtered[1]
        if len(q) > 0 and q != FILTER_KEY:
            api_results = self.NXAPI.search(q, game_id=game_id)
            for item in api_results["results"]:
                game = self.NXAPI.game(item["game_id"])
                subtitle = f"{game['name']} - Downloads: {item['downloads']}"
                # icon = self.get_icon(item["image"], item['mod_id'])
                self.add_item(
                    title=item["name"],
                    subtitle=subtitle,
                    method='open_url',
                    parameters=[item["url"]]
                )
        else:
            query = query.replace(FILTER_KEY, "")
            pattern = ".*?".join(query)
            regex = re.compile(pattern)
            for game in self.NXAPI.games_data:
                match = regex.search(game["name"].lower())
                if match:
                    self.add_item(
                        title=game["name"],
                        subtitle=f"Search for {game['name']} mods",
                        method='apply_filter',
                        parameters=[game["domain_name"]],
                        hide=True,
                        context=[game["domain_name"]],
                    )

    def context_menu(self, data):
        pass

    def apply_filter(self, filter):
        self.change_query(f"{self.user_keyword} {filter}{FILTER_KEY}", requery=True)

    def open_url(self, url):
        url = f"{BASE_URL}{url}"
        webbrowser.open(url)

if __name__ == "__main__":
    NexusmodsSearch()