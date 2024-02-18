import os
import os.path
from dotenv import load_dotenv
import mysql.connector
from decimal import Decimal
import json
from PIL import Image
from abc import ABC, abstractmethod
from streamlit_lottie import st_lottie

class App(ABC):
    def __init__(self):
        self.gif = "streamlit/lottie/Animation.json"
        self.image = Image.open("streamlit/images/circle.png")

    @abstractmethod
    def run(self):
        pass

    def __set_password(self):
        load_dotenv()
        self.__password = os.getenv('MYSQL_PASSWORD').strip().replace("'", "")

    def connect_mysql(self):
        #Pay attention to close the returned connection
        #   with connection.close() after using this method.
        self.__set_password()
        params = {'host':'127.0.0.1',
            'user':'yaara',
            'password':self.__password,
            'port':'3306',
            'database':'weather_data'}
        connection = mysql.connector.connect(**params)
        return connection

    def __get_all_cities_latest_temp(self, cursor):
        query = """
                        SELECT timeid, cityid, temp
                        FROM weather_data.weather
                        ORDER BY timeid DESC, cityid
                        LIMIT 5;
                        """
        cursor.execute(query)
        rows = cursor.fetchall()
        data = self.clean_data(rows, data_type='list of lists')
        return data

    def get_current_temp(self):
        connection = self.connect_mysql()
        data = self.__get_all_cities_latest_temp(cursor=connection.cursor())
        connection.close()
        return data

    def find_city_index(self, city):
        # The indexes were chosen randomly. They match the indexes in the data in Mysql.
        cities_index = {'Gabash': 1, 'Netanya': 2, 'Modiin': 3, 'Eilat': 4, 'Haifa': 5}
        return cities_index[city]

    def clean_data(self, rows, data_type):
        data = []
        for row in rows:
            clean_row = tuple(float(value) if isinstance(value, Decimal) else value for value in row)
            data.append(clean_row[0] if data_type=='list' else clean_row)
        return data

    def show_gif(self):
        with open(self.gif, "r") as f:
            gif = json.load(f)
        f.close()
        st_lottie(gif, height=490)