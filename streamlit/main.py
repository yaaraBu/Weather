import time
import streamlit as st
import logging
from home import Home
from history import History


def create_menu():
    menu = ["Home", "History"]
    choice = st.sidebar.radio("Menu", menu)
    return choice

def run_app():
    st.set_page_config(page_title="weather", page_icon=":sparkles:", layout="wide")

    menu_choice = create_menu()
    page = Home() if menu_choice == "Home" else History()
    page.run()

def main():
    logging.basicConfig(level=logging.INFO, filename="streamlit/logging.log", filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s")

    while True:
        run_app()
        time.sleep(180)
        st.rerun()


if __name__ == "__main__":
    main()