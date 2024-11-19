import datetime
from typing import Any
from datetime import date, datetime

from data_setup.utils.normalize_text import normalize_text
from data_setup.utils.shared_faker import faker
from data_setup.utils.write_to_csv import write_to_csv


def generate_user_data(rows_amount: int , provider_id: str) -> tuple:
    user_keys: list[int] = []
    users_csv_list: list[dict[str, Any]] = []

    for user_id in range(rows_amount):
        user_provider_id = provider_id
        user_id = user_id + 1
        user_email = faker.unique.email()
        user_username = faker.unique.user_name()
        user_password = faker.unique.password()
        user_name = faker.first_name()
        user_last_name = faker.last_name()
        user_phone = faker.phone_number()
        user_birth_date = faker.date_of_birth(minimum_age=10, maximum_age=50)
        user_gender = faker.random_element(elements=('M', 'F'))
        user_age = (date.today() - user_birth_date).days // 365.25
        active = faker.boolean()
        user_created_at = faker.date_time_this_year()
        users_csv_list.append(
            {
                "provider_id": user_provider_id,
                "user_id": user_id,
                "email": user_email,
                "username": user_username,
                "password": user_password,
                "name": user_name,
                "last_name": user_last_name,
                "phone_number": user_phone,
                "birth_date": user_birth_date,
                "gender": user_gender,
                "age": user_age,
                "active": active,
                "created_at": user_created_at
            }
        )

        user_keys.append(user_id + 1)

    write_to_csv(users_csv_list, "users")

    return tuple(user_keys)
