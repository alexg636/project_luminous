import requests
import json
from bs4 import BeautifulSoup
import os
import pickle
import difflib

class SpotifyFlag():
    def __init__(self):
        self.OAuth_token = "BQD6-w9kQcAQMdWNGe63KV2NLiTbrowu8O1MBs7cQxaVoLd1UvSzDOH83J2T4xW84ipbJHR5KyH4HyvWbdLdWM4GbhZ-5rAhl9m6hMNSDB-dqr4cVTLh9qBoyryHJlV2QZ2b6WZp_orffh1NSQ"
        self.endpoint = "https://api.spotify.com/v1/me/player/"

    def currently_playing(self):
        endpoint = self.endpoint + "currently-playing?market=ES"
        response = requests.get(endpoint,
                                headers={'Authorization': 'Bearer {}'.format(self.OAuth_token)})
        response_data = response.content
        response_data = response_data.decode("utf-8")
        response_json = json.loads(response_data)
        artist = response_json['item']['artists'][0]['name']
        return artist

    def get_country(self, artist):
        endpoint = "https://www.last.fm/music/" + artist.replace(" ", "+")
        response = requests.get(endpoint)
        soup = BeautifulSoup(response.content, 'html.parser')
        metadata = soup.find('div', {"class": "col-main"}).find('div', {"class": "metadata-column"}).find_all('dd', {"class": "catalogue-metadata-description"})[1].text
        self.country = metadata.split(",")[-1].strip(" ")
        return self.country

    def get_flag(self):
        CURR_PATH = os.path.dirname(os.path.realpath(__file__))
        flagcolors = pickle.load(open(CURR_PATH + "/flagcolors.pickle", "rb"))
        storage = []
        for item in flagcolors:
            storage.append(item[0].decode("utf-8"))

        match = ''.join(difflib.get_close_matches(self.country.upper(), storage, n=1))
        location = storage.index(match)
        return flagcolors[location][0:4]

