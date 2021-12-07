from data_loading import *
from solution import *
from algorithm import *

import pandas as pd
import json

if __name__ == '__main__':
    df = pd.read_excel("data/example_data.xlsx")
    event_list = load_event_list(df)

    # distances = driving_distances(list(df['city'].unique()))
    with open('distances.json', 'r') as fp:
        distances = json.load(fp)

    start_date = datetime(2022, 7, 4)
    end_date = datetime(2022, 7, 10)

    population = create_initial_population(100000, event_list, distances, start_date, end_date, 'Kraków')
    population = selection(population)
    print(population[0].overall_profit())

    pass

    # solution_list = []
    # solution_list.append(SolutionElement(0, 2, 6000, **event_list[0].attributes))
    # solution_list.append(SolutionElement(1, 1, 2400, **event_list[1].attributes))
    # solution_list.append(SolutionElement(2, 1, 1600, **event_list[2].attributes))
    # solution_list.append(SolutionElement(3, 2, 5000, **event_list[3].attributes))
    #
    # solution = Solution(solution_list, distances, start_date, end_date, 'Kraków')
    # for element in solution_list:
    #     print(element)
    #
    # print(f"Całkowity zysk: {solution.overall_profit()}")
