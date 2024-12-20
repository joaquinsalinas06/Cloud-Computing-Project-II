import random
from typing import Any

from data_setup.utils.write_to_csv import write_to_csv


def generate_user_albums_data(
        rows_amount: int, user_keys: tuple[int, ...], album_keys: tuple[int, ...], provider_id: str
):
    user_albums_csv_list: list[dict[str, Any]] = []

    for _ in range(rows_amount):
        user_id = random.choice(user_keys)
        album_id = random.choice(album_keys)

        while (album_id, user_id) in user_albums_csv_list:
            album_id = random.choice(album_keys)

        user_albums_csv_list.append({"provider_id": provider_id, "album_id": album_id, "user_id": user_id})

    write_to_csv(user_albums_csv_list, "user_albums")
