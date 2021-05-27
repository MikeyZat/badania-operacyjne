import random


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
