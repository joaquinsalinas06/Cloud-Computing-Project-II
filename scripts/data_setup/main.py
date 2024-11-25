from itertools import islice
import os
import glob

from data_setup.data.artists_dict import artists_dict
from data_setup.data_generation.artist_song_album import generate_artists_songs_albums
from data_setup.data_generation.playlist import generate_playlist_data
from data_setup.data_generation.post import generate_post_data
from data_setup.data_generation.user import generate_user_data
from data_setup.data_generation.comment import generate_comment_data

provider_ids = ["Spotify", "Apple", "YouTube Music"]


def clear_output_directory(directory):
    files = glob.glob(f"{directory}/*")
    for file in files:
        if os.path.isfile(file) and (file.endswith('.csv') or file.endswith('.json')):
            os.remove(file)


clear_output_directory("../output")
print("Data generation started")

for provider_id in provider_ids:
    print(f"Generating data for {provider_id}")
    sliced_artists = islice(artists_dict.items(), len(artists_dict)//7)
    sliced_artists_dict = dict(sliced_artists)
    artists_keys, albums_keys, song_keys = generate_artists_songs_albums(
        sliced_artists_dict, provider_id
    )
    user_keys = generate_user_data(3500, provider_id)
    generate_post_data(len(user_keys), user_keys, song_keys, albums_keys, provider_id)
    generate_playlist_data(len(user_keys) * 2, user_keys, song_keys, provider_id)
    generate_comment_data(len(user_keys) * 2, user_keys, song_keys, provider_id)
