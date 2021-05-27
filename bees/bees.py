from bees.Solution import Solution
import random


class Scout:
    def __init__(self, solution: Solution, i: int):
        self.solution = solution
        self.i = i

    @property
    def cost(self):
        return self.solution.cost

    @property
    def fitness(self):
        return self.solution.fitness


class FlowerPatch:
    def __init__(self, scout: Scout, fpf: callable, mp=0.1):
        """
        Keyword arguments:
            scout - bee scout which solution will used to creating this flower patch
            fpf - function that determines size of the flower patch based on the scouts solution fitness
            mp - mutation probability mutation removes one item from a trip and later adds that item to random trip
        """
        self.scout = scout
        self.mp = mp
        self.solutions = [self.get_solution() for _ in range(fpf(self.scout.fitness))]

    def get_solution(self):
        """with the probability of mp removes item from a trip and then adds it to the other trip"""
        items_to_add = []
        car_trips = []
        truck_trips = []

        for ct in self.scout.solution.car_trips:
            car_trips.append(ct.copy())
            if random.random() < self.mp:
                if ct == []:
                    continue
                removed_item = random.choice(ct)
                car_trips[-1].remove(removed_item)
                items_to_add.append(removed_item)

        for tt in self.scout.solution.truck_trips:
            truck_trips.append(tt.copy())
            if random.random() < self.mp:
                if tt == []:
                    continue
                removed_item = random.choice(tt)
                truck_trips[-1].remove(removed_item)
                items_to_add.append(removed_item)

        random.shuffle(items_to_add)
        for item in items_to_add:
            item_added = False
            for ct in car_trips:
                if sum(i.weight for i in ct) + item.weight <= self.scout.solution.pp.car_load:
                    ct.append(item)
                    item_added = True
                    break
            if item_added:
                continue
            for tt in truck_trips:
                if sum(i.weight for i in tt) + item.weight <= self.scout.solution.pp.truck_load:
                    tt.append(item)
                    item_added = True
                    break
            if not item_added:
                car_trips.append([item])
        return Solution(car_trips, truck_trips, self.scout.solution.pp)
