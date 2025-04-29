import streamlit as st
from streamlit_option_menu import option_menu
import importlib

st.set_page_config(page_title="Custom Nav App", layout="wide")

# Horizontal navbar
selected = option_menu(
    menu_title=None,
    options=["Home", "Upload", "Tasks", "Settings"],
    icons=["house", "cloud-upload", "list-task", "gear"],
    orientation="horizontal"
)

# Dynamic import based on selection
if selected == "Home":
    page = importlib.import_module("home")
elif selected == "Upload":
    page = importlib.import_module("upload")
elif selected == "Tasks":
    page = importlib.import_module("tasks")
elif selected == "Settings":
    page = importlib.import_module("settings")

# Run the selected page
if page:
    page.app()  # You must define a function called `app()` inside each page
