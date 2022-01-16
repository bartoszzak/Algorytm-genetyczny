from typing import Dict, List, Union
from datetime import datetime, timedelta


class Event:
    def __init__(self, event_id: int, **attributes):
        self.event_id = event_id
        self.city = None
        self.start_date = None
        self.end_date = None
        self.visitors = None
        self.ingredient_cost = None
        self.parking_cost = None
        self.attributes = attributes
        self.__dict__.update(self.attributes)


class SolutionElement(Event):
    def __init__(self, event_id: Union[int, None], stay_duration: int, ingredients_bought: int, **attributes):
        super().__init__(event_id, **attributes)
        if event_id is not None:
            self.stay_duration = stay_duration
            self.ingredients_bought = ingredients_bought
            if self.stay_duration > (self.end_date - self.start_date).days + 1:
                self.stay_duration = (self.end_date - self.start_date).days + 1
        else:
            self.stay_duration = stay_duration
            self.ingredients_bought = None

        self.__dict__.update(self.attributes)

    def __str__(self):
        return f"event_id = {self.event_id}, city = {self.city}, stay_duration = {self.stay_duration}," \
               f" ingredients_bought = {self.ingredients_bought}"


class Solution:
    distances = {}
    start_date = datetime(1, 1, 1)
    end_date = datetime(1, 1, 1)
    start_city = ""
    product_price = 0.0
    max_capacity = 0
    starting_ingredients = 0

    visitors_coeff = 0.0
    distance_coeff = 0.0
    capacity_punishment_coeff = 0.0
    duration_punishment_coeff = 0.0

    def __init__(self, solution_list: List[SolutionElement]):

        self.solution_list = solution_list

        if self.solution_list[0].city is None:
            self.solution_list[0].city = self.start_city

        for i in range(1, len(self.solution_list)):
            if self.solution_list[i].city is None:
                self.solution_list[i].city = self.solution_list[i - 1].city

    def profit(self, solution_element: SolutionElement, event_day: int) -> float:
        visitors = solution_element.visitors
        return self.visitors_coeff * visitors[event_day] * self.product_price

    def ingredients_cost(self, solution_element: SolutionElement) -> float:
        return solution_element.ingredients_bought * solution_element.ingredient_cost

    def parking_cost(self, solution_element: SolutionElement) -> float:
        cost = 0
        for day in range(solution_element.stay_duration):
            cost += solution_element.parking_cost[day]
        return cost

    def overall_distance_cost(self) -> float:
        # koszt dojazdu z miasta startowego na pierwsze wydarzenie
        cost = self.distance_coeff * self.distances[self.start_city][self.solution_list[0].city]

        for i in range(1, len(self.solution_list)):
            cost += self.distance_coeff * self.distances[self.solution_list[i - 1].city][self.solution_list[i].city]

        # koszt powrotu do miasta startowego
        cost += self.distance_coeff * self.distances[self.start_city][self.solution_list[-1].city]
        return cost

    def capacity_punishment(self, current_ingredients: int) -> float:
        if current_ingredients < 0:
            return -current_ingredients * self.capacity_punishment_coeff
        elif current_ingredients > self.max_capacity:
            return (current_ingredients - self.max_capacity) * self.capacity_punishment_coeff
        else:
            return 0

    def duration_punishment(self, current_date: datetime) -> float:
        if current_date > self.end_date:
            return (current_date - self.end_date).days * self.duration_punishment_coeff
        else:
            return 0

    def overall_profit(self):
        overall_profit = 0
        current_date = self.start_date
        current_ingredients = self.starting_ingredients
        for solution_element in self.solution_list:
            # print(f"current_date = {current_date}, current_ingredients = {current_ingredients}")
            # print(f"event_id = {solution_element.event_id}, city = {solution_element.city},"
            #       f" event_start_date = {solution_element.start_date}, event_end_date = {solution_element.end_date}")
            if solution_element.event_id is not None:
                ingredients_used = 0
                for event_day in range(solution_element.stay_duration):
                    if solution_element.start_date <= current_date <= solution_element.end_date:
                        profit = self.profit(solution_element, event_day)
                        overall_profit += profit
                        ingredients_used += profit // self.product_price
                        # print(f"    day = {event_day + 1}, profit = {profit}, ingredients_used = {ingredients_used}")

                    current_date += timedelta(days=1)

                overall_profit -= self.parking_cost(solution_element)
                current_ingredients -= ingredients_used
                current_ingredients += solution_element.ingredients_bought
                overall_profit -= self.capacity_punishment(current_ingredients)

                overall_profit -= self.ingredients_cost(solution_element)
                # print(f"    parking cost = {self.parking_cost(solution_element)},"
                #       f" ingredients_bought = {solution_element.ingredients_bought},"
                #       f" ingredients_cost = {self.ingredients_cost(solution_element)}\n")

        overall_profit -= self.overall_distance_cost()
        overall_profit -= self.duration_punishment(current_date)
        return overall_profit
