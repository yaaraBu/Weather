import io
import requests
import json
import time
from datetime import datetime
import os
import os.path
from dotenv import load_dotenv
import logging
import mysql.connector

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload



#getting from OpenWeather new data and save it into a dict: {city_name:data}
def get_live_temp(cities_loc, base_url):
    cities_weather = {}

    for city in cities_loc:
        url = base_url + '&lat=' + str(cities_loc[city][0]) + '&lon=' + str(cities_loc[city][1])
        r = requests.get(url)

        if r.status_code == 200:
            weather_data = r.json()
        else:
            print(f"Error: {r.status_code}")
            return None

        cities_weather[city] = weather_data

    return cities_weather


#saving the existing data to a local file
def save_single_data(cities_weather, single_filename):
    now = datetime.now()
    cities_weather["date_time"] = now.isoformat(timespec="minutes")

    with open(single_filename, "w") as new_file:
        new_file.truncate()
        json.dump(cities_weather, new_file)

    return


#upload the local file to drive
def upload_single_to_drive(single_file_path, creds):

    if os.stat(single_file_path).st_size == 0:
        return

    now = datetime.now()
    date_time = now.isoformat(timespec="minutes")

    try:
        service = build("drive", "v3", credentials=creds)

        r = service.files().list(
            q="name='WeatherData' and mimeType='application/vnd.google-apps.folder'",
            spaces="drive").execute()
        folder_id = r['files'][0]['id']
        file_metadata = {
            "name": date_time,
            "parents": [folder_id]}

        media = MediaFileUpload(single_file_path)
        service.files().create(body=file_metadata,
                               media_body=media,
                               fields="id").execute()
        return

    except HttpError as e:
        logging.info("Error: " + str(e))
        return


def update_mysql_db(cities_index, single_file_path):
    if os.stat(single_file_path).st_size == 0:
        return

    connection = mysql.connector.connect(
        host='127.0.0.1',
        user='yaara',
        password='YaaraBuda1',
        port='3306',
        database='weather_data'
    )
    cursor = connection.cursor()

    query = "SELECT MAX(timeid) AS last_timeid FROM times;"
    cursor.execute(query)
    result = cursor.fetchone()
    last_timeid = result[0]
    new_timeid = last_timeid + 1
    f = open(single_file_path)
    data = json.load(f)

    query = """
                INSERT INTO times (timeid ,date_time)
                VALUES (%s, %s);
            """
    values = (
        new_timeid,
        data['date_time']
    )
    cursor.execute(query, values)

    for city in cities_index:
        query = """
                    INSERT INTO weather(cityid, timeid, temp, feels_like, temp_min, temp_max, pressure, humidity, visibility,
                                            wind_speed, wind_deg, rain_1h, clouds, dt, sunrise, sunset)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
        values = (
            cities_index[city],
            new_timeid,
            data[city]['main']['temp'],
            data[city]['main']['feels_like'],
            data[city]['main']['temp_min'],
            data[city]['main']['temp_max'],
            data[city]['main']['pressure'],
            data[city]['main']['humidity'],
            data[city]['visibility'],
            data[city]['wind']['speed'],
            data[city]['wind']['deg'],
            data[city].get('rain', {}).get('1h', 0),
            data[city]['clouds']['all'],
            data[city]['dt'],
            data[city]['sys']['sunrise'],
            data[city]['sys']['sunset'],
        )
        cursor.execute(query, values)

    connection.commit()
    connection.close()
    f.close()
    return


def read_data_from_drive(creds, cities_loc, single_file_path):
    try:
        service = build("drive", "v3", credentials=creds)

        r = service.files().list(
            q="name='WeatherData' and mimeType='application/vnd.google-apps.folder'",
            spaces="drive").execute()
        folder_id = r['files'][0]['id']

        query = f"parents = '{folder_id}'"
        r = service.files().list(q=query).execute()
        files = r.get('files')
        nextPageToken = r.get('NextPageToken')

        all_temperatures = []

        while nextPageToken:
            r = service.files().list(q=query).execute()
            files.extend(r.get('files'))
            nextPageToken = r.get('NextPageToken')

        for file in files:
            r = service.files().get_media(fileId=file["id"])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fd=fh, request=r)

            done = False
            while not done:
                done = downloader.next_chunk()

            fh.seek(0)

            with open(os.path.join(single_file_path), "wb") as f:
                f.write(fh.read())
                f.close()

            f = open(single_file_path)
            try:
                data = json.load(f)
            except:
                logging.info(str(file["name"]) + ' has an error')

            temperatures = {}
            for city in cities_loc:
                temperatures[city] = data[city]["main"]["temp"]
            temperatures["date_time"] = data["date_time"]

            all_temperatures.append(temperatures)

        all_temperatures_sorted = sorted(all_temperatures, key=lambda d:d["date_time"])
        return all_temperatures_sorted


    except HttpError as e:
        logging.info("Error: " + str(e))
        return None


def get_creds(SCOPES, client_secret):
    if os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        except:
            creds = None

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            # If the credentials are there but they're expired, refresh them.
            creds.refresh(Request())
        else:
            # If we don't have credentials, create new.
            flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def update_data(cities_loc, cities_index, base_url, single_file_path, creds):
    cities_weather = get_live_temp(cities_loc, base_url)

    temperatures = {}
    for city in cities_weather:
        temperatures[city] = cities_weather[city]['main']['temp']

    save_single_data(cities_weather, single_file_path)
    logging.info('Data updated successfully')
    update_mysql_db(cities_index, single_file_path)
    logging.info('MySql updated successfully')
    upload_single_to_drive(single_file_path, creds)
    logging.info("Uploaded to drive successfully")

    return


def main():
    logging.basicConfig(level=logging.INFO, filename="logging.log", filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s")

    load_dotenv()
    api_key = os.getenv('API_OPENWEATHER')
    client_secret = str(os.getenv('CLIENT_SECRET'))

    # Change this to a path in your device.
    single_file_path = "/home/bina/Desktop/GitHubYaara/single_data.json"

    base_url = ("https://api.openweathermap.org/data/2.5/weather?"
                "appid=" + str(api_key) + "&units=metric")
    cities_loc = {'Gabash': [32.078121, 34.847019], 'Netanya': [32.329369, 34.856541],
                  'Modiin': [31.899160, 35.007408], 'Eilat': [29.557669, 34.951923], 'Haifa': [32.817280, 34.988762]}
    cities_index = {'Gabash': 1, 'Netanya': 2, 'Modiin': 3, 'Eilat': 4, 'Haifa': 5}
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    creds = get_creds(SCOPES, client_secret)

    while True:
        update_data(cities_loc, cities_index, base_url, single_file_path, creds)
        time.sleep(180)


if __name__ == "__main__":
    main()