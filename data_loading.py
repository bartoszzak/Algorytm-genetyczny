import json
import logging
import random
from time import sleep
from typing import Union, Tuple, List, Dict, Optional

import pandas as pd
import requests
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geopy.geocoders import Nominatim

from solution import *

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


def load_event_list(df: pd.DataFrame) -> List[Event]:
    event_list = []
    columns = df.columns
    for idx in range(len(df)):
        attributes = {column: df[column][idx] for column in columns[1:]}
        if isinstance(attributes['visitors'], str):
            attributes['visitors'] = [int(i) for i in attributes['visitors'].split(',')]
        else:
            attributes['visitors'] = [attributes['visitors']]

        if isinstance(attributes['parking_cost'], str):
            attributes['parking_cost'] = [int(i) for i in attributes['parking_cost'].split(',')]
        else:
            attributes['parking_cost'] = [attributes['parking_cost']]

        event_list.append(Event(df['event_id'][idx], **attributes))
    return event_list


def driving_distances(cities: Union[Tuple, List], distances: Optional[Dict] = None) -> Dict[str, Dict[str, float]]:
    if distances is None:
        distances = {city: {} for city in cities}
        unchecked_cities = cities[:]
    else:
        unchecked_cities = list(set(cities) - set(distances.keys()))
        if not unchecked_cities:
            return distances
        distances = {**distances, **{city: {} for city in unchecked_cities}}
    for city_1 in cities:
        location_1 = geocode(geolocator, city_1, 2)
        try:
            unchecked_cities.remove(city_1)
        except ValueError:
            pass
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
    with open('distances.json', 'w') as fp:
        json.dump(distances, fp)
    return distances
