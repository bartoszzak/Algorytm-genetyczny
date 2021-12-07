from solution import *
import random


def create_initial_population(population_size: int, event_list: List[Event], distances: Dict, start_date: datetime,
                              end_date: datetime, start_city: str, product_price: float = 9.0,
                              max_capacity: int = 100000, starting_ingredients: int = 500, visitors_coeff: float = 0.2,
                              distance_coeff: float = 50 / 100000, capacity_punishment_coeff: float = 18.0,
                              duration_punishment_coeff: float = 5000) -> List[Solution]:
    population: List[Solution] = []
    for _ in range(population_size):
        solution_duration = 0
        solution_list = []
        while solution_duration < (end_date - start_date).days:
            event = random.choice(event_list)
            stay_duration = random.randint(1, (event.end_date - event.start_date).days + 1)
            solution_duration += stay_duration
            ingredients_bought = random.randint(0, max_capacity)
            solution_element = SolutionElement(event.event_id, stay_duration, ingredients_bought, **event.attributes)
            solution_list.append(solution_element)

        population.append(
            Solution(solution_list, distances, start_date, end_date, start_city, product_price, max_capacity,
                     starting_ingredients, visitors_coeff, distance_coeff, capacity_punishment_coeff,
                     duration_punishment_coeff))
    return population


def selection(population: List[Solution], method: str = "rank") -> List[Solution]:
    if method == 'rank':
        population = sorted(population, key=lambda x: x.overall_profit(), reverse=True)
        return population
