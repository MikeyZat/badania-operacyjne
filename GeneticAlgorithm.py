from random import random, choice


class GeneticAlgorithm:

    def __init__(self, first_population_generator: callable,
                 selection_model: callable, stop_condition: callable, mutation_probability: float = 0.1):
        self.first_generation_func = first_population_generator
        self.selection_model = selection_model
        self.stop_condition = stop_condition
        self.mutation_probability = mutation_probability

    def run(self):
        population = self.first_generation_func()
        population.sort(key=lambda x: x.fitness, reverse=True)
        population_len = len(population)
        i = 0
        while True:
            selected = self.selection_model(population)
            new_population = selected.copy()
            while len(new_population) != population_len:
                child = choice(population).cross(choice(population))
                if random() <= self.mutation_probability:
                    child.mutation()
                new_population.append(child)

            population = new_population
            the_best_match = max(population, key=lambda x: x.fitness)

            if i % 50 == 0:
                print(f'Generation: {i} S: {the_best_match}')

            i += 1
            if self.stop_condition(the_best_match, the_best_match.fitness, i):
                return the_best_match