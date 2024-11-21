import datetime
from typing import Any
from datetime import date, datetime

from data_setup.utils.shared_faker import faker
from data_setup.utils.write_to_json import write_to_json


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
        user_phone = faker.basic_phone_number()
        user_birth_date = faker.date_of_birth(minimum_age=10, maximum_age=50).strftime("%Y-%m-%d")
        user_gender = faker.random_element(elements=('M', 'F'))
        user_age = int((date.today() - datetime.strptime(user_birth_date, "%Y-%m-%d").date()).days // 365.25)
        active = faker.boolean()
        user_created_at = faker.date_time_this_year().strftime("%Y-%m-%d %H:%M:%S")

        users_csv_list.append(
            {
                "provider_id": {"S": user_provider_id},
                "user_id": {"N": str(user_id)},
                "email": {"S": user_email},
                "username": {"S": user_username},
                "password": {"S": user_password},
                "name": {"S": user_name},
                "last_name": {"S": user_last_name},
                "phone_number": {"S": user_phone},
                "birth_date": {"S": user_birth_date},
                "gender": {"S": user_gender},
                "age": {"N": str(user_age)},
                "active": {"BOOL": active},
                "created_at": {"S": user_created_at}
            }
        )

        user_keys.append(user_id)

    write_to_json(users_csv_list, "users")

    return tuple(user_keys)
