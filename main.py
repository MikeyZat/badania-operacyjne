import numpy as np


# not sure what this class will look like in the future
class Item:
    def __init__(self, weight):
        self.weight = weight

    def __sub__(self, other):
        return self.weight - other

    def __add__(self, other):
        return self.weight + other

    def __gt__(self, other):
        return self.weight > other

    def __ge__(self, other):
        return self.weight >= other

    def __lt__(self, other):
        return self.weight < other

    def __le__(self, other):
        return self.weight <= other

    def __iadd__(self, other):
        self.weight += other

    def __isub__(self, other):
        self.weight -= other

    def __str__(self):
        return str(self.weight)

    def __repr__(self):
        return str(self.weight)



def divide_into_trips(items, capacity):
    divided_weights = []

    curr_capacity = capacity
    curr_trip_items = []
    for item in items:
        if curr_capacity - item.weight >= 0:
            curr_trip_items.append(item)
        else:
            divided_weights.append(np.array(curr_trip_items))
            curr_trip_items = [item]
            curr_capacity = capacity
        curr_capacity -= item.weight
    if curr_trip_items:
        divided_weights.append(np.array(curr_trip_items))
    return np.array(divided_weights, dtype=object)

def cost(car_trips, truck_trips, car_cost, truck_cost):
    return len(car_trips)*car_cost+len(truck_trips)*truck_cost

# I'm assuming every weight < truck capacity
def rand_solution(items, car_capacity, truck_capacity, car_item_prob=-1):
    """creates a solution by shuffling weights and splitting the array"""
    if car_item_prob == -1:
        car_item_prob = car_capacity / truck_capacity

    np.random.shuffle(items)
    split_i = int(items.shape[0] * car_item_prob)
    car_items = items[:split_i]
    truck_items = np.concatenate((items[split_i:], car_items[car_items > car_capacity]))
    car_items = car_items[car_items <= car_capacity]

    return divide_into_trips(car_items, car_capacity), divide_into_trips(truck_items, truck_capacity)


def main():
    n = 10
    car_capacity = n // 2
    truck_capacity = 2 * n
    weights = np.random.randint(1, n // 1.5, n)
    
    car_cost = 10
    truck_cost = 50

    items = np.array([Item(w) for w in weights])
    print(items)
    print()

    car_trips, truck_trips = rand_solution(items, car_capacity, truck_capacity)
    print(car_trips)
    print("=============")
    print(truck_trips)
    
    operation_cost = cost(car_trips, truck_trips, car_cost, truck_cost)
    
    print(operation_cost)

if __name__ == '__main__':
    main()
