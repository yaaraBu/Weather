import os
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from open_weather import OpenWeather


class Drive(OpenWeather):
    def __init__(self):
        super().__init__()
        self.__client_secret = str(os.getenv('CLIENT_SECRET'))
        self.__SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __try_to_get_exist_creds(self):
        try:
            return Credentials.from_authorized_user_file("update_data/token.json", self.__SCOPES)
        except:
            return None

    def __creat_new_creds(self, creds):
        try:
            creds.refresh(Request())
        except:
            flow = InstalledAppFlow.from_client_secrets_file(self.__client_secret, self.__SCOPES)
            creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    def __get_folder_id(self, service):
        r = service.files().list(
            q="name='WeatherData' and mimeType='application/vnd.google-apps.folder'",
            spaces="drive").execute()
        return r['files'][0]['id']

    def __execute_file_to_drive(self, service):
        file_metadata = {
            "name": self.get_current_time(),
            "parents": [self.__get_folder_id(service)]}

        media = MediaFileUpload(self.get_local_path())
        service.files().create(body=file_metadata,
                               media_body=media,
                               fields="id").execute()

    def upload(self):
        drive = Drive()
        creds = drive.get_creds()
        try:
            service = build("drive", "v3", credentials=creds)
            self.__execute_file_to_drive(service)

        except HttpError as e:
            logging.info("Error: " + str(e))
            return

    def get_creds(self):
        if os.path.exists("update_data/token.json"):
            creds = self.__try_to_get_exist_creds()
        else:
            creds = None

        if not creds or not creds.valid:
            creds = self.__creat_new_creds(creds)

        return creds