    
# def app():
import streamlit as st
import json
import pandas as pd
import numpy as np
import pickle
from tabulate import tabulate  # Ensure tabulate is installed: pip install tabulate
from io import StringIO
from collections import defaultdict
from source.main_function import Main
import json
import requests
import importlib

from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import math
from io import BytesIO
import base64
import streamlit as st
from io import BytesIO
from PIL import Image, UnidentifiedImageError

# st.set_page_config(layout="wide")  # Ensures the app uses the full width of the page

st.markdown("""
    <style>
        /* Container class to wrap inputs in smaller width */
        .css-1cpxqw2, .css-1kyxreq {
            max-width: 300px;  /* max width for individual widgets */
            width: 100% !important;
        }

        /* Text input */
        .stTextInput input {
            font-size: 13px;
            padding: 6px;
            height: 32px;
            width: 100% !important;
        }

        /* Number input */
        .stNumberInput input {
            font-size: 13px;
            padding: 6px;
            height: 32px;
            width: 100% !important;
        }

        /* Selectbox */
        .stSelectbox div[data-baseweb="select"] {
            font-size: 13px;
            padding: 4px;
            width: 100% !important;
        }

        /* Buttons */
        .stButton > button {
            font-size: 13px !important;
            padding: 6px 12px !important;
            border-radius: 6px !important;
            width: 100% !important;
        }

        label {
            font-size: 13px;
            margin-bottom: 2px;
        }
    </style>
""", unsafe_allow_html=True)



def display_editable_dataframe(data):
    if data and 'cfs' in data and 'processed_response' in data['cfs']:
        processed_data = data['cfs']['processed_response']

        # Convert list of dicts into DataFrame
        cfs_df = pd.DataFrame(processed_data)

        # Optional: Reorder columns to show "Particulars" first if it exists
        columns = cfs_df.columns.tolist()
        if "Particulars" in columns:
            columns.remove("Particulars")
            cfs_df = cfs_df[["Particulars"] + columns]

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



texts = input_data["cfs"]["paddleOCR"]["text"]
bounding_boxes = input_data["cfs"]["paddleOCR"]["bbox"] 



# Load and store dataframe in session state
cfs_df = display_editable_dataframe(input_data)
if cfs_df is not None:
    if 'cfs_df' not in st.session_state:
        st.session_state.cfs_df = cfs_df
    else:
        cfs_df = st.session_state.cfs_df

    st.markdown("### Column and Row Operations")

    row_col1, row_col2, row_col3 = st.columns([1, 1, 1])

    with row_col1:
        st.markdown('<div class="three-col-section">', unsafe_allow_html=True)
        st.subheader("🧩 Add Row / Rename Column")

        if 'selected_index' not in st.session_state:
            st.session_state.selected_index = len(cfs_df)

        selected_index_input = st.text_input("Index to add row:", value=str(st.session_state.selected_index))

        if selected_index_input.isdigit():
            selected_index = int(selected_index_input)
            st.session_state.selected_index = selected_index
        else:
            selected_index = len(cfs_df)
            st.warning("Please enter a valid integer index. Using end of dataframe as default.")

        if selected_index < 0 or selected_index > len(cfs_df):
            st.error(f"Index {selected_index} is out of bounds. Using end of dataframe instead.")
            selected_index = len(cfs_df)
            st.session_state.selected_index = selected_index

        if st.button("➕ Add Row", key="add_row_button"):
            empty_row = {col: '' for col in cfs_df.columns}
            new_row_df = pd.DataFrame([empty_row])
            top_part = cfs_df.iloc[:selected_index]
            bottom_part = cfs_df.iloc[selected_index:]
            edited_df = pd.concat([top_part, new_row_df, bottom_part], ignore_index=True)
            st.session_state.cfs_df = edited_df
            st.session_state.cfs = edited_df.to_dict(orient='list')
            st.success(f"Empty row added at index {selected_index}!")

        col_to_rename = st.selectbox("Select column to rename", cfs_df.columns, key="rename_selector")
        new_col_name = st.text_input("New column name", key="rename_input", max_chars=15)
        if st.button("✏️ Rename Column", key="rename_column_button"):
            if new_col_name.strip():
                cfs_df.rename(columns={col_to_rename: new_col_name.strip()}, inplace=True)
                st.session_state.cfs_df = cfs_df
                st.session_state.cfs = cfs_df.to_dict(orient='list')
                st.success(f"Renamed '{col_to_rename}' to '{new_col_name.strip()}'")
            else:
                st.warning("Please enter a valid new column name.")

        st.markdown('</div>', unsafe_allow_html=True)

    with row_col2:
        st.markdown('<div class="three-col-section">', unsafe_allow_html=True)
        st.subheader("📐 Add / Delete Column")

        column_name_input = st.text_input("New column name", "New Column", max_chars=15, key="new_column_name")
        if st.button("➕ Add Column", key="add_column_button"):
            new_column_name = column_name_input.strip() or f"New Column {len(cfs_df.columns) + 1}"
            cfs_df[new_column_name] = ''
            st.session_state.cfs_df = cfs_df
            st.session_state.cfs = cfs_df.to_dict(orient='list')
            st.success(f"New column '{new_column_name}' added!")

        column_to_delete = st.selectbox("Select column to delete", cfs_df.columns, key="delete_selector")
        if st.button("❌ Delete Column", key="delete_column_button"):
            if column_to_delete:
                cfs_df.drop(columns=[column_to_delete], inplace=True)
                st.session_state.cfs_df = cfs_df
                st.session_state.cfs = cfs_df.to_dict(orient='list')
                st.success(f"Deleted column '{column_to_delete}'")

        st.markdown('</div>', unsafe_allow_html=True)

    with row_col3:
        st.markdown('<div class="three-col-section">', unsafe_allow_html=True)
        st.subheader("🖊️ Edit Cell")

        cfs_df = st.session_state.cfs_df
        edited_df_with_index = cfs_df.reset_index(drop='level_0' in cfs_df.columns)

        # Initialize clicked text in session state
        if "clicked_text" not in st.session_state:
            st.session_state.clicked_text = ""

        selected_row = st.number_input("Row", min_value=0, max_value=len(edited_df_with_index)-1, step=1)
        selected_column = st.selectbox("Column", edited_df_with_index.columns)

        st.info(f"Inserting {st.session_state.clicked_text} in Row {selected_row}, Column '{selected_column}'")

        if st.button("📥 Insert Text"):
            if selected_column in edited_df_with_index.columns:
                edited_df_with_index.at[selected_row, selected_column] = st.session_state.clicked_text
                st.success(f"Inserted '{st.session_state.clicked_text}' into row {selected_row}, column '{selected_column}'")

        st.markdown('</div>', unsafe_allow_html=True)



# Two-column layout
col1, col2 = st.columns(2)

with col1:
    st.write("### Cashflow Sheet")

    def json2im(data) -> np.ndarray:
        """Convert a dict (or JSON string) back to a Numpy array"""
        # if isinstance(data, str):
        #     data = json.loads(data)  # convert JSON string to dict
        imdata = base64.b64decode(data)
        im = pickle.loads(imdata)
        return im

    img = json2im(input_data["cfs"]["image_base64"])

    # type(img)  # Should be <class 'numpy.ndarray'>

    # Display the image using PIL
    bg_image = Image.fromarray(img)

    if bg_image:
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            background_image=bg_image,
            height=bg_image.height,
            width=bg_image.width,
            drawing_mode="rect",
            key="canvas_cashflow",
        )

        def get_bbox_center(bbox):
            points = list(zip(bbox[::2], bbox[1::2]))
            x_coords = [pt[0] for pt in points]
            y_coords = [pt[1] for pt in points]
            return (sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords))

        # Initialize clicked text in session state
        if "clicked_text" not in st.session_state:
            st.session_state.clicked_text = ""

        if canvas_result.json_data is not None:
            objects = canvas_result.json_data.get("objects", [])
            if objects:
                x_click = objects[-1]["left"]
                y_click = objects[-1]["top"]

                min_dist = float("inf")
                closest_index = -1

                for i, bbox in enumerate(bounding_boxes):
                    cx, cy = get_bbox_center(bbox)
                    dist = math.hypot(cx - x_click, cy - y_click)
                    if dist < min_dist:
                        min_dist = dist
                        closest_index = i

                if closest_index != -1:
                    st.session_state.clicked_text = texts[closest_index]
                    st.success(f"Closest text: {st.session_state.clicked_text}")
                    st.write(f"Clicked at: ({round(x_click)}, {round(y_click)})")
    else:
        st.warning("Canvas not displayed due to image loading failure.")


with col2:
    st.write("### Edit Financial Data")

    # cfs_df = st.session_state.cfs_df
    # edited_df_with_index = cfs_df.reset_index(drop='level_0' in cfs_df.columns)

    # # Row and column selectors
    # selected_row = st.number_input("Select Row to Edit", min_value=0, max_value=len(edited_df_with_index)-1, step=1)
    # selected_column = st.selectbox("Select Column", edited_df_with_index.columns)

    # st.info(f"Inserting {st.session_state.clicked_text} in the Row: '{selected_row}', Column: '{selected_column}'...")

    # # Button to apply clicked text to table
    # if st.button("Insert Clicked Text into Table"):
    #     if selected_column in edited_df_with_index.columns:
    #         edited_df_with_index.at[selected_row, selected_column] = st.session_state.clicked_text
    #         st.success(f"Inserted '{st.session_state.clicked_text}' into row {selected_row}, column '{selected_column}'")

    # Toggle editor
    on = st.toggle("Edit Table")

    if on:
        edited_df = st.data_editor(
            edited_df_with_index,
            use_container_width=True,
            height=800,
            num_rows="dynamic"
        )
        st.session_state.cfs_df = edited_df
    else:
        edited_df = st.session_state.cfs_df
        def format_bold_html(val):
            if isinstance(val, str) and val.startswith('**') and val.endswith('**'):
                return f'<strong style="font-weight:900">{val.strip("*")}</strong>'
            return str(val)

        html = edited_df_with_index.applymap(format_bold_html).to_html(escape=False, index=False)
        st.markdown(f"""
        <div style="height: 800px; overflow-y: auto; margin: 1rem 0;">
            {html}
        </div>
        """, unsafe_allow_html=True)



    # # Now, use the styled dataframe in st.data_editor:
    # edited_df = st.data_editor(
    #     edited_df_with_index,
    #     use_container_width=True,
    #     height=800,
    #     num_rows="dynamic",
    #     column_config={
    #         "index": st.column_config.NumberColumn(
    #             "Index",
    #             help="Row index",
    #             width="small",
    #         )
    #     }
    # )


        # Save changes
        if st.button("Next"):
            # Drop the index column before saving

            if "index" in edited_df.columns:
                edited_df_no_index = edited_df.drop(columns=["index"])
            else:
                edited_df_no_index = edited_df.copy()

            # edited_df_no_index = edited_df.drop(columns=["index"])

            # Convert to JSON without the index
            edited_json = edited_df_no_index.to_dict(orient='list')
            md = json_to_markdown_table(edited_json)
            st.session_state.cfs_df = edited_df_no_index
            st.session_state.cfs = edited_json
            st.success("Changes saved successfully as JSON!")

            def transform_and_send(data: dict, database_url: str):
                # Transforming data
                transformed_data = {
                    "image_base64": data['cfs']['image_base64'],  # Base64 encoded image  
                    "raw_response": data['cfs']['raw_response'],  # Raw OCR response
                    "page_number": 1,                   
                    "response": md  # Serialize the raw response as a JSON string
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

        if st.button("Skip"):
            st.switch_page("pages/formula.py")