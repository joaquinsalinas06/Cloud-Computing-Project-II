import random

from typing import Any, List, Dict
from data_setup.utils.shared_faker import faker
from data_setup.utils.write_to_json import write_to_json


def generate_playlist_data(
        rows_amount: int, user_keys: tuple[int, ...], song_keys: tuple[int, ...], provider_id: str
):
    playlists_json_list: List[Dict[str, Any]] = []

    for _ in range(rows_amount):
        user_id = random.choice(user_keys)
        playlist_name = faker.text(max_nb_chars=50).replace("\n", " ")

        playlist_id = len(playlists_json_list) + 1
        unique_songs_ids = random.sample(song_keys, random.randint(1, (len(song_keys)//4)))

        playlists_json_list.append(
            {
                "provider_id": provider_id,
                "user_id": user_id,
                "playlist_id": playlist_id,
                "playlist_name": playlist_name,
                "song_ids": unique_songs_ids,
                "created_at": faker.date_time_between(start_date="-5y", end_date="now").strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    write_to_json(playlists_json_list, "playlists_json")
