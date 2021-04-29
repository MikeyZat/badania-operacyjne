def best_rank_selection(generation):
    max_selected = int(len(generation) / 10)
    sorted_by_fitness = sorted(generation, key=lambda x: x.fitness, reverse=True)
    return sorted_by_fitness[:max_selected]
