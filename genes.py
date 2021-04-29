from functools import cached_property
from typing import Iterable, Set, List
from sortedcontainers import SortedList
from pprint import pprint
import random
import util

from Item import Item


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
        if self.weight > self.truck_load:
            return 0
        return self.weight / (self.truck_load
                              if self.is_by_truck
                              else self.car_load)

    @cached_property
    def cost_fitness(self) -> float:
        if self.weight > self.truck_load:
            return 0
        return self.weight / self.cost

    @cached_property
    def cost(self):
        return self.truck_cost if self.is_by_truck else self.car_cost

    def __hash__(self):
        return hash(self.subset) ^ hash('truck' if self.is_by_truck else 'car')

    def __str__(self):
        return (
            f'Gene with weight {self.weight}, cost {self.cost} and fitness {self.mass_fitness} or {self.cost_fitness}'
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
        self.args = truck_load, car_load, truck_cost, car_cost
        self.genes: Set[Gene] = {Gene(p, *self.args) for p in partition}

    def cross(self, other):
        """Operacja krzyżowania opisana w dokumentacji pod
        Algorytmy -> genetyczny -> krzyżowanie
        """
        self_genes: List[Gene] = sorted(
            self.genes, key=lambda g: g.cost_fitness, reverse=True)
        other_genes: List[Gene] = sorted(
            other.genes, key=lambda g: g.cost_fitness, reverse=True)
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
            self_gene = [
                gene for gene in step_2_genes_self if item in gene.subset][0]
            other_gene = [
                gene for gene in step_2_genes_other if item in gene.subset][0]
            if (self_gene.cost_fitness < other_gene.cost_fitness
                    or (self_gene.cost_fitness == other_gene.cost_fitness
                        and random.random() < 0.5)):
                chosen_gene = self_gene
                chosen_seq = step_2_genes_self
            else:
                chosen_gene = other_gene
                chosen_seq = step_2_genes_other
            chosen_seq.remove(chosen_gene)
            chosen_gene = Gene(set(chosen_gene) - {item}, *self.args)
            chosen_seq.append(chosen_gene)
        # Krok 4: dodawanie przedmiotów nie występujących w ogóle
        genes_so_far = SortedList(step_2_genes_self + step_2_genes_other + list(common_genes),
                                  key=lambda g: -g.cost_fitness)
        for item in in_no_genes:
            already_inserted = False
            for gene in genes_so_far[::]:
                if item.weight + gene.weight > gene.truck_load:
                    continue
                new_gene_ver = Gene(list(gene) + [item], *self.args)
                if new_gene_ver.cost_fitness > gene.cost_fitness:
                    genes_so_far.remove(gene)
                    genes_so_far.add(new_gene_ver)
                    already_inserted = True
                    break
            if already_inserted:
                break
            for gene in genes_so_far[::-1]:
                if item.weight + gene.weight <= gene.truck_load:
                    new_gene_ver = Gene(list(gene) + [item], *self.args)
                    genes_so_far.remove(gene)
                    genes_so_far.add(new_gene_ver)
                    already_inserted = True
                    break
            if not already_inserted:
                genes_so_far.add(Gene([item], *self.args))

        return Chromosome(genes_so_far, *self.args)

    @property
    def fitness(self):
        """Fitness equals the whole chromosome cost"""
        return -self.cost

    @property
    def cost(self):
        """The whole chromosome cost"""
        return sum((gene.cost for gene in self.genes))

    def mutation(self):
        """delete one item from random gene and insert it in another"""
        new_genes = sorted(self.genes, key=lambda g: -g.cost_fitness)

        # pick gene from which we will delete one item
        # remove it from new genes so we will not insert the item back to it
        mutated_gene = random.choices(new_genes, weights=[g.cost_fitness for g in new_genes], k=1)[0]
        new_genes.remove(mutated_gene)

        # pick the item to be deleted and delete it from gene
        mutated_gene_items = list(mutated_gene)
        item = random.choice(mutated_gene_items)
        mutated_gene_items.remove(item)
        mutated_gene = Gene(mutated_gene_items, *self.args)

        # add item to the most efficient gene, the efficiency of which will increase as a result of such an operation
        item_added = False
        for g in new_genes:
            if g.weight + item.weight > self.args[0]:
                continue
            new_gene = Gene(list(g) + [item], *self.args)
            if new_gene.cost_fitness > g.cost_fitness:
                new_genes.remove(g)
                new_genes.append(new_gene)
                item_added = True
                break
        # if we haven't added it yet, add item to the least efficient gene that will be able to contain it
        if not item_added:
            for g in reversed(new_genes):
                if g.weight + item.weight > self.args[0]:
                    continue
                new_gene = Gene(list(g) + [item], *self.args)
                new_genes.remove(g)
                new_genes.append(new_gene)
                item_added = True
                break
        # if we haven't added it yet (no gene can contain the item) create new gene and add item to it
        if not item_added:
            new_genes.append(Gene([item], *self.args))

        # add mutated gene that we deleted earlier
        new_genes.append(mutated_gene)
        self.genes = set(new_genes)

    def __len__(self):
        return len(self.genes)

    def __str__(self):
        return f'Chromosome with current genes:\n {[str(gene) for gene in self.genes]}\n' \
               f'and fitness {self.fitness}\n'


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

