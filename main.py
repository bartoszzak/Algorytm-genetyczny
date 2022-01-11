from data_loading import *
from solution import *
from algorithm import *

import pandas as pd
import json
import matplotlib.pyplot as plt

if __name__ == '__main__':
    df = pd.read_excel("data/example_data.xlsx")
    event_list = load_event_list(df)

    # distances = driving_distances(list(df['city'].unique()))
    with open('distances.json', 'r') as fp:
        distances = json.load(fp)

    algorithm_settings = {
        'selection_method': "tournament",
        'tournament_size': 10,
        'crossover_methods': ["one_point", "two_point"],
        'mutation_methods': ["uniform", "swap", "event_change"],
        'population_size': 100,
        'generations': 500,
        'parents_percent': 30,
        'mutation_size': 0.30,
    }
    problem_settings = {
        'start_date': datetime(2022, 7, 4),
        'end_date': datetime(2022, 7, 15),
        'start_city': "Kraków",
        'product_price': 9.0,
        'max_capacity': 100000,
        'starting_ingredients': 500,
        'visitors_coeff': 0.2,
        'distance_coeff': 50 / 100000,
        'capacity_punishment_coeff': 18.0,
        'duration_punishment_coeff': 5000
    }

    best_solution, best_solutions_in_generations = genetic_algorithm(**algorithm_settings, **problem_settings)
    plt.figure(figsize=(10, 6))
    plt.plot(best_solutions_in_generations)
    plt.grid()
    plt.ylabel("Całkowity przychód")
    plt.xlabel("Generacja")
    plt.show()

