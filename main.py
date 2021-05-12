import random
from GeneticAlgorithm import GeneticAlgorithm
from genes import Chromosome
from Item import Item
from ga_selections import best_rank_selection
import logging


def divide_into_trips(items, capacity):
    divided_weights = []

    curr_capacity = capacity
    curr_trip_items = []
    for item in items:
        if curr_capacity - item.weight >= 0:
            curr_trip_items.append(item)
        else:
            divided_weights.append(curr_trip_items)
            curr_trip_items = [item]
            curr_capacity = capacity
        curr_capacity -= item.weight
    if curr_trip_items:
        divided_weights.append(curr_trip_items)
    return divided_weights


def cost(car_trips, truck_trips, car_cost, truck_cost):
    return len(car_trips)*car_cost + len(truck_trips)*truck_cost


# I'm assuming every weight < truck capacity
def rand_solution(items, car_capacity, truck_capacity, car_item_prob=-1):
    """creates a solution by shuffling weights and splitting the array"""
    if car_item_prob == -1:
        car_item_prob = car_capacity / truck_capacity

    random.shuffle(items)
    split_i = int(len(items) * car_item_prob)
    car_items = items[:split_i]
    truck_items = items[split_i:] + \
        [item for item in car_items if item.weight > car_capacity]
    car_items = [item for item in car_items if item.weight <= car_capacity]

    return divide_into_trips(car_items, car_capacity), divide_into_trips(truck_items, truck_capacity)


def print_rand_solution(file_name='ex.json'):
    """RANDOM SOLUTION PRINTING"""
    items, truck_capacity, car_capacity, truck_cost, car_cost = Item.from_json(
        file_name)
    car_trips, truck_trips = rand_solution(
        items, car_capacity, truck_capacity, random.uniform(0, 1))

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
        items, car_capacity, truck_capacity, random.uniform(0, 1))
    return car_trips + truck_trips


def ga_population_generator(file_name='ex.json'):
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
            ) for _ in range(100)
        ]

    return _gen


def ga_stop_condition(curr_best_match, curr_best_match_fitness, i):
    return i > 1000


def main():

    logging.basicConfig(level=logging.ERROR, filename='output.log')

    print_rand_solution()

    # GENETIC ALGORITHM STARTS
    ga = GeneticAlgorithm(ga_population_generator('example.json'),
                          best_rank_selection, ga_stop_condition)

    solution = ga.run()
    print("Found solution:")
    print(solution)
    print(solution.cost)


if __name__ == '__main__':
    main()
