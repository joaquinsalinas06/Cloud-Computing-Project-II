import random

import pandas as pd

from data_setup.utils.shared_faker import faker
from data_setup.utils.spotify_methods import *
from data_setup.utils.write_to_json import write_to_json


def generate_artists_songs_albums(
        artists_dict: dict[int, dict[str, Any]], provider_id: str
) -> tuple[tuple, tuple, tuple]:
    artists_json_list: list[dict[str, Any]] = []
    albums_json_list: list[dict[str, Any]] = []
    songs_json_list: list[dict[str, Any]] = []

    artists_keys: list[int] = []
    albums_keys: list[int] = []
    songs_keys: list[int] = []

    album_counter = 0
    song_counter = 0
    artist_count = 0

    for artist_id, artist_info in artists_dict.items():
        artist_count += 1
        print(f"Processing artist {artist_info['name']} with the id {artist_count}")
        artist_spotify_id = get_artist_id(artist_info["name"])

        if not artist_spotify_id:
            continue

        image_url, artist_genre = get_artist_details(artist_spotify_id)

        if artist_genre is None:
            artist_genre = artist_info["genre"][0]

        birth_date = faker.date_of_birth(minimum_age=20, maximum_age=70).strftime("%Y-%m-%d")
        artist_status = faker.random_element(elements=('Active', 'Inactive'))
        artist_country = faker.country()

        artists_json_list.append(
            {
                "provider_id": {"S": provider_id},
                "artist_id": {"N": str(artist_count)},
                "name": {"S": artist_info["name"]},
                "genre": {"S": artist_genre},
                "status": {"BOOL": artist_status == 'Active'},
                "birth_date": {"S": birth_date},
                "country": {"S": artist_country},
                "cover_image_url": {"S": image_url}
            }
        )
        artists_keys.append(artist_count)

        albums = get_albums_by_artist(artist_spotify_id)

        if not albums:
            continue

        for album in albums:
            album_counter += 1
            album_id = album["id"]
            album_title = album["name"]
            album_release_date = album["release_date"]
            album_cover_image_url = (
                album["images"][0]["url"] if album["images"] else None
            )
            album_link = album["external_urls"]["spotify"]

            songs = get_tracks_by_album(album_id)

            if not songs:
                album_counter -= 1
                continue

            songs_count = len(songs)
            song_ids = []

            for song in songs:
                song_counter += 1
                song_title = song["name"]
                song_duration = song["duration_ms"] // 1000
                song_release_date = album_release_date
                song_link = song["external_urls"]["spotify"]
                song_preview_url = song["preview_url"]
                genre = random.choice(artist_info["genre"])

                songs_json_list.append(
                    {
                        "provider_id": {"S": provider_id},
                        "song_id": {"N": str(song_counter)},
                        "title": {"S": song_title},
                        "genre": {"S": genre},
                        "release_date": {"S": pd.to_datetime(
                            song_release_date, errors="coerce"
                        ).strftime("%Y-%m-%d")},
                        "duration": {"S": str(song_duration // 60).zfill(2)
                                          + ":" + str(song_duration % 60).zfill(2)},
                        "cover_image_url": {"S": album_cover_image_url},
                        "times_played": {"N": str(faker.random_int(min=0, max=100000))},
                        "song_url": {"S": song_link},
                        "preview_music_url": {"S": song_preview_url},
                        "album_id": {"N": str(album_counter)},
                        "artist_id": {"N": str(artist_id)},
                    }
                )
                songs_keys.append(song_counter)
                song_ids.append(song_counter)

            albums_json_list.append(
                {
                    "provider_id": {"S": provider_id},
                    "album_id": {"N": str(album_counter)},
                    "title": {"S": album_title},
                    "release_date": {"S": pd.to_datetime(
                        album_release_date, errors="coerce"
                    ).strftime("%Y-%m-%d")},
                    "songs_count": {"N": str(songs_count)},
                    "cover_image_url": {"S": album_cover_image_url},
                    "spotify_url": {"S": album_link},
                    "artist_id": {"N": str(artist_id)},
                    "song_ids": {"NS": [str(song_id) for song_id in song_ids]}
                }
            )
            albums_keys.append(album_counter)

    write_to_json(artists_json_list, "artists")
    write_to_json(albums_json_list, "albums")
    write_to_json(songs_json_list, "songs")

    return tuple(artists_keys), tuple(albums_keys), tuple(songs_keys)
