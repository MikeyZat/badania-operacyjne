import random
from bees.BeeAlgorithm import BeeAlgorithm
from bees.ProblemParameters import ProblemParameters
from bees.Solution import Solution
from genetic.GeneticAlgorithm import GeneticAlgorithm
from genetic.genes import Chromosome
from Item import Item
from genetic.ga_selections import best_rank_selection
from rand_solution_generator import rand_solution
import logging
from argparse import ArgumentParser


def cost(car_trips, truck_trips, car_cost, truck_cost):
    return len(car_trips) * car_cost + len(truck_trips) * truck_cost


def print_rand_solution(file_name='test_data/ex.json'):
    """RANDOM SOLUTION PRINTING"""
    items, truck_capacity, car_capacity, truck_cost, car_cost = Item.from_json(
        file_name)
    car_trips, truck_trips = rand_solution(
        items, car_capacity, truck_capacity, random.random())

    print('\nVia car')
    print(f'n = {len(car_trips)}')
    print(car_trips)
    print('\n=============\nVia truck')
    print(f'm = {len(truck_trips)}')
    print(truck_trips)
    operation_cost = cost(car_trips, truck_trips, car_cost, truck_cost)
    print('\nCost')
    print(operation_cost)


# GENETIC

def gene_rand_solution(items, car_capacity, truck_capacity):
    car_trips, truck_trips = rand_solution(
        items, car_capacity, truck_capacity, random.random())
    return car_trips + truck_trips


def ga_population_generator(file_name='test_data/ex.json', pop_size=100):
    items, truck_capacity, car_capacity, truck_cost, car_cost = Item.from_json(
        file_name)

    def _gen():
        return [
            Chromosome(
                gene_rand_solution(items, car_capacity, truck_capacity),
                truck_capacity,
                car_capacity,
                truck_cost,
                car_cost
            ) for _ in range(pop_size)
        ]

    return _gen


def ga_basic_stop_condition(n_gens):
    def _stop_condition(_, __, i):
        return i > n_gens
    return _stop_condition


# BEES

def get_pp(file_name='test_data/ex.json'):
    items, truck_capacity, car_capacity, truck_cost, car_cost = Item.from_json(file_name)
    return ProblemParameters(truck_capacity, car_capacity, truck_cost, car_cost)


def bee_fpf(fitness):
    return int(-fitness) // 10


def get_bee_sf(file_name='test_data/ex.json'):
    items, truck_capacity, car_capacity, truck_cost, car_cost = Item.from_json(file_name)
    pp = ProblemParameters(truck_capacity, car_capacity, truck_cost, car_cost)

    def _bee_sf():
        ct, tt = rand_solution(items, car_capacity, truck_capacity)
        return Solution(ct, tt, pp)

    return _bee_sf


def main():
    parser = ArgumentParser(
        description='Demonstracja algorytmów populacyjnych'
    )
    parser.add_argument(
        'infile', nargs='?', default='test_data/ex.json',
        help='Ścieżka do pliku JSON z instancją problemu o strukturze '
             'identycznej, jak załączony simple.json (domyślnie ex.json)'
    )
    parser.add_argument(
        '-n', dest='gens', type=int, default=1000,
        help='Ilość pokoleń, które chcemy wygenerować (domyślnie 1000)'
    )
    parser.add_argument(
        '-u', dest='unchanged_gens', type=int, default=200,
        help='Ilość pokoleń z rzędu bez poprawy, po których powinniśmy '
             'się zatrzymać (domyślnie 200)'
    )
    parser.add_argument(
        '-k', dest='pop_size', type=int, default=100,
        help='Rozmiar populacji w każdym pokoleniu'
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.ERROR)

    # print_rand_solution(args.infile)

    # GENETIC ALGORITHM STARTS
    print("-" * 100)
    print("Running genetic algorithm")
    ga = GeneticAlgorithm(ga_population_generator(args.infile, args.pop_size),
                          best_rank_selection, ga_basic_stop_condition(args.gens))

    solution = ga.run(args.gens)
    print("Found solution:")
    print(solution)
    print(solution.cost)

    # BEES ALGORITHM STARTS
    print("-"*100)
    print("Running bees algorithm")
    pp = get_pp(args.infile)
    ba = BeeAlgorithm(args.gens, 50, 25, 50, 10, 5, bee_fpf, get_bee_sf(args.infile), pp)
    solution = ba.run(args.pop_size)
    print("Found solution:")
    print(solution)
    print(solution.cost)


if __name__ == '__main__':
    main()
