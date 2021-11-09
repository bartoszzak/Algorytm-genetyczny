from data_loading import *
from solution import *

import networkx as nx
import pandas as pd
import json

if __name__ == '__main__':
    df = pd.read_excel("data/example_data.xlsx")
    event_list = load_event_list(df)

    # distances = driving_distances(list(df['city'].unique()))
    with open('distances.json', 'r') as fp:
        distances = json.load(fp)

    # add_edges(G, distances)

    solution_list = []
    # for _ in range(4):
    #     event_id = event_list[random.randint(0, 6)].event_id
    #     stay_duration = random.randint(1, 3)
    #     ingredients_bought = random.randint(0, 2000)
    #     attributes = event_list[event_id].attributes
    #
    #     solution_list.append(SolutionElement(event_id, stay_duration, ingredients_bought, **attributes))

    solution_list.append(SolutionElement(0, 3, 6000, **event_list[0].attributes))
    solution_list.append(SolutionElement(1, 3, 11000, **event_list[1].attributes))
    solution_list.append(SolutionElement(2, 3, 2400, **event_list[2].attributes))
    solution_list.append(SolutionElement(3, 3, 8400, **event_list[3].attributes))

    # solution_list = [SolutionElement(event_list[5].event_id, 2, 1), SolutionElement(event_list[6].event_id, 1, 1),
    #                  SolutionElement(event_list[1].event_id, 2, 1), SolutionElement(event_list[1].event_id, 2, 1)]
    solution = Solution(solution_list, distances, datetime(2022, 7, 1), datetime(2022, 8, 1), 'Kraków')
    for element in solution_list:
        print(element)

    print(solution.overall_profit())
