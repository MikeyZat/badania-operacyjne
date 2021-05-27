from bees.ProblemParameters import ProblemParameters


class Solution:
    def __init__(self, car_trips: list, truck_trips: list, pp: ProblemParameters):
        self.car_trips = car_trips
        self.truck_trips = truck_trips
        self.pp = pp

    @property
    def cost(self):
        return len(self.car_trips) * self.pp.car_cost + len(self.truck_trips) * self.pp.truck_cost

    @property
    def fitness(self):
        return -self.cost

    def contains_all(self, items):
        for item in items:
            found = False
            for ct in self.car_trips:
                if item in ct:
                    found = True
                    break
            if found:
                continue
            for tt in self.truck_trips:
                if item in tt:
                    found = True
                    break
            if not found:
                return False
        return True

    def __str__(self):
        return f"Fitness: {self.fitness}\n" \
               f"Car trips: {self.car_trips}\n" \
               f"Truck trips: {self.truck_trips}"

    def __repr__(self):
        return self.__str__()
