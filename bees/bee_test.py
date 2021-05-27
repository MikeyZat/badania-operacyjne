from ProblemParameters import ProblemParameters
from Item import Item
from BeeAlgorithm import BeeAlgorithm
from rand_solution_generator import rand_solution
from Solution import Solution

items, truck_capacity, car_capacity, truck_cost, car_cost = Item.from_json('../test_data/ex.json')
pp = ProblemParameters(truck_capacity, car_capacity, truck_cost, car_cost)


def test_fpf(fitness):
    return int(-fitness) // 10


def test_sf():
    ct, tt = rand_solution(items, car_capacity, truck_capacity)
    return Solution(ct, tt, pp)


def main():
    ba = BeeAlgorithm(1000, 50, 25, 50, 10, 5, test_fpf, test_sf, pp)
    ba.run(100)


if __name__ == '__main__':
    main()
