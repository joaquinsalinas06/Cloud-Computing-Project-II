import random
from typing import Any

from data_setup.utils.shared_faker import faker
from data_setup.utils.write_to_csv import write_to_csv


def generate_comment_data(
    rows_amount: int, user_keys: tuple[int, ...], post_keys: tuple[int, ...], provider_id: str
) -> None:
    commment_csv_list: list[dict[str, Any]] = []

    for comment_id in range(rows_amount):
        comment_id_val = comment_id + 1
        post_id = random.choice(post_keys)
        date = faker.date_between(start_date="-1y", end_date="now").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        user_id = random.choice(user_keys)
        text = faker.text(max_nb_chars=50).replace("\n", " ")
        commment_csv_list.append(
            {
                "provider_id": provider_id,
                "comment_id": comment_id_val,
                "post_id": post_id,
                "date": date,
                "user_id": user_id,
                "text": text
            }
        )


    write_to_csv(commment_csv_list, "comments")
