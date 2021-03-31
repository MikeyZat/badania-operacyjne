from functools import cached_property
from typing import Set

def mass(subset):
    #TODO
    pass

class Gene:
    def __init__(self, subset: set, truck_load, car_load):
        # assert truck_load > car_load
        assert mass(subset) <= truck_load
        self.subset = frozenset(subset)
        self.is_by_truck = mass(subset) > car_load
        self.truck_load = truck_load
        self.car_load = car_load
    
    @cached_property
    def mass(self):
        return mass(self.subset)
    
    @cached_property
    def fitness(self):
        return self.mass / (self.truck_load 
                            if self.is_by_truck 
                            else self.car_load)
    
    def __hash__(self):
        return hash(self.subset) ^ hash('truck' if self.is_by_truck else 'car')
    
class Chromosome:
    def __init__(self, partition: Set[set], truck_load, car_load):
        self.genes = {Gene(p, truck_load, car_load) for p in partition}
        
    @property
    def fitness(self):
        return -sum((gene.mass for gene in self.genes))