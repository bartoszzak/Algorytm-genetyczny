from typing import Dict, List, Union
from datetime import datetime

import networkx as nx


class Event:
    def __init__(self, event_id: int, **attributes):
        self.event_id = event_id
        self.__dict__.update(attributes)


class SolutionElement:
    def __init__(self, event: Union[Event, None], stay_duration: int, ingredients_bought: int):
        if Event is not None:
            self.visitors = event.visitors
            self.city = event.city
            self.event_id = event.event_id
            self.stay_duration = stay_duration
            self.ingredients_bought = ingredients_bought
        else:
            self.visitors = None
            self.city = None
            self.event_id = None
            self.stay_duration = stay_duration
            self.ingredients_bought = None

    def __str__(self):
        return f"event_id = {self.event_id}, city = {self.city}, stay_duration = {self.stay_duration}," \
               f" ingredients_bought = {self.ingredients_bought}"


class Solution:
    def __init__(self, solution_list: List[SolutionElement], distances: Dict[str, Dict[str, float]],
                 start_date: datetime, end_date: datetime, start_city: str,
                 profit_coeff: float = 0.2, distance_coeff: float = 50 / 100000):
        self.solution_list = solution_list
        self.distances = distances
        self.start_date = start_date
        self.end_date = end_date
        self.current_date = start_date
        self.start_city = start_city
        self.profit_coeff = profit_coeff
        self.distance_coeff = distance_coeff

        if self.solution_list[0].city is None:
            self.solution_list[0].city = self.start_city

        for i in range(1, len(self.solution_list)):
            if self.solution_list[i].city is None:
                self.solution_list[i].city = self.solution_list[i - 1].city

    def distance_cost(self) -> float:
        # koszt dojazdu z miasta startowego na pierwsze wydarzenie
        cost = self.distance_coeff * self.distances[self.start_city][self.solution_list[0].city]

        for i in range(1, len(self.solution_list)):
            cost += self.distance_coeff * self.distances[self.solution_list[i - 1].city][self.solution_list[i].city]

        # koszt powrotu do miasta startowego
        cost += self.distance_coeff * self.distances[self.start_city][self.solution_list[-1].city]

        return cost
