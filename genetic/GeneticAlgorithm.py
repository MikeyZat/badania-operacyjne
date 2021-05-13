from random import random, choice
from tqdm import trange


def key_f(x):
    return x.fitness


class GeneticAlgorithm:

    def __init__(self, first_population_generator: callable,
                 selection_model: callable, stop_condition: callable, mutation_probability: float = 0.1):
        self.first_generation_func = first_population_generator
        self.selection_model = selection_model
        self.stop_condition = stop_condition
        self.mutation_probability = mutation_probability

    def run(self, n_generations):
        population = self.first_generation_func()
        population.sort(key=key_f, reverse=True)
        population_len = len(population)
        global_best = population[0]
        generations_unchanged = 0  # ilość pokoleń z rzędu bez poprawy
        for i in trange(n_generations):
            selected = self.selection_model(population)
            new_population = selected.copy()
            while len(new_population) != population_len:
                child = choice(population).cross(choice(population))
                if random() <= self.mutation_probability:
                    child.mutation()
                new_population.append(child)

            population = new_population
            the_best_match = max(population, key=key_f)
            if key_f(the_best_match) <= key_f(global_best):
                generations_unchanged += 1
            else:
                global_best = the_best_match
                generations_unchanged = 0

            # if i % 50 == 0:
            #     print(f'Generation: {i} S: {the_best_match}')

            if self.stop_condition(the_best_match, the_best_match.fitness, generations_unchanged):
                break

        return global_best
