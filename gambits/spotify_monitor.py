import requests
import json
from bs4 import BeautifulSoup
import pickle
import difflib
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import threading
from time import sleep
import musicbrainzngs

class SpotifyFlag(threading.Thread):
    def __init__(self):
        self.VERSION = "0.0.1"
        threading.Thread.__init__(self)
        self.kill = False
        # self.CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
        # self.CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
        # self.REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")
        # self.USERNAME = os.environ.get("SPOTIFY_USERNAME")
        self.CLIENT_ID = ""
        self.CLIENT_SECRET = ""
        self.REDIRECT_URI = "http://127.0.0.1:9090"
        self.USERNAME = "alexg636"
        self.scope = "user-read-currently-playing"
        musicbrainzngs.set_useragent("project_luminous", self.VERSION, self.USERNAME)

        self.auth()
        
    def auth(self):
        client_mgr = SpotifyClientCredentials(  
                            client_id=self.CLIENT_ID,
                            client_secret=self.CLIENT_SECRET,
                            )
        token = spotipy.util.prompt_for_user_token(
                            self.USERNAME,
                            self.scope,
                            self.CLIENT_ID,
                            self.CLIENT_SECRET,
                            self.REDIRECT_URI
                            )
        if token:
            self.sp = spotipy.Spotify(auth=token)

    def get_artist(self):
        current_track = self.sp.current_user_playing_track()
        self.artist = current_track['item']['artists'][0]['name']
        return self.artist

    def get_country(self):
        # endpoint = "https://www.last.fm/music/" + self.artist.replace(" ", "+")
        # response = requests.get(endpoint)
        # soup = BeautifulSoup(response.content, 'html.parser')
        # metadata = soup.find('div', {"class": "col-main"}).find('div', {"class": "metadata-column"}).find_all('dd', {"class": "catalogue-metadata-description"})[1].text
        # self.country = metadata.split(",")[-1].strip(" ")
        metadata = musicbrainzngs.search_artists(artist=self.artist)
        self.country = metadata['artist-list'][0]['area']['name']
        return self.country

    def get_flag(self):
        CURR_PATH = os.path.dirname(os.path.realpath(__file__))
        flagcolors = pickle.load(open(CURR_PATH + "/../serialized_objects/flagcolors.pickle", "rb"))
        storage = []
        for item in flagcolors:
            storage.append(item[0].decode("utf-8"))

        match = ''.join(difflib.get_close_matches(self.country.upper(), storage, n=1))
        location = storage.index(match)
        return flagcolors[location][0:4]

    def run(self):
        artist = ['']
        while True:
            prev_artist = self.get_artist()
            while prev_artist == self.artist:
                self.get_artist()
                sleep(1)
            print(self.get_artist())
            print(self.get_country())
            print(self.get_flag())
            

        


