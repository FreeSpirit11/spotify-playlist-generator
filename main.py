import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint

date=input("Which year do you want to travel to? Type the date in this format YYY-MM-DD: ")
URL=f"https://www.billboard.com/charts/hot-100/{date}"

#####################SPOTIFY API###########################
#Spotipy is a Python library that provides a simple interface for interacting with the Spotify Web API.

# Spotify credentials and playlist information
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
REDIRECT_URI = "https://my_spotify_playlist.com"
SCOPE = "playlist-modify-private"
playlist_name = f"{date} Billboard 100"

# Authenticate and get user ID
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI, scope=SCOPE, show_dialog=True,
                                               cache_path="token.txt"))
user_id = sp.current_user()['id']

# Create a private playlist
playlist = sp.user_playlist_create(user_id, playlist_name, public=False, collaborative=False)
playlist_id = playlist['id']


############################WEB SCRAPING#################################
#web scraping billboard
response=requests.get(URL)
response.raise_for_status()
website_html = response.text

soup = BeautifulSoup(website_html, "html.parser")
songs_tags=soup.select(selector="li h3")

all_songs=[song.getText(strip=True) for song in songs_tags][:100]

#############################SPOTIFY API##################################

# Search for the songs in Spotify and retrieve their URIs
songs_uris=[]
for song in all_songs:
    query=f"track: {song} year: {date.split('-')[0]}"
    result=sp.search(q=query, limit=1, type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")
    else:
        songs_uris.append(uri)

sp.playlist_add_items(playlist_id, songs_uris)
