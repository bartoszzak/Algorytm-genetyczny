import logging
from time import sleep
from typing import Union, Tuple, List, Dict
from copy import deepcopy
import json
import random

import networkx as nx
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import requests

user_agent = 'user_me_{}'.format(random.randint(10000, 99999))
geolocator = Nominatim(user_agent=user_agent)


def geocode(geolocator, city, sleep_sec):
    try:
        return geolocator.geocode(city)
    except GeocoderTimedOut:
        logging.info('TIMED OUT: GeocoderTimedOut: Retrying...')
        sleep(random.randint(1 * 100, sleep_sec * 100) / 100)
        return geocode(geolocator, city, sleep_sec)
    except GeocoderServiceError as e:
        logging.info('CONNECTION REFUSED: GeocoderServiceError encountered.')
        logging.error(e)
        return None
    except Exception as e:
        logging.info('ERROR: Terminating due to exception {}'.format(e))
        return None


def load_vertices(g: nx.Graph, df: pd.DataFrame):
    for idx in range(len(df)):
        columns = df.columns
        attributes = {column: df[column][idx] for column in columns[1:]}
        if isinstance(attributes['visitors'], str):
            attributes['visitors'] = [int(i) for i in attributes['visitors'].split(',')]
        else:
            attributes['visitors'] = [attributes['visitors']]
        print(attributes)
        g.add_node(df['event_id'][idx], **attributes)


def driving_distances(cities: Union[Tuple, List]):
    distances = {city: {} for city in cities}
    unchecked_cities = cities[:]
    for city_1 in cities:
        location_1 = geocode(geolocator, city_1, 2)
        unchecked_cities.remove(city_1)
        distances[city_1][city_1] = 0
        for city_2 in unchecked_cities:
            location_2 = geocode(geolocator, city_2, 2)
            r = requests.get(f"http://router.project-osrm.org/route/v1/car/{location_1.longitude},{location_1.latitude};{location_2.longitude},{location_2.latitude}?overview=false")
            routes = json.loads(r.content)
            route_1 = routes.get("routes")[0]
            distance = route_1['distance']
            print(city_1, city_2, distance)
            distances[city_1][city_2] = distance
            distances[city_2][city_1] = distance
    return distances


def add_edges(g: nx.Graph, distances: Dict):
    unchecked_nodes = deepcopy(g.nodes)
    unchecked_nodes = list(unchecked_nodes)
    for node_1 in g.nodes:
        city_1 = g.nodes[node_1]['city']
        unchecked_nodes.remove(node_1)
        for node_2 in unchecked_nodes:
            city_2 = g.nodes[node_2]['city']
            g.add_edge(node_1, node_2)
            g[node_1][node_2]['weight'] = distances[city_1][city_2]
            g.add_edge(node_2, node_1)
            g[node_2][node_1]['weight'] = distances[city_2][city_1]


G = nx.Graph()
df = pd.read_excel("data/example_data.xlsx")

load_vertices(G, df)
# distances = driving_distances(list(df['city'].unique()))
with open('distances.json', 'r') as fp:
    distances = json.load(fp)

add_edges(G, distances)
print(G.edges)
print(G.get_edge_data(0, 6))
