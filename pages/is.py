import streamlit as st
import pandas as pd
import json
import requests

st.set_page_config(layout="wide")
st.title("Financial Data Table")


# ----------------------------- #
# Utility Functions
# ----------------------------- #
def display_editable_dataframe(data):
    if data and 'is' in data and 'processed_response' in data['is']:
        df = pd.DataFrame(data['is']['processed_response'])
        if "Particulars" in df.columns:
            cols = df.columns.tolist()
            cols.remove("Particulars")
            df = df[["Particulars"] + sorted(cols)]
        return df
    return None

def json_to_markdown_table(json_data):
    columns = list(json_data.keys())
    rows = zip(*[json_data[col] for col in columns])
    md = "| " + " | ".join(columns) + " |\n"
    md += "| " + " | ".join(["---"] * len(columns)) + " |\n"
    for row in rows:
        row_values = [str(cell) if cell != '' else ' ' for cell in row]
        md += "| " + " | ".join(row_values) + " |\n"
    return md

def transform_and_send(data: dict, database_url: str):
    transformed_data = {
        "url": data['is']['pdf_url'],
        "prompt": data['is']['prompt'],
        "page_number": 1,
        "response": json.dumps(data['is']['raw_response'])
    }
    try:
        response = requests.post(database_url, json=transformed_data)
        response.raise_for_status()
        return {'status': 'success', 'response': response.json()}
    except requests.exceptions.RequestException as e:
        return {'status': 'error', 'error': str(e)}

def update_json_file(key, value, filepath='json/variables.json'):
    with open(filepath, 'r') as file:
        data = json.load(file)
    data[key] = value
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

# ----------------------------- #
# Load session data
# ----------------------------- #
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
is_df = display_editable_dataframe(input_data)
if is_df is not None:
    if 'is_df' not in st.session_state:
        st.session_state.is_df = is_df
    else:
        is_df = st.session_state.is_df

    st.markdown("### Column and Row Operations")

    row_col1, row_col2 = st.columns([1, 1])

    with row_col1:
        if 'selected_index' not in st.session_state:
            st.session_state.selected_index = len(is_df)

        selected_index = st.text_input("Index to add row:", value=str(st.session_state.selected_index))
        if selected_index.isdigit():
            st.session_state.selected_index = int(selected_index)

        if st.button("Add Row"):
            empty_row = {col: '' for col in is_df.columns}
            new_row_df = pd.DataFrame([empty_row])
            top_part = is_df.iloc[:st.session_state.selected_index]
            bottom_part = is_df.iloc[st.session_state.selected_index:]
            edited_df = pd.concat([top_part, new_row_df, bottom_part], ignore_index=True)

            st.session_state.is_df = edited_df
            st.session_state.pls = edited_df.to_dict(orient='list')
            st.success(f"Empty row added at index {st.session_state.selected_index}!")

    with row_col2:
        column_name_input = st.text_input("Enter new column name:", "New Column")
        if st.button("Add Column"):
            new_column_name = column_name_input.strip() or f"New Column {len(is_df.columns) + 1}"
            is_df[new_column_name] = ''
            st.session_state.is_df = is_df
            st.session_state.pls = is_df.to_dict(orient='list')
            st.success(f"New column '{new_column_name}' added!")

    col_rename, col_delete = st.columns(2)

    with col_rename:
        st.markdown("#### Rename a Column")
        col_to_rename = st.selectbox("Select a column to rename:", is_df.columns, key="rename_selector")
        new_col_name = st.text_input("Enter new column name:", key="rename_input")
        if st.button("Rename Column"):
            if new_col_name.strip():
                is_df.rename(columns={col_to_rename: new_col_name.strip()}, inplace=True)
                st.session_state.is_df = is_df
                st.session_state.pls = is_df.to_dict(orient='list')
                st.success(f"Column '{col_to_rename}' renamed to '{new_col_name.strip()}'!")
            else:
                st.warning("Please enter a valid new column name.")

    with col_delete:
        column_to_delete = st.selectbox("Select a column to delete:", is_df.columns)
        if st.button("Delete Column"):
            if column_to_delete:
                is_df.drop(columns=[column_to_delete], inplace=True)
                st.session_state.is_df = is_df
                st.session_state.pls = is_df.to_dict(orient='list')
                st.success(f"Column '{column_to_delete}' deleted!")






# ----------------------------- #
# UI Layout
# ----------------------------- #
col1, col2 = st.columns(2)

with col1:
    st.write("### Income Sheet")
    st.image(files[1], caption="Income Sheet", use_container_width=True)

with col2:
    st.write("### Edit Financial Data")
    is_df = st.session_state.is_df

    edited_df_with_index = is_df.reset_index(drop=False)
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

    # ----------------------------- #
    # Final Save & Database Push
    # ----------------------------- #
    if st.button("Next"):
        final_df = edited_df.drop(columns=["index"])
        final_json = final_df.to_dict(orient='list')
        markdown = json_to_markdown_table(final_json)

        input_data['is']['raw_response']['natural_text'] = markdown
        st.session_state.is_df = final_df
        st.session_state.pls = final_json

        db_response = transform_and_send(input_data, "http://192.168.10.50:8000/store_ocr_data")
        if db_response['status'] == 'success':
            income_id = db_response['response']['id']
            update_json_file('income_id', income_id)
            st.success("Changes saved and data stored successfully!")
            st.switch_page("pages/cfs.py")
        else:
            st.error(f"Database error: {db_response['error']}")
