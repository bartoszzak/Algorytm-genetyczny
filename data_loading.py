import logging
from time import sleep

import networkx as nx
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import requests
import json
import datetime
import random

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
        g.add_node(df['event_id'][idx], **attributes)


G = nx.Graph()
df = pd.read_excel("data/example_data.xlsx")

load_vertices(G, df)
print(G.nodes[0]['start_date'])
print(G.nodes[0]['end_date'])
print(G.nodes[0]['start_date'] - G.nodes[0]['end_date'])
print((G.nodes[0]['end_date'] - G.nodes[0]['start_date']).days)