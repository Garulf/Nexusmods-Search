import json
import os
import shutil
import requests


BASE_URL = 'https://www.nexusmods.com'
IMAGE_URL = "https://staticdelivery.nexusmods.com"
SEARCH_URL = 'https://search.nexusmods.com'
SEARCH_ENDPOINT = '/mods'
GAMES_JSON = './plugin/games.json'

class NexusAPI(object):

    def __init__(self):
        self._session = requests.Session()
        self._games_data = None

    @property
    def games_data(self):
        if self._games_data is None:
            with open(GAMES_JSON, "r") as f:
                self._games_data = json.load(f)
        return self._games_data

    def game(self, id):
        for item in self.games_data:
            if item["id"] == id:
                return item

    def request(self, method, url, endpoint, params=None, verify_ssl=True, timeout=60):
        url = f"{url}{endpoint}"
        response = self._session.request(method, url, params=params, verify=verify_ssl, timeout=timeout)
        response.raise_for_status()
        return response

    def search(self, query, game_id=0, blocked_tags=[1429,1073,1428,1040,1068], blocked_authors=None, include_adult=1):
        query = query.replace(" ", ",")
        params = (
            ('terms', query),
            ('game_id', game_id),
            ('blocked_tags', blocked_tags),
            ('blocked_authors', blocked_authors),
            ('include_adult', include_adult),
        )

        response = self.request("get", SEARCH_URL, SEARCH_ENDPOINT, params)
        return response.json()

    def grab_image(self, endpoint, filename, path=None):
        if endpoint:
            if path is None:
                path = os.getcwd()
            full_path = os.path.join(path, str(filename))
            try:
                response = self.request("get", IMAGE_URL, endpoint)
            except:
                raise
            else:
                with open(full_path, 'wb') as f:
                    f.write(response.content)   
