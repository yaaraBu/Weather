import os
import json
from dotenv import load_dotenv
import mysql.connector
from open_weather import OpenWeather

class Mysql(OpenWeather):
    def __init__(self):
        super().__init__()

    def __set_password(self):
        load_dotenv()
        self.__password = os.getenv('MYSQL_PASSWORD').strip().replace("'", "")

    def __get_new_time_id(self, cursor):
        query = "SELECT MAX(timeid) AS last_timeid FROM times;"
        cursor.execute(query)
        result = cursor.fetchone()
        last_timeid = result[0]
        return (last_timeid + 1)

    def __get_local_file_data(self, path):
        f = open(path)
        data = json.load(f)
        f.close()
        return data

    def __insert_new_time(self, cursor, data, new_timeid):
        query = """
                        INSERT INTO times (timeid ,date_time)
                        VALUES (%s, %s);
                    """
        values = (
            new_timeid,
            data['date_time']
        )
        cursor.execute(query, values)

    def __insert_new_weather(self, data, city, timeid, cursor):
        query = """
                            INSERT INTO weather(cityid, timeid, temp, feels_like, temp_min, temp_max, pressure, humidity, visibility,
                                                    wind_speed, wind_deg, rain_1h, clouds, dt, sunrise, sunset)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                            """
        values = (
            city.index,
            timeid,
            data[city.name]['main']['temp'],
            data[city.name]['main']['feels_like'],
            data[city.name]['main']['temp_min'],
            data[city.name]['main']['temp_max'],
            data[city.name]['main']['pressure'],
            data[city.name]['main']['humidity'],
            data[city.name]['visibility'],
            data[city.name]['wind']['speed'],
            data[city.name]['wind']['deg'],
            data[city.name].get('rain', {}).get('1h', 0),
            data[city.name]['clouds']['all'],
            data[city.name]['dt'],
            data[city.name]['sys']['sunrise'],
            data[city.name]['sys']['sunset'],
        )
        cursor.execute(query, values)

    def __insert_new_data_to_db(self, cursor):
        data = self.__get_local_file_data(self.get_local_path())
        new_timeid = self.__get_new_time_id(cursor)
        self.__insert_new_time(cursor, data, new_timeid)

        for city in self.cities:
            self.__insert_new_weather(data, city, new_timeid, cursor)

    def update_db(self):
        connection = self.connect()
        cursor = connection.cursor()

        self.__insert_new_data_to_db(cursor)

        connection.commit()
        connection.close()
        return

    def connect(self):
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
