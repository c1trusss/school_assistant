import json
from dataclasses import dataclass


@dataclass
class Product:
    name: str
    kcal: int
    proteins: int
    fats: int
    carbohydrates: int
    composition: str


class User:

    def __init__(self, user_id=0):

        self.id = user_id

        if self.id:
            with open('users.json', encoding='utf8') as file:
                data = json.load(file)

            user_info = data.get(str(self.id))

            self.name = user_info["name"]
            self.account_created = user_info["account_created"]
            self.admin = eval(user_info["admin"])
            self.sub = eval(user_info["sub"])

