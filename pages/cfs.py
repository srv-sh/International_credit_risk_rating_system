    
# def app():
import streamlit as st
import json
import pandas as pd
from tabulate import tabulate  # Ensure tabulate is installed: pip install tabulate
from io import StringIO
from collections import defaultdict
from source.main_function import Main
import json
import requests
import importlib

# st.set_page_config(layout="wide")  # Ensures the app uses the full width of the page

def display_editable_dataframe(data):
    if data and 'cfs' in data and 'processed_response' in data['cfs']:
        processed_data = data['cfs']['processed_response']

        # Convert list of dicts into DataFrame
        cfs_df = pd.DataFrame(processed_data)

        # Optional: Reorder columns to show "Particulars" first if it exists
        columns = cfs_df.columns.tolist()
        if "Particulars" in columns:
            columns.remove("Particulars")
            cfs_df = cfs_df[["Particulars"] + sorted(columns)]

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




# Load and store dataframe in session state
cfs_df = display_editable_dataframe(input_data)
if cfs_df is not None:
    if 'cfs_df' not in st.session_state:
        st.session_state.cfs_df = cfs_df
    else:
        cfs_df = st.session_state.cfs_df

    st.markdown("### Column and Row Operations")

    row_col1, row_col2 = st.columns([1, 1])

    with row_col1:
        if 'selected_index' not in st.session_state:
            st.session_state.selected_index = len(cfs_df)

        selected_index = st.text_input("Index to add row:", value=str(st.session_state.selected_index))
        # if selected_index.isdigit():
        if isinstance(selected_index, int):
            st.session_state.selected_index = int(selected_index)

        if st.button("Add Row"):
            empty_row = {col: '' for col in cfs_df.columns}
            new_row_df = pd.DataFrame([empty_row])
            top_part = cfs_df.iloc[:st.session_state.selected_index]
            bottom_part = cfs_df.iloc[st.session_state.selected_index:]
            edited_df = pd.concat([top_part, new_row_df, bottom_part], ignore_index=True)

            st.session_state.cfs_df = edited_df
            st.session_state.cfs = edited_df.to_dict(orient='list')
            st.success(f"Empty row added at index {st.session_state.selected_index}!")

    with row_col2:
        column_name_input = st.text_input("Enter new column name:", "New Column")
        if st.button("Add Column"):
            new_column_name = column_name_input.strip() or f"New Column {len(cfs_df.columns) + 1}"
            cfs_df[new_column_name] = ''
            st.session_state.cfs_df = cfs_df
            st.session_state.cfs = cfs_df.to_dict(orient='list')
            st.success(f"New column '{new_column_name}' added!")

    col_rename, col_delete = st.columns(2)

    with col_rename:
        st.markdown("#### Rename a Column")
        col_to_rename = st.selectbox("Select a column to rename:", cfs_df.columns, key="rename_selector")
        new_col_name = st.text_input("Enter new column name:", key="rename_input")
        if st.button("Rename Column"):
            if new_col_name.strip():
                cfs_df.rename(columns={col_to_rename: new_col_name.strip()}, inplace=True)
                st.session_state.cfs_df = cfs_df
                st.session_state.cfs = cfs_df.to_dict(orient='list')
                st.success(f"Column '{col_to_rename}' renamed to '{new_col_name.strip()}'!")
            else:
                st.warning("Please enter a valid new column name.")

    with col_delete:
        column_to_delete = st.selectbox("Select a column to delete:", cfs_df.columns)
        if st.button("Delete Column"):
            if column_to_delete:
                cfs_df.drop(columns=[column_to_delete], inplace=True)
                st.session_state.cfs_df = cfs_df
                st.session_state.cfs = cfs_df.to_dict(orient='list')
                st.success(f"Column '{column_to_delete}' deleted!")



# Display image and DataFrame
col1, col2 = st.columns(2)

with col1:
    st.write("### Cashflow Sheet")
    image = files[2]
    st.image(image, caption="Cashflow Sheet", use_container_width=True)

# with col2:
    
#         st.write("### Edit Financial Data")
#         cfs_df = st.session_state.cfs_df

#         # Reset index for display in the table
#         edited_df_with_index = cfs_df.reset_index(drop=False)  # Reset index and include it as a column

#         # Display editable DataFrame with index shown in the UI
#         edited_df = st.data_editor(
#             edited_df_with_index,
#             use_container_width=True,
#             height=800,
#             num_rows="dynamic",
#             column_config={
#                 "index": st.column_config.NumberColumn(
#                     "Index",  # Display the index as a column
#                     help="Row index",
#                     width="small",
#                 )
#             }
#         )

with col2:
    st.write("### Edit Financial Data")
    cfs_df = st.session_state.cfs_df
    edited_df_with_index = cfs_df.reset_index(drop=False)
    
    on = st.toggle("Edit Table")
    
    if on:
        # Edit mode - use data editor
        edited_df = st.data_editor(
            edited_df_with_index,
            use_container_width=True,
            height=800,
            num_rows="dynamic",
            column_config={
                "index": st.column_config.NumberColumn(
                    "Index",
                    help="Row index",
                    width="small",
                )
            }
        )
    else:
        edited_df = edited_df_with_index
        def format_bold_html(val):
            if isinstance(val, str) and val.startswith('**') and val.endswith('**'):
                return f'<strong style="font-weight:900">{val.strip("*")}</strong>'
            return str(val)

        # Convert to HTML
        html = cfs_df.applymap(format_bold_html).to_html(escape=False, index=False)
        
        # Display in scrollable container
        st.markdown(f"""
        <div style="height: 800px; overflow-y: auto; margin: 1rem 0;">
            {html}
        </div>
        """, unsafe_allow_html=True)


        # Save changes
        if st.button("Next"):
            # Drop the index column before saving
            edited_df_no_index = edited_df.drop(columns=["index"])

            # Convert to JSON without the index
            edited_json = edited_df_no_index.to_dict(orient='list')
            md = json_to_markdown_table(edited_json)

            input_data['cfs']['raw_response']['natural_text'] = md
            st.session_state.cfs_df = edited_df_no_index
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

            if 'bs' in st.session_state:
                bs = st.session_state.bs
            else:
                st.error("bs not found")

            if 'pls' in st.session_state:
                pls = st.session_state.pls
            else:
                st.error("pls not found")

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
            st.session_state.intermediate = intermediate_values
            
            st.switch_page("pages/formula.py")