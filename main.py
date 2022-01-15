from multiprocessing import Queue
from threading import Thread

import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from algorithm import *


def ga_mp(queue: Queue, **kwargs):
    best_solution, best_solutions_in_generations = genetic_algorithm(**kwargs)
    queue.put((best_solution, best_solutions_in_generations))


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


if __name__ == '__main__':
    queue = Queue()
    t = Thread()

    algorithm_settings = {
        'population_size': 100,
        'generations': 100,
        'parents_percent': 15.0,
        'mutation_size': 0.15,
        'selection_method': "tournament",
        'tournament_size': 10,
        'crossover_methods': ["one_point", "two_point"],
        'mutation_methods': ["uniform", "swap", "event_change"]
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

    finished_running = True

    path = "data/example_data.xlsx"

    _VARS = {'fig_agg': False,
             'pltFig': False}

    plot_column = [
        [sg.Canvas(key='figCanvas', background_color='#FDF6E3')],

        [sg.Multiline(key="result", size=(74, 7)),
         sg.Button("Start", enable_events=True, key="start", size=(11, 5))]
    ]

    settings_column_text_width = 23
    settings_column = [
        [sg.Text("Parametry zagadnienia", font=("Arial", 12, "bold"))],
        [sg.Text("Plik z danymi (.xlsx)"), sg.Input(enable_events=True, key="path", size=(20, 1)),
         sg.FileBrowse("Wybierz plik", target="path", initial_folder="data")],

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

        [sg.Text('Współczynnik odległości', size=(settings_column_text_width, 1)),
         sg.InputText(problem_settings['distance_coeff'], size=(24, 1), enable_events=True, key="distance_coeff")],

        [sg.Text('Wsp. f. kary - pojemność', size=(settings_column_text_width, 1)),
         sg.InputText(problem_settings['capacity_punishment_coeff'], size=(24, 1), enable_events=True,
                      key="capacity_punishment_coeff")],

        [sg.Text('Wsp. f. kary - czas trwania', size=(settings_column_text_width, 1)),
         sg.InputText(problem_settings['duration_punishment_coeff'], size=(24, 1), enable_events=True,
                      key="duration_punishment_coeff")],

        [sg.Text("_" * (settings_column_text_width + 30))],

        [sg.Text("Parametry algorytmu", font=("Arial", 12, "bold"))],

        [sg.Text('Rozmiar populacji', size=(settings_column_text_width, 1)),
         sg.InputText(algorithm_settings['population_size'], size=(24, 1), enable_events=True,
                      key="population_size")],

        [sg.Text('Ilość pokoleń', size=(settings_column_text_width, 1)),
         sg.InputText(algorithm_settings['generations'], size=(24, 1), enable_events=True,
                      key="generations")],

        [sg.Text('Rodzice [%]', size=(settings_column_text_width, 1)),
         sg.InputText(algorithm_settings['parents_percent'], size=(24, 1), enable_events=True,
                      key="parents_percent")],

        [sg.Text('Mutacja [%]', size=(settings_column_text_width, 1)),
         sg.InputText(algorithm_settings['mutation_size'] * 100, size=(24, 1), enable_events=True,
                      key="mutation_size")],

        [sg.Text('Rozmiar turnieju', size=(settings_column_text_width, 1)),
         sg.InputText(algorithm_settings['tournament_size'], size=(24, 1), enable_events=True,
                      key="tournament_size")],

        [sg.Text('Metody krzyżowania', size=(settings_column_text_width, 1))],
        [sg.Checkbox("One point", default=True, enable_events=True, key="one_point"),
         sg.Checkbox("Two point", default=True, enable_events=True, key="two_point")],

        [sg.Text('Metody mutacji', size=(settings_column_text_width, 1))],
        [sg.Checkbox("Uniform", default=True, enable_events=True, key="uniform"),
         sg.Checkbox("Swap", default=True, enable_events=True, key="swap"),
         sg.Checkbox("Event change", default=True, enable_events=True, key="event_change")]
    ]

    layout = [
        [
            sg.Column(settings_column),
            sg.Column(plot_column, element_justification="center")
        ]
    ]

    window = sg.Window("Genetic algorithm", layout, element_justification="center", finalize=True)


    def drawChart(data):
        _VARS['pltFig'] = plt.figure()
        plt.plot(data)
        plt.grid()
        plt.ylabel("Całkowity przychód")
        plt.xlabel("Generacja")
        _VARS['fig_agg'] = draw_figure(
            window['figCanvas'].TKCanvas, _VARS['pltFig'])


    def updateChart(data):
        _VARS['fig_agg'].get_tk_widget().forget()
        # plt.cla()
        plt.clf()
        plt.plot(data)
        plt.grid()
        plt.ylabel("Całkowity przychód")
        plt.xlabel("Generacja")
        _VARS['fig_agg'] = draw_figure(
            window['figCanvas'].TKCanvas, _VARS['pltFig'])


    drawChart([])

    while True:
        event, values = window.read(timeout=300)
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
                if float(values["product_price"]) < 0 or float(values["product_price"]) > 1:
                    sg.Popup("Nieprawidłowa wartość")
                    values["product_price"] = problem_settings['product_price']
                    window['product_price'].update(values["product_price"])
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

        if event == "distance_coeff":
            try:
                if float(values["distance_coeff"]) < 0:
                    sg.Popup("Nieprawidłowa wartość")
                    values["distance_coeff"] = problem_settings['distance_coeff']
                    window['distance_coeff'].update(values["distance_coeff"])
                problem_settings['distance_coeff'] = int(values["distance_coeff"])
            except ValueError:
                pass

        if event == "capacity_punishment_coeff":
            try:
                if float(values["capacity_punishment_coeff"]) < 0:
                    sg.Popup("Nieprawidłowa wartość")
                    values["capacity_punishment_coeff"] = problem_settings['capacity_punishment_coeff']
                    window['capacity_punishment_coeff'].update(values["capacity_punishment_coeff"])
                problem_settings['capacity_punishment_coeff'] = int(values["capacity_punishment_coeff"])
            except ValueError:
                pass

        if event == "duration_punishment_coeff":
            try:
                if float(values["duration_punishment_coeff"]) < 0:
                    sg.Popup("Nieprawidłowa wartość")
                    values["duration_punishment_coeff"] = problem_settings['duration_punishment_coeff']
                    window['duration_punishment_coeff'].update(values["duration_punishment_coeff"])
                problem_settings['duration_punishment_coeff'] = int(values["duration_punishment_coeff"])
            except ValueError:
                pass

        if event == "population_size":
            try:
                if int(values["population_size"]) < 0:
                    sg.Popup("Nieprawidłowa wartość")
                    values["population_size"] = algorithm_settings['population_size']
                    window['population_size'].update(values["population_size"])
                algorithm_settings['population_size'] = int(values["population_size"])
            except ValueError:
                pass

        if event == "generations":
            try:
                if int(values["generations"]) < 0:
                    sg.Popup("Nieprawidłowa wartość")
                    values["generations"] = algorithm_settings['generations']
                    window['generations'].update(values["generations"])
                algorithm_settings['generations'] = int(values["generations"])
            except ValueError:
                pass

        if event == "parents_percent":
            try:
                if float(values["parents_percent"]) < 0 or float(values["parents_percent"]) > 100:
                    sg.Popup("Nieprawidłowa wartość")
                    values["parents_percent"] = algorithm_settings['parents_percent']
                    window['parents_percent'].update(values["parents_percent"])
                algorithm_settings['parents_percent'] = float(values["parents_percent"])
            except ValueError:
                pass

        if event == "mutation_size":
            try:
                if float(values["mutation_size"]) < 0 or float(values["mutation_size"]) > 100:
                    sg.Popup("Nieprawidłowa wartość")
                    values["mutation_size"] = algorithm_settings['mutation_size'] * 100
                    window['mutation_size'].update(values["mutation_size"])
                algorithm_settings['mutation_size'] = float(values["mutation_size"]) / 100
            except ValueError:
                pass

        if event == "tournament_size":
            try:
                if int(values["tournament_size"]) < 0 or int(values["tournament_size"]) > int(
                        values["population_size"]):
                    sg.Popup("Nieprawidłowa wartość")
                    values["tournament_size"] = algorithm_settings['tournament_size']
                    window['tournament_size'].update(values["tournament_size"])
                algorithm_settings['tournament_size'] = int(values["tournament_size"])
            except ValueError:
                pass

        if event == "one_point":
            if values["one_point"] is True and "one_point" not in algorithm_settings['crossover_methods']:
                algorithm_settings['crossover_methods'].append("one_point")
            elif values["one_point"] is False:
                try:
                    algorithm_settings['crossover_methods'].remove("one_point")
                except Exception:
                    pass

        if event == "two_point":
            if values["two_point"] is True and "two_point" not in algorithm_settings['crossover_methods']:
                algorithm_settings['crossover_methods'].append("two_point")
            elif values["two_point"] is False:
                try:
                    algorithm_settings['crossover_methods'].remove("two_point")
                except Exception:
                    pass

            # TODO: zrobic sprawdzenie czy ktores jest zaznaczone

        if event == "uniform":
            if values["uniform"] is True and "uniform" not in algorithm_settings['mutation_methods']:
                algorithm_settings['mutation_methods'].append("uniform")
            elif values["uniform"] is False:
                try:
                    algorithm_settings['mutation_methods'].remove("uniform")
                except Exception:
                    pass

        if event == "swap":
            if values["swap"] is True and "swap" not in algorithm_settings['mutation_methods']:
                algorithm_settings['mutation_methods'].append("swap")
            elif values["swap"] is False:
                try:
                    algorithm_settings['mutation_methods'].remove("swap")
                except Exception:
                    pass

        if event == "event_change":
            if values["event_change"] is True and "event_change" not in algorithm_settings['mutation_methods']:
                algorithm_settings['mutation_methods'].append("event_change")
            elif values["event_change"] is False:
                try:
                    algorithm_settings['mutation_methods'].remove("event_change")
                except Exception:
                    pass

        if event == "path":
            path = values["path"]
            print(path)

        if event == "start":
            print("START")
            df = pd.read_excel(path)
            event_list = load_event_list(df)
            cities = list(df['city'].unique())
            with open('distances.json', 'r') as fp:
                distances = json.load(fp)
            if not set(cities) == set(distances.keys()):
                sg.Popup("Wczytywanie odległości pomiędzy miastami...")
                distances = driving_distances(list(df['city'].unique()))

            t = Thread(target=ga_mp, args=(queue,),
                       kwargs={**algorithm_settings, **problem_settings, **{"distances": distances}}, daemon=True)
            t.start()
            window["start"].update(disabled=True)
            finished_running = False

        if not t.is_alive() and not finished_running:
            window["start"].update(disabled=False)
            finished_running = True
            best_solution, best_solutions_in_generations = queue.get()
            print(best_solution, best_solutions_in_generations)
            updateChart(best_solutions_in_generations)
            result = ""
            for i, el in enumerate(best_solution.solution_list):
                result += f"{i + 1}. {el}\n"
            result += f"Przychód z najlepszego rozwiązania: {best_solution.overall_profit()}"
            window["result"].update(result)

    window.close()
