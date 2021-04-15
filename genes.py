from functools import cached_property
from typing import Iterable
from pprint import pprint

from main import Item


class Gene:
    def __init__(self, subset: Iterable[Item], truck_load,
                 car_load, truck_cost, car_cost):
        # assert truck_load > car_load
        self.subset = frozenset(subset)
        subset_mass = sum(item.weight for item in subset)
        assert subset_mass <= truck_load
        self.is_by_truck = subset_mass > car_load
        self.truck_load = truck_load
        self.car_load = car_load
        self.truck_cost = truck_cost
        self.car_cost = car_cost

    @cached_property
    def weight(self):
        return sum(item.weight for item in self.subset)

    @cached_property
    def fitness(self):
        return self.weight / (self.truck_load
                              if self.is_by_truck
                              else self.car_load)

    @cached_property
    def fitness_alt(self):
        return self.weight / (self.truck_cost
                              if self.is_by_truck
                              else self.car_cost)

    def __hash__(self):
        return hash(self.subset) ^ hash('truck' if self.is_by_truck else 'car')

    def __str__(self):
        return (f'Gene with weight {self.weight} and fitness {self.fitness} or {self.fitness_alt}'
                f' (transport via {"truck" if self.is_by_truck else "car"})')

    def __len__(self):
        return len(self.subset)


class Chromosome:
    def __init__(self, partition: Iterable[Iterable[Item]],
                 truck_load, car_load, truck_cost, car_cost):
        self.genes = {Gene(p, truck_load, car_load, truck_cost, car_cost)
                      for p in partition}

    @property
    def fitness(self):
        return -sum((gene.weight for gene in self.genes))


if __name__ == '__main__':
    items = {
        Item(name='chair1', weight=4),
        Item(name='chair2', weight=4),
        Item(name='chair3', weight=4),
        # Item(name='chair4', weight=4),
        # Item(name='table', weight=20),
    }
    pprint(items)
    print(Gene(items, 60, 12, 50, 15))
