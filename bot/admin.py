from datetime import datetime
import json


def add_user(id: int, name: str) -> bool:

    """
    Добавляет пользователя в базу

    В качестве аргументов принимает:

    1. id - id пользователя (message.from_user.id)

    2. name - имя пользователя (message.from_user.username)

    В результате добавляет пользователя в файл users.json
    """

    user_exist = False

    user = {
        "name": name,
        "account_created": '-'.join((str(datetime.now().date())).split('-')[::-1]),
        "admin": "False",
        "sub": "True",
    }

    with open("users.json", 'r', encoding='utf8') as file:
        data = json.load(file)
        if str(id) not in data:
            data[str(id)] = user
        else:
            user_exist = True

    with open("users.json", 'w', encoding='utf8') as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)

    return user_exist