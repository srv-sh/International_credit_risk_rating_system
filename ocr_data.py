import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import os
from dotenv import load_dotenv
import requests

load_dotenv()

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Hide menu
st.markdown("""
<style>
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.title("Home Page")
st.write("Welcome to the Home Page")

st.markdown("## Upload Image Files")

def get_images():
    """Upload multiple images"""
    uploaded_files = st.file_uploader("Upload multiple images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    return uploaded_files if uploaded_files else None

files = get_images()

if files:
    st.success(f"{len(files)} file(s) uploaded successfully")
    st.session_state.files = files
else:
    st.session_state.pop("files", None)

def hit_fastapi(files):
    """Send uploaded images to FastAPI"""
    url = "http://192.168.10.50:8000/uploadfiles"  # Ensure correct URL

    if not files or len(files) == 0:
        st.error("No files to upload.")
        return None

    # Prepare files in correct format
    files_to_upload = [('files', (file.name, file.getvalue(), file.type)) for file in files]

    try:
        response = requests.post(url, files=files_to_upload)
        response.raise_for_status()  # Raise error for HTTP 4xx/5xx
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")

    return None

# Submit button
submit = st.button("Next")

if files and submit:
    input_data = hit_fastapi(files)
    
    if input_data:
        st.session_state.input = input_data
        switch_page("bs")
    else:
        st.warning("Error processing files.")
