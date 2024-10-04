import json
import requests
import folium
import os
from dotenv import load_dotenv
from flask import Flask
from geopy.distance import lonlat, distance


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat

def load_data():
    with open('coffee.json', 'r', encoding='CP1251') as my_file:
        coffee_json = my_file.read()
        return coffee_json


def calc_distance(coffee_map_info):
    coffee_distance_info = []

    for i, value in enumerate(coffee_map_info):
        coffee_geo = coffee_map_info[i]['geoData']['coordinates']
        coffee = {
            'title': coffee_map_info[i]['Name'],
            'distance': distance(lonlat(*user_coords), lonlat(*coffee_geo)).km,
            'latitude': coffee_map_info[i]['Latitude_WGS84'],
            'longitude': coffee_map_info[i]['Longitude_WGS84'],
        }
        coffee_distance_info.append(coffee)

    return coffee_distance_info


def get_coffee_distance(coffee_distance_info):
    return coffee_distance_info['distance']


def create_map(coffee_distance_info):
    nearest_coffee = sorted(coffee_distance_info, key=get_coffee_distance)

    moscow_map = folium.Map(location=(55.7522, 37.6156))

    for i, value in enumerate(nearest_coffee[:5]):
        folium.Marker(
            location=[nearest_coffee[i]['latitude'], nearest_coffee[i]['longitude']],
            tooltip="Click me!",
            popup=nearest_coffee[i]['title'],
            icon=folium.Icon(color="darkred"),
        ).add_to(moscow_map)

        folium.Marker(
            location=[user_coords[1], user_coords[0]],
            tooltip="Я",
            popup="Моё местоположение",
            icon=folium.Icon(color="green"),
        ).add_to(moscow_map)

    moscow_map.save("index.html")


def hello_world():
    with open('index.html') as file:
        return file.read()


if __name__ == '__main__':
    load_dotenv()
    apikey = os.getenv('YANDEX_API')

    coffee_map_info = json.loads(load_data())

    user_geo = input("Где вы находитесь? ")
    user_coords = fetch_coordinates(apikey, user_geo)

    create_map(calc_distance(coffee_map_info))
    
    app = Flask(__name__)
    app.add_url_rule('/', 'hello', hello_world)
    app.run('0.0.0.0')
