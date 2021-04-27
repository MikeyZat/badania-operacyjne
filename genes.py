from functools import cached_property
from typing import Iterable, Set, List
from pprint import pprint
from random import random
import util

from main import Item


def mass_fitness(s: Iterable[Item], truck_load, car_load):
    weight = sum(item.weight for item in s)
    return weight / (car_load if weight < car_load else truck_load)


def cost_fitness(s: Iterable[Item], car_load,
                 truck_cost, car_cost):
    weight = sum(item.weight for item in s)
    return weight / (car_cost if weight < car_load else truck_cost)


class Gene:
    """Klasa genu, reprezentująca jeden transport

    # Interfejs
    ## Atrybuty
    * subset -> niemutowalny zbiór przedmiotów
    * is_by_truck -> prawda jeśli transport musi odbyć się ciężarówką, fałsz w przeciwnym wypadku
    * truck_load, car_load, truck_cost, car_cost -> dane wejściowe problemu
    * weight -> sumaryczna masa przedmiotów
    * mass_fitness -> sprawność massFitness z dokumentacji
    * cost_fitness -> sprawność costFitness z dokumentacji
    ## Metody
    * __hash__ -> żeby geny można było wrzucić do zbioru
    * __str__, __eq__ -> oczywiste
    * __len__, __iter__ -> żeby gen mógł być traktowany jak Iterable
    """

    def __init__(self, subset: Iterable[Item], truck_load,
                 car_load, truck_cost, car_cost):
        # assert truck_load > car_load
        self.subset = frozenset(subset)
        subset_mass = sum(item.weight for item in subset)
        assert subset_mass <= truck_load
        self.is_by_truck: bool = subset_mass > car_load
        self.truck_load: float = truck_load
        self.car_load: float = car_load
        self.truck_cost: float = truck_cost
        self.car_cost: float = car_cost

    @cached_property
    def weight(self) -> float:
        return sum(item.weight for item in self)

    @cached_property
    def mass_fitness(self) -> float:
        return self.weight / (self.truck_load
                              if self.is_by_truck
                              else self.car_load)

    @cached_property
    def cost_fitness(self) -> float:
        return self.weight / (self.truck_cost
                              if self.is_by_truck
                              else self.car_cost)

    def __hash__(self):
        return hash(self.subset) ^ hash('truck' if self.is_by_truck else 'car')

    def __str__(self):
        return (f'Gene with weight {self.weight} and fitness {self.mass_fitness} or {self.cost_fitness}'
                f' (transport via {"truck" if self.is_by_truck else "car"})')

    def __len__(self):
        return len(self.subset)

    def __eq__(self, other):
        if not isinstance(other, (Gene, set, list)):
            return NotImplemented
        elif isinstance(other, Gene):
            return self.subset == other.subset
        else:
            return set(self.subset) == set(other)

    def __iter__(self):
        return iter(self.subset)


class Chromosome:
    def __init__(self, partition: Iterable[Iterable[Item]],
                 truck_load, car_load, truck_cost, car_cost):
        self.genes: Set[Gene] = {
            Gene(p, truck_load, car_load, truck_cost, car_cost)
            for p in partition
        }

    def cross(self, other):
        """Operacja krzyżowania opisana w dokumentacji pod
        Algorytmy -> genetyczny -> krzyżowanie
        """
        self_genes: List[Gene] = sorted(self.genes, key=lambda g: g.cost_fitness, reverse=True)
        other_genes: List[Gene] = sorted(other.genes, key=lambda g: g.cost_fitness, reverse=True)
        common_genes: Set[Gene] = set()
        i = j = 0
        # Krok 1: szukanie identycznych genów
        while i < len(self) and j < len(other):
            i_fit = self_genes[i].cost_fitness
            j_fit = other_genes[j].cost_fitness

            if i_fit < j_fit:
                j += 1
            elif i_fit > j_fit:
                i += 1
            else:  # włączanie identycznych genów
                for gene in other_genes[j:]:
                    if gene.cost_fitness < i_fit:
                        break
                    if gene == self_genes[i]:
                        common_genes.add(gene)
                        break
                i += 1
        # Krok 2: wybieranie najlepszych genów z obu rodziców
        step_2_genes_self: List[Gene] = []
        step_2_genes_other: List[Gene] = []
        genes_from_self = (len(self) - len(common_genes)) // 2
        genes_from_other = (len(other) - len(common_genes)) // 2
        for gene in self_genes:
            if genes_from_self == 0:
                break
            if gene not in common_genes:
                step_2_genes_self.append(gene)
                genes_from_self -= 1
        for gene in other_genes:
            if genes_from_other == 0:
                break
            if gene not in common_genes:
                step_2_genes_other.append(gene)
                genes_from_other -= 1

        # przygotowanie do kroków 3-4
        all_items: Set[Item] = set(util.flatten(self_genes))
        in_no_genes: Set[Item] = (all_items - set(util.flatten(step_2_genes_self))
                                  - set(util.flatten(step_2_genes_other)))
        in_2_genes: Set[Item] = (set(util.flatten(step_2_genes_self))
                                 & set(util.flatten(step_2_genes_other)))
        # Krok 3: usuwanie przedmiotów występujących 2 razy
        chosen_seq = chosen_gene = None
        for item in in_2_genes:
            self_gene = [gene for gene in step_2_genes_self if item in gene.subset][0]
            other_gene = [gene for gene in step_2_genes_other if item in gene.subset][0]
            if (self_gene.cost_fitness < other_gene.cost_fitness
                or (self_gene.cost_fitness == other_gene.cost_fitness
                    and random() < 0.5)):
                chosen_gene = self_gene
                chosen_seq = step_2_genes_self
            else:
                chosen_gene = other_gene
                chosen_seq = step_2_genes_other
            chosen_seq.remove(chosen_gene)
            chosen_gene = Gene(set(chosen_gene)-{item}, chosen_gene.truck_load,
                               chosen_gene.car_load, chosen_gene.truck_cost,
                               chosen_gene.car_cost)
            chosen_seq.append(chosen_gene)
        # TODO Krok 4: dodawanie przedmiotów nie występujących w ogóle

    @property
    def fitness(self):
        return -sum((gene.weight for gene in self.genes))

    def __len__(self):
        return len(self.genes)


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
