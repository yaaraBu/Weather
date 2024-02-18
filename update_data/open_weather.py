import logging
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from city import City


class OpenWeather:
    def __init__(self):
        self.cities = self.__def_cities()
        self.__base_url = self.__def_base_url()
        # Change this into a path in your device. Doesn't really matter where.
        self.__local_path = "/home/bina/Desktop/GitHubYaara/single_data.json"

    def get_local_path(self):
        return self.__local_path

    def __def_base_url(self):
        load_dotenv()
        api_key = os.getenv('API_OPENWEATHER')
        return ("https://api.openweathermap.org/data/2.5/weather?"
                         "appid=" + str(api_key) + "&units=metric")

    def __def_cities(self):
        cities = []
        cities.append(City('Gabash', 32.078121, 34.847019, 1))
        cities.append(City('Netanya', 32.329369, 34.856541, 2))
        cities.append(City('Modiin', 31.899160, 35.007408, 3))
        cities.append(City('Eilat', 29.557669, 34.951923, 4))
        cities.append(City('Haifa', 32.817280, 34.988762, 5))
        return cities

    def __get_data_from_request(self, request):
        if request.status_code == 200:
            return request.json()
        else:
            logging.error(f"Error: {request.status_code}")
            return None

    def __get_data_of_one_city(self, city):
        url = self.__base_url + '&lat=' + str(city.lat) + '&lon=' + str(city.lon)
        r = requests.get(url)
        return self.__get_data_from_request(r)

    def __add_time_to_data(self, cities_weather):
        cities_weather["date_time"] = self.get_current_time()
        return cities_weather

    def __get_live_temp(self):
        cities_weather = {}
        for city in self.cities:
            cities_weather[city.name] = self.__get_data_of_one_city(city)
        cities_weather = self.__add_time_to_data(cities_weather)
        return cities_weather

    def get_current_time(self):
        now = datetime.now()
        return now.isoformat(timespec="minutes")

    def save_locally(self):
        cities_weather = self.__get_live_temp()
        with open(self.get_local_path(), "w") as new_file:
            new_file.truncate()
            json.dump(cities_weather, new_file)