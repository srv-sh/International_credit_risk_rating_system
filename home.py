    
# def app():
# home.py
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import os
from dotenv import load_dotenv
from source.main_function import Main  
import os
import torch
from streamlit_option_menu import option_menu
import importlib

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)] 

# or simply:
torch.classes.__path__ = []
load_dotenv()

hide_menu = """
<style>
#MainMenu {
    visibility: hidden;
}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)


# Create a temporary directory to store the uploaded files
temp_dir = os.getenv('GET_FILE')
if temp_dir:  # Ensure temp_dir is valid
    os.makedirs(temp_dir, exist_ok=True)
else:
    st.error("Temporary directory is not set. Please check your environment variables.")

st.title("Home Page")
st.write("Welcome to the Home Page")

# User details input
st.markdown("## User Information")
name = st.text_input("Full Name")
address = st.text_area("Address")
phone = st.text_input("Phone Number")
email = st.text_input("Email Address")

st.markdown("## Image Files Upload")

def get_images():
    # Upload images
    balance_sheet_img = st.file_uploader("Please Upload the Balance Sheet Image", type=["png", "jpg", "jpeg"], key="img1")
    cash_flow_sheet_img = st.file_uploader("Please Upload the Cash Flow Sheet Image", type=["png", "jpg", "jpeg"], key="img2")
    profit_loss_sheet_img = st.file_uploader("Please Upload the Profit-Loss Sheet Image", type=["png", "jpg", "jpeg"], key="img3")

    return balance_sheet_img, cash_flow_sheet_img, profit_loss_sheet_img

def get_file():
    # Get the uploaded images
    sheet = get_images()
    
    # Check if all files are uploaded
    if sheet and sheet[0] and sheet[1] and sheet[2]:
        st.success("Files uploaded successfully")
        return sheet
    else:
        st.warning("Please upload all required files.")
        return None

files = get_file()

st.session_state.files = files

submit = st.button("Next")

if files and submit:
    if all(files) and name and address and phone and email:
        main_program = Main()

        input_data = main_program.hit_fastapi(files)

        if input_data:
            st.session_state.input = input_data
            switch_page("bs")
            # page = importlib.import_module("pages.bs")
            # page.app()


            # intermediate_values = main_program.intermediate_values(input_data)
            # print(intermediate_values)

            # inter_result = main_program.intermediate_result(input_data, intermediate_values)

            # output = main_program.final_output(inter_result)

            # st.session_state.output = output

            # print("Output:")
            # print(output)

            # switch_page("display")

    else:
        st.warning("Please upload all files and fill in all required details.")
