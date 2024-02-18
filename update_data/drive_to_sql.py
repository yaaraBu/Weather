import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
import json
import logging
from googleapiclient.errors import HttpError

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
                logging.error(str(file["name"]) + ' has an error')

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