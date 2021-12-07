from data_loading import *
from solution import *
from algorithm import *

import pandas as pd
import json

if __name__ == '__main__':
    df = pd.read_excel("data/example_data.xlsx")
    event_list = load_event_list(df)

    # distances = driving_distances(list(df['city'].unique()))
    # with open('distances.json', 'w') as fp:
    #     json.dump(distances, fp)
    with open('distances.json', 'r') as fp:
        distances = json.load(fp)

    start_date = datetime(2022, 7, 4)
    end_date = datetime(2022, 7, 15)

    generations = 1000
    best_solutions = []
    population = create_initial_population(30, event_list, distances, start_date, end_date, 'Kraków')
    for _ in range(generations):
        parents = selection(population, 30)
        best_solutions.append(population[0].overall_profit())
        children = crossover(parents)
        mutation_chance = 0.1
        for child in children:
            if random.random() <= 0.1:
                mutation(child)

        population[-len(children):] = children

    print(max(population, key=lambda x: x.overall_profit()).overall_profit())
    print(best_solutions)

