import streamlit as st
from datetime import datetime
from graph import Graph
from choice import Choice
from app import App

class History(App):
    def __get_hours_from_the_beginning_of_time(self):
        current_time = datetime.now()
        time_of_first_data = datetime.strptime('2024-02-05 16:22:00', '%Y-%m-%d %H:%M:%S')
        return (current_time - time_of_first_data).total_seconds() / 3600

    def __find_real_kind(self, kind):
        meaning = {'Tempetatures': 'temp', 'Humidity': 'humidity', 'Wind Speed': 'wind_speed'}
        return meaning[kind]

    def __find_num_of_hours(self, duration):
        if duration == 'All':
            return self.__get_hours_from_the_beginning_of_time()
        else:
            hours = {'Last Hour': 1, 'Last 24 Hours': 24, 'Last 3 Days': 72, 'Last Week': 168}
            return hours[duration]

    def __take_user_choices(self):
        city = st.selectbox('Select City', options=['Gabash', 'Netanya',
                                                           'Modiin', 'Eilat', 'Haifa'])
        kind = st.selectbox('Select Graph', options=['Tempetatures', 'Humidity', 'Wind Speed'])
        duration = st.selectbox('Select Duration', options=['Last Hour', 'Last 24 Hours',
                                                                   'Last 3 Days', 'Last Week', 'All'])
        return Choice(city, kind, duration)

    def __set_graph(self, choice):
        graph = Graph()
        graph.cityid = self.find_city_index(choice.city)
        graph.kind = self.__find_real_kind(choice.kind)
        graph.duration = self.__find_num_of_hours(choice.duration)
        return graph

    def __define_graph_by_user(self):
        choice = self.__take_user_choices()
        graph = self.__set_graph(choice)
        return graph

    def run(self):
        st.title("History")

        graph = self.__define_graph_by_user()
        graph.run()
        self.show_gif()