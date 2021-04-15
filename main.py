import dataclasses
import random


# not sure what this class will look like in the future
@dataclasses.dataclass(order=True, frozen=True)
class Item:
    weight: float
    name: str = dataclasses.field(default='')

    def __sub__(self, other):
        return self.weight - other

    def __add__(self, other):
        return self.weight + other

    def __str__(self):
        return str(self.weight)


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
    truck_items = items[split_i:] + [item for item in car_items if item.weight > car_capacity]
    car_items = [item for item in car_items if item.weight <= car_capacity]

    return divide_into_trips(car_items, car_capacity), divide_into_trips(truck_items, truck_capacity)


def main():
    n = 10
    car_capacity = n // 2
    truck_capacity = 2 * n
    weights = random.choices(list(range(1, int(n / 1.5))), k=n)
    
    car_cost = 10
    truck_cost = 50

    items = [Item(w) for w in weights]
    print('all items:')
    print(items)

    car_trips, truck_trips = rand_solution(items, car_capacity, truck_capacity)
    print('\nVia car')
    print(car_trips)
    print('\n=============\nVia truck')
    print(truck_trips)
    
    operation_cost = cost(car_trips, truck_trips, car_cost, truck_cost)

    print('\nCost')
    print(operation_cost)


if __name__ == '__main__':
    main()
