import requests
import json
import time
import streamlit as st
from streamlit_lottie import st_lottie
from PIL import Image
import os



def get_live_temp(lat, lon):
    url = base_url + '&lat=' + str(lat) + '&lon=' + str(lon)
    r = requests.get(url)

    if r.status_code == 200:
        weather_data = r.json()
    else:
        print(f"Error: {r.status_code}")
        return None

    return weather_data


def load_gif(file_path: str):
    with open(file_path, "r") as f:
        return json.load(f)


api_key = str(os.environ.get('API_OPENWEATHER'))
sun_img = Image.open("images/sun.png")
circle_img = Image.open("images/circle.png")
gif = load_gif("lottie/Animation.json")
base_url = ("https://api.openweathermap.org/data/2.5/weather?"
               "appid=" + api_key + "&units=metric")
cities_loc = {'Gabash':[32.078121, 34.847019], 'Netanya':[32.329369,34.856541],
              'Modiin':[31.899160, 35.007408], 'Eilat':[29.557669, 34.951923], 'Haifa':[32.817280, 34.988762]}
cities_wether = {}

while True:
    for city in cities_loc:
        data = get_live_temp(cities_loc[city][0], cities_loc[city][1])
        cities_wether[city] = data


    st.set_page_config(page_title="weather", page_icon=":sparkles:", layout="wide")


    logo_col, empty_col, title_col, logo_col1 = st.columns((1, 2, 5, 1))
    with logo_col:
        st.image(circle_img)
    with title_col:
        st.title("Israel Weather :sun_behind_rain_cloud:")
    with logo_col1:
        st.image(circle_img)
    st.write('---')


    gsh_col, nt_col, mod_col, elt_col, hf_col = st.columns(5)
    columns = {'Gabash':gsh_col, 'Netanya':nt_col,
              'Modiin':mod_col, 'Eilat':elt_col, 'Haifa':hf_col}

    for city in columns:
        with columns[city]:
            st.header(city)
            st.write('##')
            st.write('Temperature is now: ' + str(cities_wether[city]['main']['temp']) + ' C.')
            st.write('Feels like: ' + str(cities_wether[city]['main']['feels_like']) + ' C.')


    st_lottie(gif, height=500)
    #st.image(sun_img)

    time.sleep(60)
    st.experimental_rerun()
