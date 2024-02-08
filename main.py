import json
import time
import streamlit as st
from streamlit_lottie import st_lottie
from PIL import Image
import pandas as pd
import plotly_express as px
import logging
import os
import os.path
from dotenv import load_dotenv
import mysql.connector
from decimal import Decimal

from updates import get_creds



def load_gif(file_path: str):
    with open(file_path, "r") as f:
        return json.load(f)


def connect_to_mysql():
    connection = mysql.connector.connect(
        host='127.0.0.1',
        user='yaara',
        password='YaaraBuda1',
        port='3306',
        database='weather_data'
    )
    return connection.cursor()


def get_current_temp_from_mysql():
    connection = mysql.connector.connect(
        host='127.0.0.1',
        user='yaara',
        password='YaaraBuda1',
        port='3306',
        database='weather_data'
    )
    cursor = connection.cursor()
    query = """
                SELECT timeid, cityid, temp
                FROM weather_data.weather
                ORDER BY timeid DESC, cityid
                LIMIT 5;
                """
    cursor.execute(query)
    rows = cursor.fetchall()
    data = []
    for row in rows:
        clean_row = tuple(float(value) if isinstance(value, Decimal) else value for value in row)
        data.append(clean_row)

    connection.commit()
    connection.close()
    return data


def get_history_temp(cityid):
    connection = mysql.connector.connect(
        host='127.0.0.1',
        user='yaara',
        password='YaaraBuda1',
        port='3306',
        database='weather_data'
    )
    cursor = connection.cursor()

    query = """
                SELECT temp
                FROM weather_data.weather
                WHERE cityid=(%s)
                ORDER BY timeid;
                """
    cities_list = [cityid]
    cursor.execute(query, cities_list)
    rows = cursor.fetchall()
    data = []
    for row in rows:
        clean_row = tuple(float(value) if isinstance(value, Decimal) else value for value in row)
        data.append(clean_row[0])

    query = """
                SELECT date_time
                FROM weather_data.times
                ORDER BY timeid;
                """
    cursor.execute(query)
    rows = cursor.fetchall()
    times = []
    for row in rows:
        clean_row = tuple(float(value) if isinstance(value, Decimal) else value for value in row)
        times.append(clean_row[0])

    connection.commit()
    connection.close()
    return [data, times]


def run_web(cities_index, circle_img, gif):
    data = get_current_temp_from_mysql()
    st.set_page_config(page_title="weather", page_icon=":sparkles:", layout="wide")

    menu = ["Home", "History"]
    choice = st.sidebar.radio("Menu", menu)

    if choice == "Home":

        logo_col, empty_col, title_col, logo_col1 = st.columns((1, 2, 5, 1))
        with logo_col:
            st.image(circle_img)
        with title_col:
            st.title("Israel Weather :sun_behind_rain_cloud:")
        with logo_col1:
            st.image(circle_img)
        st.write('---')

        gsh_col, nt_col, mod_col, elt_col, hf_col = st.columns(5)
        columns = {'Gabash': gsh_col, 'Netanya': nt_col,
                   'Modiin': mod_col, 'Eilat': elt_col, 'Haifa': hf_col}

        for city in columns:
            with columns[city]:
                st.header(city)
                st.write('##')

                st.write('Temperature is now:')
                st.write(str(data[cities_index[city] - 1][2]) + ' C.')

        st_lottie(gif, height=490)


    else:

        st.title("History")
        city = st.selectbox('Select city', options=['Gabash', 'Netanya',
                                                    'Modiin', 'Eilat', 'Haifa'])
        data = get_history_temp(cities_index[city])
        columns_names = ["temp", "time"]
        df = pd.DataFrame(data, columns_names)
        df = df.transpose()
        plot = px.line(df, x="time", y="temp", labels={"time": "date and time", "temp": "temperature"})
        st.plotly_chart(plot)

        st_lottie(gif, height=490)


def main():

    circle_img = Image.open("images/circle.png")
    gif = load_gif("lottie/Animation.json")

    logging.basicConfig(level=logging.INFO, filename="logging.log", filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s")

    load_dotenv()
    #add here the password YaaraBuda1 to env variable
    cities_index = {'Gabash': 1, 'Netanya': 2, 'Modiin': 3, 'Eilat': 4, 'Haifa': 5}

    while True:
        run_web(cities_index, circle_img, gif)
        time.sleep(180)
        st.rerun()



if __name__ == "__main__":
    main()