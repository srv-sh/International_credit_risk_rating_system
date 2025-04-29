import streamlit as st
from streamlit_option_menu import option_menu
import importlib

# Set page config at the very top
st.set_page_config(page_title="Credit Scoring Dashboard", layout="wide")

# Navigation
selected = option_menu(
    menu_title=None,
    options=["Home", "Balance-Sheet", "Income-Sheet", "Cashflow-Sheet"],
    icons=["house", "cloud-upload", "list-task", "gear"],
    orientation="horizontal"
)

# Dynamically import pages
page = None
if selected == "Home":
    page = importlib.import_module("home")
elif selected == "Balance-Sheet":
    page = importlib.import_module("pages.bs")
elif selected == "Income-Sheet":
    page = importlib.import_module("pages.is")
elif selected == "Cashflow-Sheet":
    page = importlib.import_module("pages.cfs")

# Run the selected page
if page:
    try:
        page.app()
    except Exception as e:
        st.error(f"Failed to load page: {e}")
