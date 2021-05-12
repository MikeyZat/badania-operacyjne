from functools import cached_property
from typing import Iterable, Set, List
from sortedcontainers import SortedList
from pprint import pprint
import random
import util
import logging
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
            f' (transport via {"truck" if self.is_by_truck else "car"})'
        )

    def __len__(self):
        return len(self.subset)

    def __eq__(self, other):
        if not isinstance(other, (Gene, set, list)):
            return NotImplemented
        elif isinstance(other, Gene):
            return self.subset == other.subset
        else:
            return set(self.subset) == set(other)

    def __repr__(self):
        return (
            f'Gene({repr(set(self.subset))}, {self.truck_load}, '
            f'{self.car_load}, {self.truck_cost}, {self.car_cost})'
        )

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
        try:
            assert isinstance(other, Chromosome)
            assert self.all_items() == other.all_items()
            logging.debug('Starting crossing algorithm')
        except AssertionError:
            logging.critical(f'''Differing chromosomes:
    {repr(self)}
    and
    {repr(other)}''')
            raise SystemExit(1)
        try:
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
                                      - set(util.flatten(step_2_genes_other))
                                      - set(util.flatten(common_genes)))
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
                    continue
                for gene in genes_so_far[::-1]:
                    if item.weight + gene.weight <= gene.truck_load:
                        new_gene_ver = Gene(list(gene) + [item], *self.args)
                        genes_so_far.remove(gene)
                        genes_so_far.add(new_gene_ver)
                        already_inserted = True
                        break
                if not already_inserted:
                    genes_so_far.add(Gene([item], *self.args))

            ret = Chromosome(genes_so_far, *self.args)
        except Exception:
            logging.critical(f'''Crossing
    {repr(self)}
    and
    {repr(other)}
    encountered an unexpected error''')
            raise SystemExit(1)
        if self.all_items() == ret.all_items():
            logging.debug('Crossing success')
            return ret
        else:
            logging.critical(f'''crossing error
    {repr(self)}
    and
    {repr(other)}
    produced erroneous child
    {repr(ret)} 
    ''')
            raise SystemExit(1)

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

    def __iter__(self):
        return iter(self.genes)

    def all_items(self):
        return set(util.flatten(self))

    def __repr__(self):
        return f'Chromosome({repr([set(gene) for gene in self.genes])}, {repr(self.args)[1:-1]})'


if __name__ == '__main__':
    chromosome1 = Chromosome([{Item(weight=6.96, name='rusty nail'), Item(weight=6.06, name='cup'), Item(weight=6.07, name='bookmark'), Item(weight=8.78, name='letter opener'), Item(weight=1.85, name='jar of pickles'), Item(weight=10.28, name='multitool')}, {Item(weight=17.43, name='grid paper'), Item(weight=4.46, name='soap'), Item(weight=18.11, name='bell')}, {Item(weight=9.13, name='canteen')}, {Item(weight=1.08, name='handful of change'), Item(weight=9.29, name='light bulb'), Item(weight=13.35, name='statuette'), Item(weight=9.08, name='incense holder'), Item(weight=7.2, name='shark')}, {Item(weight=17.01, name='plush pony'), Item(weight=3.17, name='tissue box'), Item(weight=8.24, name='chair'), Item(weight=9.4, name='can of beans')}, {Item(weight=13.66, name='beaded bracelet'), Item(weight=1.99, name='martini glass'), Item(weight=16.4, name='class ring'), Item(weight=7.95, name='bottle of nail polish')}, {Item(weight=13.81, name='plush dog'), Item(weight=10.29, name='rabbit'), Item(weight=14.57, name='roll of toilet paper')}, {Item(weight=8.18, name='bananas'), Item(weight=8.11, name='zebra'), Item(weight=18.05, name='shawl')}, {Item(weight=12.75, name='box of tissues'), Item(weight=11.43, name='shoes'), Item(weight=14.49, name='cars')}, {Item(weight=14.38, name='tea cup'), Item(weight=7.97, name='bow tie'), Item(weight=9.11, name='zipper'), Item(weight=6.88, name='tv')}, {Item(weight=6.58, name='CD'), Item(weight=3.78, name='door'), Item(weight=8.84, name='ring'), Item(weight=12.03, name='spoon'), Item(weight=8.28, name='socks')}, {Item(weight=9.15, name='bottle of syrup'), Item(weight=7.15, name='craft book'), Item(weight=9.39, name='egg'), Item(weight=6.25, name='roll of stickers'), Item(weight=6.99, name='candle')}, {Item(weight=19.54, name='book of matches'), Item(weight=19.36, name='box'), Item(weight=1.1, name='hair clip')}, {Item(weight=13.83, name='plush rabbit'), Item(weight=4.04, name='bottle of perfume'), Item(weight=5.39, name='lemon'), Item(weight=16.74, name='game cartridge')}, {Item(weight=5.06, name='stick of incense'), Item(weight=15.8, name='milk'), Item(weight=13.4, name='pair of scissors')}, {Item(weight=1.4, name='pair of glasses'), Item(weight=7.6, name='soccer ball'), Item(weight=2.02, name='tennis ball'), Item(weight=13.29, name='postage stamp'), Item(weight=15.56, name='carrots')}, {Item(weight=17.0, name='laser pointer'), Item(weight=12.74, name='bonesaw'), Item(weight=4.78, name='carton of ice cream'), Item(weight=1.71, name='safety pin')}, {Item(weight=16.37, name='egg beater'), Item(weight=6.53, name='sheet of paper'), Item(weight=17.1, name='house')}, {Item(weight=17.28, name='pasta strainer'), Item(weight=11.49, name='marble'), Item(weight=11.23, name='handheld game system')}, {Item(weight=18.3, name='quilt'), Item(weight=2.71, name='straw'), Item(weight=18.99, name='flashlight')}, {Item(weight=13.47, name='bottle of water'), Item(weight=19.7, name='pearl necklace'), Item(weight=6.83, name='hair pin')}, {Item(weight=10.56, name='cat'), Item(weight=15.67, name='tooth pick'), Item(weight=8.41, name='scotch tape'), Item(weight=3.29, name='whip')}, {Item(weight=4.29, name='mirror'), Item(weight=1.26, name='dagger'), Item(weight=3.45, name='steak knife'), Item(weight=4.43, name='button'), Item(weight=5.0, name='spectacles'), Item(weight=2.44, name='washcloth'), Item(weight=17.45, name='candlestick')}, {Item(weight=2.35, name='empty tin can'), Item(weight=17.71, name='pair of handcuffs'), Item(weight=17.83, name='Christmas ornament'), Item(weight=2.11, name='can of whipped cream')}, {Item(weight=13.24, name='spatula'), Item(weight=19.34, name='toothpaste')}, {Item(weight=16.51, name='hand bag'), Item(weight=3.8, name='pair of earrings'), Item(weight=19.69, name='map')}, {Item(weight=15.0, name='lace'), Item(weight=16.27, name='lip gloss'), Item(weight=8.63, name='fork')}], 40, 10, 50, 15)

    chromosome2 = Chromosome([{Item(weight=8.63, name='fork'), Item(weight=13.29, name='postage stamp'), Item(weight=10.29, name='rabbit'), Item(weight=7.2, name='shark')}, {Item(weight=4.29, name='mirror'), Item(weight=16.37, name='egg beater'), Item(weight=19.34, name='toothpaste')}, {Item(weight=13.81, name='plush dog'), Item(weight=8.11, name='zebra'), Item(weight=18.05, name='shawl')}, {Item(weight=17.0, name='laser pointer'), Item(weight=1.08, name='handful of change'), Item(weight=6.07, name='bookmark'), Item(weight=14.38, name='tea cup')}, {Item(weight=1.4, name='pair of glasses'), Item(weight=15.8, name='milk'), Item(weight=14.49, name='cars'), Item(weight=6.53, name='sheet of paper')}, {Item(weight=17.43, name='grid paper'), Item(weight=6.06, name='cup'), Item(weight=16.51, name='hand bag')}, {Item(weight=6.58, name='CD')}, {Item(weight=6.99, name='candle'), Item(weight=16.27, name='lip gloss'), Item(weight=15.56, name='carrots'), Item(weight=1.1, name='hair clip')}, {Item(weight=9.15, name='bottle of syrup'), Item(weight=12.74, name='bonesaw'), Item(weight=18.11, name='bell')}, {Item(weight=16.74, name='game cartridge'), Item(weight=13.83, name='plush rabbit'), Item(weight=5.39, name='lemon'), Item(weight=4.04, name='bottle of perfume')}, {Item(weight=10.56, name='cat'), Item(weight=13.4, name='pair of scissors'), Item(weight=2.11, name='can of whipped cream'), Item(weight=3.78, name='door'), Item(weight=9.13, name='canteen')}, {Item(weight=2.35, name='empty tin can'), Item(weight=3.8, name='pair of earrings'), Item(weight=11.43, name='shoes'), Item(weight=12.75, name='box of tissues'), Item(weight=9.08, name='incense holder')}, {Item(weight=17.28, name='pasta strainer'), Item(weight=11.49, name='marble'), Item(weight=11.23, name='handheld game system')}, {Item(weight=18.3, name='quilt'), Item(weight=2.71, name='straw'), Item(weight=18.99, name='flashlight')}, {Item(weight=15.67, name='tooth pick'), Item(weight=6.88, name='tv'), Item(weight=17.45, name='candlestick')}, {Item(weight=4.43, name='button'), Item(weight=10.28, name='multitool'), Item(weight=14.57, name='roll of toilet paper'), Item(weight=7.95, name='bottle of nail polish')}, {Item(weight=19.69, name='map'), Item(weight=8.28, name='socks'), Item(weight=12.03, name='spoon')}, {Item(weight=6.25, name='roll of stickers'), Item(weight=8.41, name='scotch tape'), Item(weight=8.24, name='chair'), Item(weight=17.1, name='house')}, {Item(weight=15.0, name='lace'), Item(weight=19.54, name='book of matches'), Item(weight=3.45, name='steak knife'), Item(weight=1.99, name='martini glass')}, {Item(weight=13.66, name='beaded bracelet'), Item(weight=2.02, name='tennis ball'), Item(weight=4.78, name='carton of ice cream'), Item(weight=1.71, name='safety pin'), Item(weight=17.71, name='pair of handcuffs')}, {Item(weight=5.06, name='stick of incense'), Item(weight=13.35, name='statuette'), Item(weight=13.47, name='bottle of water'), Item(weight=6.83, name='hair pin')}, {Item(weight=6.96, name='rusty nail'), Item(weight=9.29, name='light bulb'), Item(weight=9.11, name='zipper'), Item(weight=8.18, name='bananas'), Item(weight=3.17, name='tissue box'), Item(weight=2.44, name='washcloth')}, {Item(weight=8.84, name='ring'), Item(weight=7.15, name='craft book'), Item(weight=4.46, name='soap'), Item(weight=17.83, name='Christmas ornament')}, {Item(weight=7.97, name='bow tie'), Item(weight=16.4, name='class ring'), Item(weight=1.26, name='dagger'), Item(weight=8.78, name='letter opener'), Item(weight=5.0, name='spectacles')}, {Item(weight=1.85, name='jar of pickles'), Item(weight=9.4, name='can of beans'), Item(weight=19.36, name='box'), Item(weight=9.39, name='egg')}, {Item(weight=13.24, name='spatula'), Item(weight=7.6, name='soccer ball')}, {Item(weight=17.01, name='plush pony'), Item(weight=19.7, name='pearl necklace'), Item(weight=3.29, name='whip')}], 40, 10, 50, 15)

    chromosome1.cross(chromosome2)
