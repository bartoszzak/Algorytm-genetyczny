import pickle

from solution import *
from data_loading import *
import pandas as pd
import random
from copy import deepcopy, copy
import json

df = pd.read_excel("data/example_data.xlsx")
event_list = load_event_list(df)

# distances = driving_distances(list(df['city'].unique()))
# with open('distances.json', 'w') as fp:
#     json.dump(distances, fp)
with open('distances.json', 'r') as fp:
    distances = json.load(fp)


def genetic_algorithm(population_size: int, generations: int, crossover_methods: List[str], mutation_methods: List[str],
                      mutation_chance: float, parents_percent: int, start_date: datetime, end_date: datetime, start_city: str,
                      product_price: float = 9.0, max_capacity: int = 100000, starting_ingredients: int = 500,
                      visitors_coeff: float = 0.2, distance_coeff: float = 50 / 100000,
                      capacity_punishment_coeff: float = 18.0, duration_punishment_coeff: float = 5000):
    best_in_generations: List[float] = []
    population = create_initial_population(population_size, start_date, end_date, start_city, product_price,
                                           max_capacity, starting_ingredients, visitors_coeff, distance_coeff,
                                           capacity_punishment_coeff, duration_punishment_coeff)
    for _ in range(generations):
        parents = selection(population, parents_percent)
        best_in_generations.append(population[0].overall_profit())
        children = crossover(parents, random.choice(crossover_methods))
        for child in children:
            if random.random() <= mutation_chance:
                mutation(child, random.choice(mutation_methods))

        population[-len(children):] = children

    best_solution: Solution = max(population, key=lambda x: x.overall_profit())
    return best_solution, best_in_generations


def create_initial_population(population_size: int, start_date: datetime,
                              end_date: datetime, start_city: str, product_price: float,
                              max_capacity: int, starting_ingredients: int, visitors_coeff: float,
                              distance_coeff: float, capacity_punishment_coeff: float,
                              duration_punishment_coeff: float) -> List[Solution]:
    population: List[Solution] = [None for _ in range(population_size)]

    for i in range(population_size):
        solution_duration = 0
        solution_list = []
        event_list_copy = event_list[:]
        while solution_duration < (end_date - start_date).days and event_list_copy:
            event = event_list_copy.pop(random.randint(0, len(event_list_copy) - 1))
            stay_duration = random.randint(1, (event.end_date - event.start_date).days + 1)
            solution_duration += stay_duration
            ingredients_bought = random.randint(0, max_capacity)
            solution_element = SolutionElement(event.event_id, stay_duration, ingredients_bought, **event.attributes)
            solution_list.append(solution_element)

        population[i] = Solution(solution_list, distances, start_date, end_date, start_city, product_price,
                                 max_capacity, starting_ingredients, visitors_coeff, distance_coeff,
                                 capacity_punishment_coeff, duration_punishment_coeff)
    return population


def selection(population: List[Solution], parents_percent: float, method: str = "rank") -> List[Solution]:
    if method == 'rank':
        num_of_parents = int(len(population) * parents_percent / 100)
        if num_of_parents % 2 == 1:
            num_of_parents += 1
        population.sort(key=lambda x: x.overall_profit(), reverse=True)
        parents = population[:num_of_parents]
        return parents


def crossover(parents: List[Solution], method="one_point") -> List[Solution]:
    children: List[Union[None, Solution]] = [None for _ in range(len(parents))]
    random.shuffle(parents)
    if method == "one_point":
        for i in range(0, len(parents), 2):
            parent1 = pickle.loads(pickle.dumps(parents[i], -1))
            parent2 = pickle.loads(pickle.dumps(parents[i + 1], -1))

            crossover_point = random.randint(1, min(len(parent1.solution_list), len(parent2.solution_list)) - 2)
            child1_solution_list = parent1.solution_list[:crossover_point] + parent2.solution_list[crossover_point:]
            child2_solution_list = parent2.solution_list[:crossover_point] + parent1.solution_list[crossover_point:]
            child1 = parent1
            child1.solution_list = child1_solution_list
            child2 = parent2
            child2.solution_list = child2_solution_list

            children[i] = child1
            children[i + 1] = child2

    elif method == "two_point":
        for i in range(0, len(parents), 2):
            parent1 = pickle.loads(pickle.dumps(parents[i], -1))
            parent2 = pickle.loads(pickle.dumps(parents[i + 1], -1))

            idx = range(1, min(len(parent1.solution_list), len(parent2.solution_list)))
            crossover_point1, crossover_point2 = random.sample(idx, 2)
            crossover_point1, crossover_point2 = min(crossover_point1, crossover_point2), max(crossover_point1,
                                                                                              crossover_point2)
            child1_solution_list = parent1.solution_list[:crossover_point1] \
                                   + parent2.solution_list[crossover_point1:crossover_point2] \
                                   + parent1.solution_list[crossover_point2:]
            child2_solution_list = parent2.solution_list[:crossover_point1] \
                                   + parent1.solution_list[crossover_point1:crossover_point2] \
                                   + parent2.solution_list[crossover_point2:]

            child1 = parent1
            child1.solution_list = child1_solution_list
            child2 = parent2
            child2.solution_list = child2_solution_list

            children[i] = child1
            children[i + 1] = child2

    return children


def mutation(child: Solution, method="uniform"):
    if method == "uniform":
        index = random.randint(0, len(child.solution_list) - 1)
        element = child.solution_list[index]
        if random.random() > 0.5:
            element.stay_duration = random.randint(1, (element.end_date - element.start_date).days + 1)
        else:
            element.ingredients_bought = random.randint(0, child.max_capacity)

    elif method == "swap":
        idx = range(len(child.solution_list))
        i1, i2 = random.sample(idx, 2)
        child.solution_list[i1], child.solution_list[i2] = child.solution_list[i2], child.solution_list[i1]

    elif method == "event_change":
        new_event = random.choice(event_list)
        index = random.randint(0, len(child.solution_list) - 1)
        stay_duration = child.solution_list[index].stay_duration
        ingredients_bought = child.solution_list[index].ingredients_bought
        child.solution_list[index] = SolutionElement(new_event.event_id, stay_duration, ingredients_bought,
                                                     **new_event.attributes)
