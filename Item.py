import dataclasses
import json


@dataclasses.dataclass(order=True, frozen=True)
class Item:
    weight: float
    name: str = dataclasses.field(default='')

    def __sub__(self, other):
        return self.weight - other

    def __add__(self, other):
        return self.weight + other

    def __str__(self):
        return f'{self.name}: {self.weight}'

    @staticmethod
    def from_json(path: str):
        """Wczytuje plik jako JSON i tworzy z niego listę przedmiotów"""
        with open(path) as fin:
            ret = json.load(fin)
        return (
            [Item(**kwargs) for kwargs in ret['items']],
            ret['truck_load'], ret['car_load'],
            ret['truck_cost'], ret['car_cost']
        )

