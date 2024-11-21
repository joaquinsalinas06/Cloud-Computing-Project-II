import random
from typing import Any

from data_setup.utils.shared_faker import faker
from data_setup.utils.write_to_json import write_to_json


def generate_post_data(
        rows_amount: int,
        user_keys: tuple[int, ...],
        song_keys: tuple[int, ...],
        album_keys: tuple[int, ...],
        provider_id: str,
) -> None:
    post_csv_list: list[dict[str, Any]] = []

    for post_id in range(rows_amount):
        created_at = faker.date_time_between(start_date="-1y", end_date="now").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        user_id = random.choice(user_keys)
        description = faker.text(max_nb_chars=50).replace("\n", " ")

        if random.choice([True, False]):
            song_id = random.choice(song_keys)
            album_id = None
        else:
            song_id = None
            album_id = random.choice(album_keys)

        post_csv_list.append(
            {
                "provider_id": {"S": provider_id},
                "post_id": {"N": str(post_id)},
                "user_id": {"N": str(user_id)},
                "song_id": {"N": str(song_id)},
                "album_id": {"N": str(album_id)},
                "description": {"S": description},
                "created_at": {"S": created_at}
            }
        )

    write_to_json(post_csv_list, "posts")
