import streamlit as st
from app import App

class Home(App):
    def __create_cities_columns(self):
        gsh_col, nt_col, mod_col, elt_col, hf_col = st.columns(5)
        columns = {'Gabash': gsh_col, 'Netanya': nt_col,
                   'Modiin': mod_col, 'Eilat': elt_col, 'Haifa': hf_col}
        return columns

    def __show_temp_of_city(self, city, data):
        st.header(city)
        st.write('##')
        st.write('Temperature is now:')
        city_index = self.find_city_index(city)
        st.write(str(data[city_index - 1][2]) + ' C.')

    def __show_title(self, img):
        logo_col, empty_col, title_col, logo_col1 = st.columns((1, 2, 5, 1))
        with logo_col:
            st.image(img)
        with title_col:
            st.title("Israel Weather :sun_behind_rain_cloud:")
        with logo_col1:
            st.image(img)
        st.write('---')

    def __show_cities_weather(self):
        data = self.get_current_temp()
        columns = self.__create_cities_columns()
        for city in columns:
            with columns[city]:
                self.__show_temp_of_city(city, data)

    def run(self):
        self.__show_title(self.image)
        self.__show_cities_weather()
        self.show_gif()