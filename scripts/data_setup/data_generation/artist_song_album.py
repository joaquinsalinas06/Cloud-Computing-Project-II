import random

import pandas as pd

from data_setup.utils.shared_faker import faker
from data_setup.utils.spotify_methods import *
from data_setup.utils.write_to_csv import write_to_csv


def generate_artists_songs_albums(
        artists_dict: dict[int, dict[str, Any]], provider_id: str
) -> tuple[tuple, tuple, tuple]:
    artists_csv_list: list[dict[str, Any]] = []
    albums_csv_list: list[dict[str, Any]] = []
    songs_csv_list: list[dict[str, Any]] = []
    artist_songs_csv_list: list[dict[str, Any]] = []

    artists_keys: list[int] = []
    albums_keys: list[int] = []
    songs_keys: list[int] = []

    album_counter = 0
    song_counter = 0
    artist_count = 0


    num_artists_to_select = random.randint(3, 5)
    selected_artists = dict(random.sample(list(artists_dict.items()), num_artists_to_select))

    for artist_id, artist_info in selected_artists.items():
        artist_count += 1
        artist_spotify_id = get_artist_id(artist_info["name"])

        if not artist_spotify_id:
            continue

        image_url, artist_genre = get_artist_details(artist_spotify_id)

        if artist_genre is None:
            artist_genre = artist_info["genre"][0]

        birth_date = faker.date_of_birth(minimum_age=20, maximum_age=70)
        artist_status = faker.random_element(elements=('Active', 'Inactive'))
        artist_country = faker.country()

        artists_csv_list.append(
            {
                "providerId": provider_id,
                "artistId": artist_count,
                "name": artist_info["name"],
                "genre": artist_genre,
                "status": artist_status,
                "birth_date": birth_date,
                "country": artist_country,
                "coverImageURL": image_url
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

            albums_csv_list.append(
                {
                    "provider_id": provider_id,
                    "album_id": album_counter,
                    "title": album_title,
                    "releaseDate": pd.to_datetime(
                        album_release_date, errors="coerce"
                    ).strftime("%Y-%m-%d"),
                    "songsCount": songs_count,
                    "coverImageUrl": album_cover_image_url,
                    "spotifyUrl": album_link,
                    "artistId": artist_id
                }

            )
            albums_keys.append(album_counter)

            for song in songs:
                song_counter += 1
                song_title = song["name"]
                song_duration = song["duration_ms"] // 1000
                song_release_date = album_release_date
                song_link = song["external_urls"]["spotify"]
                song_preview_url = song["preview_url"]
                genre = random.choice(artist_info["genre"])

                songs_csv_list.append(
                    {
                        "provider_id": provider_id,
                        "song_id": song_counter,
                        "title": song_title,
                        "genre": genre,
                        "releaseDate": pd.to_datetime(
                            song_release_date, errors="coerce"
                        ).strftime("%Y-%m-%d"),
                        "duration": str(song_duration // 60).zfill(2)
                                    + ":"
                                    + str(song_duration % 60).zfill(2),
                        "coverImageURL": album_cover_image_url,
                        "timesPlayed": faker.random_int(min=0, max=100000),
                        "musicURL": song_link,
                        "previewMusicURL": song_preview_url,
                        "albumId": album_counter,
                    }

                )
                songs_keys.append(song_counter)

                artist_songs_csv_list.append(
                    {
                        "artist_id": artist_id,
                        "song_id": song_counter,
                    }
                )

    write_to_csv(artists_csv_list, "artists")
    write_to_csv(albums_csv_list, "albums")
    write_to_csv(songs_csv_list, "songs")
    write_to_csv(artist_songs_csv_list, "artist_songs")

    return tuple(artists_keys), tuple(albums_keys), tuple(songs_keys)
