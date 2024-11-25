import random
from typing import Any

from data_setup.utils.shared_faker import faker
from data_setup.utils.write_to_json import write_to_json


def generate_comment_data(
        rows_amount: int, user_keys: tuple[int, ...], post_keys: tuple[int, ...], provider_id: str
) -> None:
    comment_csv_list: list[dict[str, Any]] = []

    for comment_id in range(rows_amount):
        comment_id_val = comment_id + 1
        post_id = random.choice(post_keys)
        date = faker.date_between(start_date="-1y", end_date="now").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        user_id = random.choice(user_keys)
        text = faker.text(max_nb_chars=50).replace("\n", " ")
        comment_csv_list.append(
            {
                "provider_id": {"S": provider_id},
                "comment_id": {"N": str(comment_id_val)},
                "post_id": {"N": str(post_id)},
                "date": {"S": date},
                "user_id": {"N": str(user_id)},
                "text": {"S": text}
            }
        )

    write_to_json(comment_csv_list, "comments")
