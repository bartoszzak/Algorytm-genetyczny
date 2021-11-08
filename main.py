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

    solution_list = [SolutionElement(event_list[random.randint(0, 6)], 1, 1) for _ in range(4)]
    solution = Solution(solution_list, distances, datetime(2000, 1, 1), datetime(2000, 1, 1), 'Kraków')
    for element in solution_list:
        print(element)
    print(solution.distance_cost())
