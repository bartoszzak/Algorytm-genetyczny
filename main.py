from data_loading import *
from solution import *
from algorithm import *

import pandas as pd
import json

if __name__ == '__main__':
    start_date = datetime(2022, 7, 4)
    end_date = datetime(2022, 7, 15)

    crossover_methods = ["one_point", "two_point"]
    mutation_methods = ["uniform", "swap", "event_change"]
    generations = 100
    mutation_chance = 0.15
    best_solutions = []
    population = create_initial_population(1000, start_date, end_date, 'Kraków')
    for _ in range(generations):
        parents = selection(population, 10)
        best_solutions.append(population[0].overall_profit())
        children = crossover(parents, random.choice(crossover_methods))
        for child in children:
            if random.random() <= mutation_chance:
                mutation(child, random.choice(mutation_methods))

        population[-len(children):] = children

    print(max(population, key=lambda x: x.overall_profit()).overall_profit())
    print(best_solutions)
    best_order = max(population, key=lambda x: x.overall_profit()).solution_list
    for el in best_order:
        print(el)
