import time
import logging
from drive import Drive
from sql_data import Mysql
from open_weather import OpenWeather


def update_data():
    open_weather = OpenWeather()

    open_weather.save_locally()
    logging.info('Data updated locally')

    Mysql().update_db()
    logging.info('MySql updated successfully')

    Drive().upload()
    logging.info("Uploaded to drive successfully")

def main():
    logging.basicConfig(level=logging.INFO, filename="update_data/logging.log", filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s")

    while True:
        update_data()
        time.sleep(180)


if __name__ == "__main__":
    main()