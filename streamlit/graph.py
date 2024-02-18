from datetime import datetime, timedelta
import pandas as pd
import plotly_express as px
import streamlit as st
from app import App

class Graph(App):
    def __init__(self, cityid=1, kind="temp", duration=1):
        self.cityid = cityid
        self.kind = kind
        self.duration = duration

    def __get_beginning_time(self):
        current = datetime.now()
        hours = self.duration
        beginning = current - timedelta(hours=hours)
        return beginning

    def __get_beginning_time_id(self, cursor):
        beginning = self.__get_beginning_time()
        query = f"""
                        SELECT timeid
                        FROM weather_data.times
                        WHERE date_time > (%s)
                        ORDER BY timeid
                        LIMIT 1;
                        """
        values = [beginning]
        cursor.execute(query, values)
        beginning_id = cursor.fetchone()[0]
        return beginning_id

    def __get_data(self, cursor):
        beginning_id = self.__get_beginning_time_id(cursor)
        query = f"""
                SELECT {self.kind}
                FROM weather_data.weather
                WHERE cityid = %s
                    AND timeid > %s
                ORDER BY timeid;
            """
        values = (self.cityid, beginning_id)
        cursor.execute(query, values)
        rows = cursor.fetchall()
        data = self.clean_data(rows, data_type='list')

        return data

    def __get_times(self, cursor):
        beginning_timeid = self.__get_beginning_time_id(cursor)
        query = f"""
                    SELECT date_time
                    FROM weather_data.times
                    WHERE timeid > %s
                    ORDER BY timeid;
                    """
        values = [beginning_timeid]
        cursor.execute(query, values)
        rows = cursor.fetchall()
        times = self.clean_data(rows, data_type='list')

        return times

    def __get_all_data(self):
        connection = self.connect_mysql()

        data = []
        data.append(self.__get_data(cursor=connection.cursor()))
        data.append(self.__get_times(cursor=connection.cursor()))

        connection.close()
        return data

    def __create_df(self, data):
        names = [self.kind, "time"]
        df = pd.DataFrame(data, names)
        df = df.transpose()
        return df

    def __create_plot(self):
        data = self.__get_all_data()
        df = self.__create_df(data)
        plot = px.line(df, x="time", y=self.kind,
                       labels={"time": "date and time", self.kind: self.kind})
        return plot

    def run(self):
        self.plot = self.__create_plot()
        st.plotly_chart(self.plot)