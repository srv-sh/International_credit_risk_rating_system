import streamlit as st
from source import api_client
import pandas as pd
import requests
import json

st.set_page_config(layout="wide")

# Function to display and manage the editable DataFrame
def display_editable_dataframe(data, key):
    if key not in data:
        st.error(f"Key '{key}' not found in input data.")
        return None

    if 'processed_response' not in data[key]:
        st.error(f"Key 'processed_response' not found in '{key}'.")
        return None

    df = pd.DataFrame(data[key]['processed_response'])
    
    # Ensure the index is displayed as a column
    df = df.reset_index().rename(columns={"index": "Row Index"})
    
    return df

def json_to_markdown_table(json_data):
    """Converts JSON to a Markdown table."""
    columns = list(json_data.keys())
    rows = zip(*[json_data[col] for col in columns])

    markdown = "| " + " | ".join(columns) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(columns)) + " |\n"
    
    for row in rows:
        markdown += "| " + " | ".join(str(cell) if cell != '' else ' ' for cell in row) + " |\n"
    
    return markdown

st.title("Financial Document Processing")

# Load input data from session state
if 'input' not in st.session_state:
    st.error("Input data not found in session state.")
    st.stop()
else:
    input_data = st.session_state.input

# Load files (images) from session state
if 'files' not in st.session_state:
    st.error("Files not found in session state.")
    st.stop()
else:
    files = st.session_state.files

# Debugging: Check available document keys
st.write("Available document keys:", list(input_data.keys()))

# Loop through each document
for i, (key, data) in enumerate(input_data.items()):
    st.write(f"### Document: {key}")
    
    # Display image
    col1, col2 = st.columns(2)
    with col1:
        if i < len(files):
            st.image(files[i], caption=f"Document {key}", use_container_width=True)
        else:
            st.warning(f"No image found for {key}")

    # Display and edit DataFrame
    with col2:
        df = display_editable_dataframe(input_data, key)
        if df is not None:
            st.write("### Edit Financial Data")

            # Ensure session state stores dataframe
            if f"{key}_df" not in st.session_state:
                st.session_state[f"{key}_df"] = df
            else:
                df = st.session_state[f"{key}_df"]

            # Add Row Button with Index Selection
            index_to_add = st.number_input(f"Enter index to add row in {key}:", min_value=0, max_value=len(df), value=len(df), step=1)
            if st.button(f"Add Row at Index {index_to_add} in {key}"):
                new_row = {col: '' for col in df.columns}
                df = pd.concat([df.iloc[:index_to_add], pd.DataFrame([new_row]), df.iloc[index_to_add:]]).reset_index(drop=True)
                df["Row Index"] = df.index  # Update index column
                st.session_state[f"{key}_df"] = df
                st.success(f"Empty row added at index {index_to_add} in {key}!")

            # Add Column Feature
            new_column_name = st.text_input(f"Enter new column name for {key}:", "New Column")
            if st.button(f"Add Column to {key}"):
                if new_column_name and new_column_name not in df.columns:
                    df[new_column_name] = ''
                    st.session_state[f"{key}_df"] = df
                    st.success(f"New column '{new_column_name}' added to {key}!")

            # Delete Column Feature
            column_to_delete = st.selectbox(f"Select a column to delete from {key}:", df.columns)
            if st.button(f"Delete Column from {key}"):
                df.drop(columns=[column_to_delete], inplace=True)
                st.session_state[f"{key}_df"] = df
                st.success(f"Column '{column_to_delete}' deleted from {key}!")

            # Editable DataFrame
            edited_df = st.data_editor(df, use_container_width=True, height=500, num_rows="dynamic")

            # Ensure index column adapts dynamically
            edited_df["Row Index"] = range(len(edited_df))

            # Save Changes
            if st.button(f"Save Changes for {key}"):
                edited_json = edited_df.drop(columns=["Row Index"]).to_dict(orient='list')
                input_data[key]['raw_response']['natural_text'] = json_to_markdown_table(edited_json)
                st.session_state[f"{key}_df"] = edited_df
                st.session_state[key] = edited_json
                st.success(f"Changes saved for {key}!")

# Function to store data in database
def transform_and_send(data, database_url):
    results = {}
    for key, doc_data in data.items():
        transformed_data = {
            "url": doc_data.get('pdf_url', ''),
            "prompt": doc_data.get('prompt', ''),
            "page_number": 1,
            "response": json.dumps(doc_data.get('raw_response', {}))
        }

        results[key] = api_client.store(database_url, transformed_data)

    return results

# Store all documents in the database
if st.button("Upload"):
    url = "store_ocr_data"
    db_response = transform_and_send(input_data, url)

    # Debugging: Show database response
    st.write("Database Response:", db_response)

    # Update local JSON file with the balance_id for each document
    try:
        with open('json/variables.json', 'r') as file:
            json_data = json.load(file)

        for key, response in db_response.items():
            if response['status'] == 'success' and 'id' in response['response']:
                json_data[f"{key}_balance_id"] = response['response']['id']

        with open('json/variables.json', 'w') as file:
            json.dump(json_data, file, indent=4)

        st.success("All documents uploaded and local JSON updated successfully!")
    except Exception as e:
        st.error(f"Error updating local JSON file: {str(e)}")
