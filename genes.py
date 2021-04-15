from functools import cached_property
from typing import Iterable, FrozenSet
from dataclasses import dataclass


__all__ = ['Item', 'Gene', 'Chromosome']


@dataclass(frozen=True)
class Item:
    name: str
    mass: float


class Gene:
    # subset: FrozenSet[Item]
    # is_by_truck: bool
    # truck_load: float
    # car_load: float

    def __init__(self, subset: Iterable[Item], truck_load, 
                 car_load, truck_cost, car_cost):
        # assert truck_load > car_load
        self.subset = frozenset(subset)
        subset_mass = sum(item.mass for item in subset)
        assert subset_mass <= truck_load
        self.is_by_truck = subset_mass > car_load
        self.truck_load = truck_load
        self.car_load = car_load
        self.truck_cost = truck_cost
        self.car_cost = car_cost

    @cached_property
    def mass(self):
        return sum(item.mass for item in self.subset)

    @cached_property
    def fitness(self):
        return self.mass / (self.truck_load
                            if self.is_by_truck
                            else self.car_load)
        
    @cached_property
    def fitness_alt(self):
        return self.mass / (self.truck_cost
                            if self.is_by_truck
                            else self.car_cost)

    def __hash__(self):
        return hash(self.subset) ^ hash('truck' if self.is_by_truck else 'car')
    
    def __str__(self):
        return f'Gene with mass {self.mass} and fitness {self.fitness}'
    
    def __len__(self):
        return len(self.subset)


class Chromosome:
    def __init__(self, partition: Iterable[Iterable[Item]], truck_load, car_load):
        self.genes = {Gene(p, truck_load, car_load) for p in partition}

    @property
    def fitness(self):
        return -sum((gene.mass for gene in self.genes))


if __name__ == '__main__':
    items = {
        Item(name='chair1', mass=4),
        Item(name='chair2', mass=4),
        Item(name='chair3', mass=4),
        Item(name='chair4', mass=4),
        Item(name='table', mass=20),
    }
    print(Gene(items, 60, 10))
    