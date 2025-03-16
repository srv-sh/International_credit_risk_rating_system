import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(layout="wide")

# Function to display the DataFrame and allow editing
def display_editable_dataframe(data):
    if data:
        bs_df = pd.DataFrame(data['bs']['processed_response'])  # Assuming 'bs' is the data of interest
        return bs_df
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
    st.write("### Balance Sheet")
    image = files[0]
    st.image(image, caption="Balance Sheet", use_container_width=True)

with col2:
    bs_df = display_editable_dataframe(input_data)

    if bs_df is not None:
        st.write("### Edit Financial Data")

        # Check if the dataframe is already stored in session state
        if 'bs_df' not in st.session_state:
            st.session_state.bs_df = bs_df
        else:
            bs_df = st.session_state.bs_df

        # Adding row position bar and "Add Row" button above the table
        row_col1, row_col2 = st.columns([1, 1])

        # Option to add a row
        with row_col1:
            if 'selected_index' not in st.session_state:
                st.session_state.selected_index = len(bs_df)

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
                empty_row = {col: '' for col in bs_df.columns}
                new_row_df = pd.DataFrame([empty_row])

                # Split the DataFrame and insert the new row at the specified index
                top_part = bs_df.iloc[:st.session_state.selected_index]
                bottom_part = bs_df.iloc[st.session_state.selected_index:]

                edited_df = pd.concat([top_part, new_row_df, bottom_part], ignore_index=True)

                # Save changes to session state
                st.session_state.bs_df = edited_df
                st.session_state.bs = edited_df.to_dict(orient='list')

                st.success(f"Empty row added successfully at index {st.session_state.selected_index}!")

        # Option to add a column
        with row_col2:
            column_name_input = st.text_input("Enter new column name:", "New Column")
            if st.button("Add Column"):
                # Use the input name for the new column
                new_column_name = column_name_input.strip() or f"New Column {len(bs_df.columns) + 1}"
                
                # Create a new column with empty values for all rows
                bs_df[new_column_name] = ''

                # Save changes to session state
                st.session_state.bs_df = bs_df
                st.session_state.bs = bs_df.to_dict(orient='list')

                st.success(f"New column '{new_column_name}' added successfully!")

        # Option to delete a column
        column_to_delete = st.selectbox("Select a column to delete:", bs_df.columns)

        if st.button("Delete Column"):
            # Delete the selected column
            if column_to_delete:
                bs_df.drop(columns=[column_to_delete], inplace=True)
                st.session_state.bs_df = bs_df
                st.session_state.bs = bs_df.to_dict(orient='list')

                st.success(f"Column '{column_to_delete}' deleted successfully!")

        # Reset index for display in the table
        edited_df_with_index = bs_df.reset_index(drop=False)  # Reset index and include it as a column

        # Display editable DataFrame with index shown in the UI
        edited_df = st.data_editor(
            edited_df_with_index,
            use_container_width=True,
            height=800,
            num_rows="dynamic",
            column_config={
                "index": st.column_config.NumberColumn(
                    "Index",  # Display the index as a column
                    help="Row index",
                    width="small",
                )
            }
        )

        # Save changes
        if st.button("Next"):
            # Drop the index column before saving
            edited_df_no_index = edited_df.drop(columns=["index"])

            # Convert to JSON without the index
            edited_json = edited_df_no_index.to_dict(orient='list')
            md = json_to_markdown_table(edited_json)

            input_data['bs']['raw_response']['natural_text'] = md
            st.session_state.bs_df = edited_df_no_index
            st.session_state.bs = edited_json
            st.success("Changes saved successfully as JSON!")

            def transform_and_send(data: dict, database_url: str):
                # Transforming data
                transformed_data = {
                    "url": data['bs']['pdf_url'],       
                    "prompt": data['bs']['prompt'],     
                    "page_number": 1,                   
                    "response": json.dumps(data['bs']['raw_response'])  # Serialize the raw response as a JSON string
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
            data['balance_id'] = storedb['response']['id']

            # Step 3: Save the modified data back to the JSON file
            with open('json/variables.json', 'w') as file:
                json.dump(data, file, indent=4)

            print("Key value updated successfully!")

            st.switch_page("pages/is.py")