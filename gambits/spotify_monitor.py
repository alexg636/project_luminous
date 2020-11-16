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
import socket

#TODO: Catch current playing artist
#TODO: No change when resuming song
#TODO: US state support
#TODO: Add threading support

class SpotifyFlag(threading.Thread):
    '''
    SpotifyFlag class encompasses several methods ultimately used
    to generate and direct UDP payloads to then digitally control
    individually addressable WS2812B via an ESP32 microcontroller.
    '''
    def __init__(self):
        self.VERSION = "0.0.1"
        threading.Thread.__init__(self)
        self.kill = False
        self.ESP_IP = "172.20.10.8"
        self.ESP_PORT = 9999
        self.NUM_LEDS = 54
        # self.CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
        # self.CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
        # self.REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")
        # self.USERNAME = os.environ.get("SPOTIFY_USERNAME")
        self.CLIENT_ID = "ab4bec25a891431b80d99cee7a7ca731"
        self.CLIENT_SECRET = "7130465b64fd4bc1baff96c28530eb87"
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
        try:
            self.artist = current_track['item']['artists'][0]['name']
        except TypeError:
            self.artist = None
        return self.artist

    def get_country(self):
        # endpoint = "https://www.last.fm/music/" + self.artist.replace(" ", "+")
        # response = requests.get(endpoint)
        # soup = BeautifulSoup(response.content, 'html.parser')
        # metadata = soup.find('div', {"class": "col-main"}).find('div', {"class": "metadata-column"}).find_all('dd', {"class": "catalogue-metadata-description"})[1].text
        # self.country = metadata.split(",")[-1].strip(" ")
        if self.artist != None:
            metadata = musicbrainzngs.search_artists(artist=self.artist)
            self.country = metadata['artist-list'][0]['area']['name']
        else:
            self.country = None

        return self.country

    def get_flag(self):
        if self.country != None:
            CURR_PATH = os.path.dirname(os.path.realpath(__file__))
            flagcolors = pickle.load(open(CURR_PATH + "/../serialized_objects/flagcolors.pickle", "rb"))
            storage = []
            for item in flagcolors:
                storage.append(item[0].decode("utf-8"))

            match = ''.join(difflib.get_close_matches(self.country.upper(), storage, n=1))
            location = storage.index(match)
            return flagcolors[location][0:4]
        else:
            return None

    def udp_payload(self):
        print(self.get_artist())
        print(self.get_country())
        flag = self.get_flag()
        print(flag)
        if flag != None:
            stripe_1 = [flag[1][1][0], flag[1][1][1], flag[1][1][2]]*18
            stripe_2 = [flag[2][1][0], flag[2][1][1], flag[2][1][2]]*18
            stripe_3 = [flag[3][1][0], flag[3][1][1], flag[3][1][2]]*18
            payload = [*stripe_1, *stripe_2, *stripe_3, 0]
            payload = bytearray(payload)
        else:
            payload = None
        return payload

    def send_payload(self, payload):
        if payload != None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(payload, (self.ESP_IP, self.ESP_PORT))
        else:
            print("Reported None, passing...")

    def run(self):
        artist = ['']
        while True:
            count = 0
            self.get_artist()
            while artist[0] == self.artist:
                self.get_artist()
                print("Attempt {}".format(count))
                count += 1
                sleep(1)
            udp_payload = self.udp_payload()
            self.send_payload(udp_payload)
            print("Sent payload: {}".format(udp_payload))
            artist[0] = self.artist
            
SO = SpotifyFlag()
SO.run()