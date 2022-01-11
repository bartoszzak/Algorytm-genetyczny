import pickle
from typing import Optional

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


def genetic_algorithm(population_size: int, generations: int, selection_method: str, tournament_size: int,
                      crossover_methods: List[str], mutation_methods: List[str],
                      mutation_size: float, parents_percent: int, start_date: datetime, end_date: datetime,
                      start_city: str, product_price: float = 9.0, max_capacity: int = 100000,
                      starting_ingredients: int = 500, visitors_coeff: float = 0.2, distance_coeff: float = 50 / 100000,
                      capacity_punishment_coeff: float = 18.0, duration_punishment_coeff: float = 5000):
    Solution.distances = distances
    Solution.start_date = start_date
    Solution.end_date = end_date
    Solution.start_city = start_city
    Solution.product_price = product_price
    Solution.max_capacity = max_capacity
    Solution.starting_ingredients = starting_ingredients

    Solution.visitors_coeff = visitors_coeff
    Solution.distance_coeff = distance_coeff
    Solution.capacity_punishment_coeff = capacity_punishment_coeff
    Solution.duration_punishment_coeff = duration_punishment_coeff

    population = create_initial_population(population_size)
    best_in_generations: List[Solution] = [max(population, key=lambda x: x.overall_profit())]
    for _ in range(generations):
        parents = selection(population, parents_percent, selection_method, tournament_size)
        num_mutation_parents = int(len(parents) * mutation_size)
        num_crossover_parents = len(parents) - num_mutation_parents
        if num_crossover_parents % 2 != 0:
            num_crossover_parents -= 1
            num_mutation_parents += 1

        num_mutation_children = int(population_size * mutation_size)
        mutation_children = [None for _ in range(num_mutation_children)]
        mutation_parents = parents[:num_mutation_parents]
        mutation_child_count = 0
        while mutation_child_count < num_mutation_children:
            for parent in mutation_parents:
                mutation_children[mutation_child_count] = mutation(parent, random.choice(mutation_methods))
                mutation_child_count += 1
                if mutation_child_count >= num_mutation_children:
                    break

        num_crossover_children = population_size - num_mutation_children
        crossover_parents = parents[num_crossover_parents:]
        crossover_children = crossover(crossover_parents, crossover_methods, num_crossover_children)

        population = crossover_children + mutation_children
        best_in_generations.append(max(population, key=lambda x: x.overall_profit()))

    best_solution: Solution = max(best_in_generations, key=lambda x: x.overall_profit())
    best_in_generations = [solution.overall_profit() for solution in best_in_generations]
    return best_solution, best_in_generations


def create_initial_population(population_size: int) -> List[Solution]:
    population: List[Solution] = [None for _ in range(population_size)]

    for i in range(population_size):
        solution_duration = 0
        solution_list = []
        event_list_copy = event_list[:]
        while solution_duration < (Solution.end_date - Solution.start_date).days and event_list_copy:
            event = event_list_copy.pop(random.randint(0, len(event_list_copy) - 1))
            stay_duration = random.randint(1, (event.end_date - event.start_date).days + 1)
            solution_duration += stay_duration
            ingredients_bought = random.randint(0, Solution.max_capacity)
            solution_element = SolutionElement(event.event_id, stay_duration, ingredients_bought, **event.attributes)
            solution_list.append(solution_element)

        population[i] = Solution(solution_list)
    return population


def selection(population: List[Union[Solution, None]], parents_percent: float, method: str = "tournament",
              tournament_size: Optional[int] = None) -> List[Solution]:
    population.sort(key=lambda x: x.overall_profit(), reverse=True)
    population_idx_list = [i for i in range(len(population))]
    num_of_parents = int(len(population) * parents_percent / 100)
    if num_of_parents % 2 == 1:
        num_of_parents += 1
    if method == 'tournament':
        parents = [None for _ in range(num_of_parents)]
        for i in range(num_of_parents):
            tournament = [random.choice(population_idx_list) for _ in range(tournament_size)]
            best_idx = min(tournament)
            parents[i] = population[best_idx]
            population_idx_list.remove(best_idx)
        return parents
    else:
        raise ValueError("Wrong selection method")


def crossover(parents: List[Solution], methods, num_of_children: int) -> List[Solution]:
    children: List[Union[None, Solution]] = [None for _ in range(num_of_children)]
    child_idx = 0
    while child_idx < num_of_children:
        random.shuffle(parents)
        for i in range(0, len(parents), 2):
            parent1 = parents[i]
            parent2 = parents[i + 1]

            method = random.choice(methods)
            if method == "one_point":
                crossover_point = random.randint(1, min(len(parent1.solution_list), len(parent2.solution_list)) - 2)
                child1_solution_list = parent1.solution_list[:crossover_point] + parent2.solution_list[crossover_point:]
                child2_solution_list = parent2.solution_list[:crossover_point] + parent1.solution_list[crossover_point:]
                child1 = Solution(child1_solution_list)
                child2 = Solution(child2_solution_list)

            elif method == "two_point":
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

                child1 = Solution(child1_solution_list)
                child2 = Solution(child2_solution_list)

            else:
                raise ValueError("Wrong crossover method")

            try:
                children[child_idx] = child1
            except IndexError:
                child_idx += 2
                break
            try:
                children[child_idx + 1] = child2
            except IndexError:
                child_idx += 2
                break
            child_idx += 2
    return children


def mutation(parent: Solution, method="uniform"):
    child = pickle.loads(pickle.dumps(parent, -1))
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

    else:
        raise ValueError("Wrong mutation method")

    return child
