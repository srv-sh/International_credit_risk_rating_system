import streamlit as st
import json
import pandas as pd
from tabulate import tabulate  # Ensure tabulate is installed: pip install tabulate
from io import StringIO
from collections import defaultdict
from source.main_function import Main
import json
import requests

st.set_page_config(layout="wide")  # Ensures the app uses the full width of the page

# files = ["aci1.png", "aci2.png", "aci3.png"]

# Function to display the DataFrame and allow editing
def display_editable_dataframe(data):
    if data:
        cfs_df = pd.DataFrame(data['cfs']['processed_response'])  # Assuming 'is' is the data of interest
        return cfs_df
    else:
        return None
    

def json_to_markdown_table(json_data):
    """
    Converts a JSON object with column names as keys to a Markdown table.
    
    Args:
        json_data (dict): A dictionary where keys are column names and values are lists of row values.

    Returns:
        str: A Markdown formatted table as a string.
    """
    # Extract column names and rows
    columns = list(json_data.keys())
    rows = zip(*[json_data[col] for col in columns])

    # Prepare the header row
    markdown = "| " + " | ".join(columns) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(columns)) + " |\n"
    
    # Prepare data rows
    for row in rows:
        row_values = [str(cell) if cell != '' else ' ' for cell in row]
        markdown += "| " + " | ".join(row_values) + " |\n"
    
    return markdown


st.title("Financial Data Table")

# Load session state data
if 'input' not in st.session_state:
    st.error("Input data not found")
else:
    input_data = st.session_state.input

if 'files' not in st.session_state:
    st.error("Files not found")
else:
    files = st.session_state.files

# Display image and DataFrame
col1, col2 = st.columns(2)

with col1:
    st.write("### Cashflow Sheet")
    image = files[2]
    st.image(image, caption="Cashflow Sheet", use_container_width=True)

with col2:
    cfs_df = display_editable_dataframe(input_data)

    if cfs_df is not None:
        st.write("### Edit Financial Data")

        # Check if the dataframe is already stored in session state
        if 'cfs_df' not in st.session_state:
            st.session_state.cfs_df = cfs_df
        else:
            cfs_df = st.session_state.cfs_df

        # Adding row position bar and "Add Row" button above the table
        row_col1, row_col2 = st.columns([1, 1])

        # Option to add a row
        with row_col1:
            if 'selected_index' not in st.session_state:
                st.session_state.selected_index = len(cfs_df)

            # Input box for index display (editable)
            selected_index = st.text_input(
                "Index to add row:", 
                value=str(st.session_state.selected_index)
            )

            # Update session state when the index is edited manually
            if selected_index.isdigit():
                st.session_state.selected_index = int(selected_index)

            # Add the row at the selected index when button is clicked
            if st.button("Add Row"):
                # Create an empty row with the same columns as the DataFrame
                empty_row = {col: '' for col in cfs_df.columns}
                new_row_df = pd.DataFrame([empty_row])

                # Split the DataFrame and insert the new row at the specified index
                top_part = cfs_df.iloc[:st.session_state.selected_index]
                bottom_part = cfs_df.iloc[st.session_state.selected_index:]

                edited_df = pd.concat([top_part, new_row_df, bottom_part], ignore_index=True)

                # Save changes to session state
                st.session_state.cfs_df = edited_df
                st.session_state.cfs = edited_df.to_dict(orient='list')

                st.success(f"Empty row added successfully at index {st.session_state.selected_index}!")

            
        # Option to add a column
        with row_col2:
            column_name_input = st.text_input("Enter new column name:", "New Column")
            if st.button("Add Column"):
                # Use the input name for the new column
                new_column_name = column_name_input.strip() or f"New Column {len(cfs_df.columns) + 1}"
                
                # Create a new column with empty values for all rows
                cfs_df[new_column_name] = ''

                # Save changes to session state
                st.session_state.cfs_df = cfs_df
                st.session_state.cfs = cfs_df.to_dict(orient='list')

                st.success(f"New column '{new_column_name}' added successfully!")

        

        # Option to delete a column
        column_to_delete = st.selectbox("Select a column to delete:", cfs_df.columns)

        if st.button("Delete Column"):
            # Delete the selected column
            if column_to_delete:
                cfs_df.drop(columns=[column_to_delete], inplace=True)
                st.session_state.cfs_df = cfs_df
                st.session_state.cfs = cfs_df.to_dict(orient='list')

                st.success(f"Column '{column_to_delete}' deleted successfully!")

        # Reset index for display in the table
        edited_df_with_index = cfs_df.reset_index()  # Reset index so it's included as a column

        # Display editable DataFrame
        edited_df = st.data_editor(edited_df_with_index, use_container_width=True, height=800, num_rows="dynamic")

        # Track the clicked index and update selected_index in session state
        if edited_df is not None and 'selected_index' in st.session_state:
            # Capture index click event
            row_click = st.session_state.selected_index
            st.session_state.selected_index = row_click
            selected_index = row_click

        # Save changes
        if st.button("Save Changes"):
            edited_df_no_index = edited_df.drop(columns=['index'], errors='ignore')  # Drop 'index' column if present

            # Convert to JSON without the index
            edited_json = edited_df_no_index.to_dict(orient='list')
            md = json_to_markdown_table(edited_json)

            input_data['cfs']['raw_response']['natural_text'] = md
            st.session_state.cfs_df = edited_df
            st.session_state.cfs = edited_json
            st.success("Changes saved successfully as JSON!")

            def transform_and_send(data: dict, database_url: str):
                # Transforming data
                transformed_data = {
                    "url": data['cfs']['pdf_url'],       
                    "prompt": data['cfs']['prompt'],     
                    "page_number": 1,                   
                    "response": json.dumps(data['cfs']['raw_response'])  # Serialize the raw response as a JSON string
                }

                # Log the transformed data to verify it's correct
                print(f"Sending transformed data: {json.dumps(transformed_data, indent=2)}")

                # Sending transformed data to the database URL
                try:
                    response = requests.post(database_url, json=transformed_data)
                    response.raise_for_status()
                    return {'status': 'success', 'response': response.json()}
                except requests.exceptions.RequestException as e:
                    return {'status': 'error', 'error': str(e)}

            # Example URL
            url = "http://192.168.10.50:8000/store_ocr_data"

            storedb = transform_and_send(input_data, url)
            print(f"THE DATABASE RESPONSE IS: {storedb}")

            # Step 1: Load the JSON file
            with open('json/variables.json', 'r') as file:
                data = json.load(file)

            # Step 2: Modify the value of a specific key
            data['cash_id'] = storedb['response']['id']

            # Step 3: Save the modified data back to the JSON file
            with open('json/variables.json', 'w') as file:
                json.dump(data, file, indent=4)

            print("Key value updated successfully!")



    if st.button("Next"):

        if 'bs' in st.session_state:
            bs = st.session_state.bs
        else:
            st.error("bs not found")

        if 'pls' in st.session_state:
            pls = st.session_state.pls
        else:
            st.error("cfs not found")

        if 'cfs' in st.session_state:
            cfs = st.session_state.cfs
        else:
            st.error("cfs not found")

        json_list = [bs, pls, cfs]

        # Merge values into lists
        # Merging logic
        merged_json = {}
        for json_obj in json_list:
            for key, value in json_obj.items():
                if key not in merged_json:
                    merged_json[key] = value if isinstance(value, list) else [value]
                else:
                    if isinstance(value, list):
                        merged_json[key].extend(value)  # Add elements if already a list
                    else:
                        merged_json[key].append(value)  # Convert single value to list



        def merge_keys(data):
            # Create a dictionary to store merged keys
            merged_data = defaultdict(list)

            # Sort keys by length to ensure substrings come before full strings
            keys = sorted(data.keys(), key=len)

            visited = set()  # Track visited keys

            for i, key1 in enumerate(keys):
                if key1 in visited:
                    continue
                merged_data[key1] = data[key1]
                for key2 in keys[i + 1:]:
                    if key2 in visited:
                        continue
                    if key1 in key2:  # If key1 is a substring of key2
                        # Merge data of key2 into key1
                        if isinstance(data[key2], list):
                            merged_data[key1].extend(data[key2])
                        else:
                            merged_data[key1].append(data[key2])
                        visited.add(key2)  # Mark key2 as visited

            # Return the merged data as a normal dictionary
            return dict(merged_data)

        merged_json = merge_keys(merged_json)

        print("THE MERGE JSON IS: ---------------------------------------")
        print("-------------------------------------------------------------------------")
        print(merged_json)

        st.session_state.input = merged_json

        main_program = Main()
        intermediate_values = main_program.intermediate_values(merged_json)
        inter_result = main_program.intermediate_result(merged_json, intermediate_values)
        output = main_program.final_output(inter_result)

        st.session_state.output = output
        st.write("### Processed Output:")
        st.json(output)

        st.switch_page("pages/parameters.py")