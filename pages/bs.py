import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(layout="wide")

def display_editable_dataframe(data):
    if data and 'bs' in data and 'processed_response' in data['bs']:
        processed_data = data['bs']['processed_response']
        bs_df = pd.DataFrame(processed_data)

        columns = bs_df.columns.tolist()
        if "Particulars" in columns:
            columns.remove("Particulars")
            bs_df = bs_df[["Particulars"] + sorted(columns)]

        return bs_df
    else:
        return None


def json_to_markdown_table(json_data):
    columns = list(json_data.keys())
    rows = zip(*[json_data[col] for col in columns])
    markdown = "| " + " | ".join(columns) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(columns)) + " |\n"
    for row in rows:
        row_values = [str(cell) if cell != '' else ' ' for cell in row]
        markdown += "| " + " | ".join(row_values) + " |\n"
    return markdown


st.title("Financial Data Table")

# Load session state data
if 'input' not in st.session_state:
    st.error("Input data not found")
    st.stop()
else:
    input_data = st.session_state.input

if 'files' not in st.session_state:
    st.error("Files not found")
    st.stop()
else:
    files = st.session_state.files

# Load and store dataframe in session state
bs_df = display_editable_dataframe(input_data)
if bs_df is not None:
    if 'bs_df' not in st.session_state:
        st.session_state.bs_df = bs_df
    else:
        bs_df = st.session_state.bs_df

    st.markdown("### Column and Row Operations")

    # row_col1, row_col2 = st.columns([1, 1])

    row_col1, row_col2 = st.columns([1, 1])

    with row_col1:
        # Set default selected_index to the number of rows in bs_df if not provided
        selected_index = len(bs_df)

        # Text input for the user to specify the index
        selected_index_input = st.text_input("Index to add row:", value=str(selected_index), max_chars=5, key="selected_index", label_visibility="collapsed")

        # Validate that the entered index is a valid integer
        if selected_index_input.isdigit():
            selected_index = int(selected_index_input)
        else:
            selected_index = len(bs_df)  # Revert to default if input is invalid

        # Validate the index is within bounds
        if selected_index < 0 or selected_index > len(bs_df):
            st.error(f"Index {selected_index} is out of bounds. Please enter a valid index.")
        else:
            if st.button("Add Row", key="add_row_button"):
                empty_row = {col: '' for col in bs_df.columns}
                new_row_df = pd.DataFrame([empty_row])
                top_part = bs_df.iloc[:selected_index]
                bottom_part = bs_df.iloc[selected_index:]
                edited_df = pd.concat([top_part, new_row_df, bottom_part], ignore_index=True)
                # Update the DataFrame in session state
                st.session_state.bs_df = edited_df
                st.session_state.bs = edited_df.to_dict(orient='list')
                st.success(f"Empty row added at index {selected_index}!")

    with row_col2:
        column_name_input = st.text_input("Enter new column name:", "New Column", max_chars=15, key="new_column_name", label_visibility="collapsed")
        if st.button("Add Column", key="add_column_button"):
            new_column_name = column_name_input.strip() or f"New Column {len(bs_df.columns) + 1}"
            bs_df[new_column_name] = ''
            st.session_state.bs_df = bs_df
            st.session_state.bs = bs_df.to_dict(orient='list')
            st.success(f"New column '{new_column_name}' added!")

    # Columns for renaming and deleting columns
    col_rename, col_delete = st.columns([1, 1])

    with col_rename:
        st.markdown("#### Rename a Column", help="Select a column to rename.")
        col_to_rename = st.selectbox("Select a column to rename:", bs_df.columns, key="rename_selector", label_visibility="collapsed")
        new_col_name = st.text_input("New name:", key="rename_input", max_chars=15, label_visibility="collapsed")
        if st.button("Rename Column", key="rename_column_button"):
            if new_col_name.strip():
                bs_df.rename(columns={col_to_rename: new_col_name.strip()}, inplace=True)
                st.session_state.bs_df = bs_df
                st.session_state.bs = bs_df.to_dict(orient='list')
                st.success(f"Column '{col_to_rename}' renamed to '{new_col_name.strip()}'!")
            else:
                st.warning("Please enter a valid new column name.")

    with col_delete:
        column_to_delete = st.selectbox("Select a column to delete:", bs_df.columns, key="delete_selector", label_visibility="collapsed")
        if st.button("Delete Column", key="delete_column_button"):
            if column_to_delete:
                bs_df.drop(columns=[column_to_delete], inplace=True)
                st.session_state.bs_df = bs_df
                st.session_state.bs = bs_df.to_dict(orient='list')
                st.success(f"Column '{column_to_delete}' deleted!")




# Two-column layout
col1, col2 = st.columns(2)

with col1:
    st.write("### Balance Sheet")
    image = files[0]
    st.image(image, caption="Balance Sheet", use_container_width=True)

with col2:
    st.write("### Edit Financial Data")
    bs_df = st.session_state.bs_df
    edited_df_with_index = bs_df.reset_index(drop=False)

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

    if st.button("Next"):
        edited_df_no_index = edited_df.drop(columns=["index"])
        edited_json = edited_df_no_index.to_dict(orient='list')
        md = json_to_markdown_table(edited_json)

        input_data['bs']['raw_response']['natural_text'] = md
        st.session_state.bs_df = edited_df_no_index
        st.session_state.bs = edited_json
        st.success("Changes saved successfully as JSON!")

        def transform_and_send(data: dict, database_url: str):
            transformed_data = {
                "url": data['bs']['pdf_url'],
                "prompt": data['bs']['prompt'],
                "page_number": 1,
                "response": json.dumps(data['bs']['raw_response'])  # <-- double check server expects a string
            }

            # Debugging print
            print("📤 Sending this to the DB:")
            print(json.dumps(transformed_data, indent=2))

            try:
                response = requests.post(database_url, json=transformed_data)
                response.raise_for_status()
                return {'status': 'success', 'response': response.json()}
            except requests.exceptions.RequestException as e:
                print("❌ Request failed:", str(e))
                return {'status': 'error', 'error': str(e)}

        url = "http://192.168.10.50:8000/store_ocr_data"
        storedb = transform_and_send(input_data, url)
        print(f"📥 THE DATABASE RESPONSE IS: {storedb}")

        if storedb['status'] == 'success' and 'response' in storedb:
            try:
                with open('json/variables.json', 'r') as file:
                    data = json.load(file)

                data['balance_id'] = storedb['response']['id']

                with open('json/variables.json', 'w') as file:
                    json.dump(data, file, indent=4)

                print("✅ Key value updated successfully!")
                st.switch_page("pages/is.py")

            except Exception as e:
                st.error("⚠️ Failed to update local variables file.")
                st.error(str(e))

        else:
            st.error("🚨 Failed to store data in the database.")
            st.error(storedb['error'])

