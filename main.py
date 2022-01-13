from data_loading import *
from solution import *
from algorithm import *

import pandas as pd
import json
import matplotlib.pyplot as plt
import PySimpleGUI as sg

if __name__ == '__main__':
    algorithm_settings = {
        'selection_method': "tournament",
        'tournament_size': 10,
        'crossover_methods': ["one_point", "two_point"],
        'mutation_methods': ["uniform", "swap", "event_change"],
        'population_size': 100,
        'generations': 100,
        'parents_percent': 15,
        'mutation_size': 0.15,
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

    settings_column_text_width = 23
    settings_column = [
        [sg.Text("Parametry zagadnienia")],
        # Wybór dat
        [sg.Text('Data startowa', size=(settings_column_text_width, 1)),
         sg.Text(f"{problem_settings['start_date'].day:02}-{problem_settings['start_date'].month:02}-"
                 f"{problem_settings['start_date'].year}", size=(9, 1), key="start_date"),
         sg.In(key='-CAL_START-', enable_events=True, visible=False),
         sg.CalendarButton("Wybierz datę", target='-CAL_START-', key='_CALENDAR_START_', format='%d-%m-%Y')],
        [sg.Text('Data końcowa', size=(settings_column_text_width, 1)),
         sg.Text(f"{problem_settings['end_date'].day:02}-{problem_settings['end_date'].month:02}-"
                 f"{problem_settings['end_date'].year}", size=(9, 1), key="end_date"),
         sg.In(key='-CAL_END-', enable_events=True, visible=False),
         sg.CalendarButton("Wybierz datę", target='-CAL_END-', key='_CALENDAR_END_', format='%d-%m-%Y')],

        [sg.Text('Miasto startowe', size=(settings_column_text_width, 1)),
         sg.InputText("Kraków", size=(24, 1), enable_events=True, key="start_city")],

        [sg.Text('Cena produktu', size=(settings_column_text_width, 1)),
         sg.InputText(problem_settings['product_price'], size=(24, 1), enable_events=True, key="product_price")],

        [sg.Text('Pojemność', size=(settings_column_text_width, 1)),
         sg.InputText(problem_settings['max_capacity'], size=(24, 1), enable_events=True, key="max_capacity")],

        [sg.Text('Startowe składniki', size=(settings_column_text_width, 1)),
         sg.InputText(problem_settings['starting_ingredients'], size=(24, 1), enable_events=True,
                      key="starting_ingredients")],

        [sg.Text('Współczynnik odwiedzających', size=(settings_column_text_width, 1)),
         sg.InputText(problem_settings['visitors_coeff'], size=(24, 1), enable_events=True, key="visitors_coeff")],
        [sg.Submit(), sg.Cancel()]
    ]

    layout = [
        [
            sg.Column(settings_column)
        ]
    ]

    window = sg.Window("Genetic algorithm", layout)

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "-CAL_START-":
            problem_settings['start_date'] = datetime(int(values["-CAL_START-"][-4:]),
                                                      int(values["-CAL_START-"][3:5]),
                                                      int(values["-CAL_START-"][:2]))
            window['start_date'].update(f"{problem_settings['start_date'].day:02}-"
                                        f"{problem_settings['start_date'].month:02}-"
                                        f"{problem_settings['start_date'].year}")

        if event == "-CAL_END-":
            problem_settings['end_date'] = datetime(int(values["-CAL_END-"][-4:]),
                                                    int(values["-CAL_END-"][3:5]),
                                                    int(values["-CAL_END-"][:2]))
            window['end_date'].update(f"{problem_settings['end_date'].day:02}-"
                                      f"{problem_settings['end_date'].month:02}-"
                                      f"{problem_settings['end_date'].year}")

        if event == "start_city":
            problem_settings['start_city'] = values["start_city"]

        if event == "product_price":
            try:
                problem_settings['product_price'] = float(values["product_price"])
            except ValueError:
                pass

        if event == "max_capacity":
            try:
                if int(values["max_capacity"]) < 0:
                    sg.Popup("Nieprawidłowa wartość")
                    values["max_capacity"] = problem_settings['max_capacity']
                    window['max_capacity'].update(values["max_capacity"])
                problem_settings['max_capacity'] = int(values["max_capacity"])
            except ValueError:
                pass

        if event == "starting_ingredients":
            try:
                if int(values["starting_ingredients"]) < 0 \
                        or int(values["starting_ingredients"]) > problem_settings['max_capacity']:
                    sg.Popup("Nieprawidłowa wartość")
                    values["starting_ingredients"] = problem_settings['starting_ingredients']
                    window['starting_ingredients'].update(values["starting_ingredients"])
                problem_settings['starting_ingredients'] = int(values["starting_ingredients"])
            except ValueError:
                pass

        if event == "visitors_coeff":
            try:
                if float(values["visitors_coeff"]) < 0 or float(values["visitors_coeff"]) > 1:
                    sg.Popup("Nieprawidłowa wartość")
                    values["visitors_coeff"] = problem_settings['visitors_coeff']
                    window['visitors_coeff'].update(values["visitors_coeff"])
                problem_settings['visitors_coeff'] = int(values["visitors_coeff"])
            except ValueError:
                pass

    window.close()
