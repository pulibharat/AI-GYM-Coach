import streamlit as st
from services.auth.login_wall import render_login_wall


def main():

    st.set_page_config(
        page_title="AI GYM Coach",
        page_icon="🏋️‍♂️",
        layout="centered",
        initial_sidebar_state="expanded")

    if not render_login_wall():
        return  # Stop rendering the rest of the app if not logged in
    st.write("Welcome to the AI GYM Coach! You are now logged in.")
    # Here you can add the rest of your app's functionality


if __name__ == "__main__":
    main()
