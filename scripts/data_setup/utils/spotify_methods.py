from typing import Any

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

client_id = os.getenv("SPOTIFY_CLIENT_ID")

client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret
    )
)


def get_artist_id(artist_name: str):
    print(client_id)
    print(client_secret)
    results: Any = sp.search(q=f"artist:{artist_name}", type="artist")
    items = results["artists"]["items"]

    if items:
        return items[0]["id"]
    else:
        return None


def get_artist_details(artist_id: str):
    artist: Any = sp.artist(artist_id)
    image_url = artist["images"][0]["url"] if artist["images"] else None
    if len(artist["genres"]) > 0:
        genres = artist["genres"][0]
    else:
        genres = None
    return image_url, genres


def get_albums_by_artist(artist_id: str, limit=22):
    albums: Any = sp.artist_albums(artist_id, limit=limit, album_type="album,single")
    return albums["items"]


def get_tracks_by_album(album_id: str, limit=15):
    tracks: Any = sp.album_tracks(album_id, limit=limit)
    tracks_with_preview = [track for track in tracks["items"] if track["preview_url"]]
    return tracks_with_preview
