import webbrowser
import os
import tempfile
from flox import Flox
from nexus import NexusAPI, BASE_URL

class NexusmodsSearch(Flox):

    def get_icon(self, url, file_name):
        file_name = f"{file_name}.jpg"
        temp_path = os.path.join(tempfile.gettempdir(), "nexusmods_search")
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)
        full_path = os.path.join(temp_path, file_name)
        if not os.path.exists(full_path):
            NXAPI = NexusAPI()
            NXAPI.grab_image(url, file_name, temp_path)
        return full_path

    def query(self, query):
        if len(query) > 1:
            NXAPI = NexusAPI()
            api_results = NXAPI.search(query)
            for item in api_results["results"]:
                subtitle = f"{item['game_name']} - Downloads: {item['downloads']}"
                icon = self.get_icon(item["image"], item['mod_id'])
                self.add_item(
                    title=item["name"],
                    subtitle=subtitle,
                    icon=icon,
                    method='open_url',
                    parameters=[item["url"]]
                ) 
            # self.logger.info(api_results)

    def context(self, data):
        pass

    def open_url(self, url):
        url = f"{BASE_URL}{url}"
        webbrowser.open(url)

if __name__ == "__main__":
    NexusmodsSearch()