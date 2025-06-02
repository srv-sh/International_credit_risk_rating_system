
# def app():
import streamlit as st
import pandas as pd
import requests
import json
import io
import pickle
import numpy as np
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import math
from io import BytesIO
import base64
import streamlit as st
from io import BytesIO
from PIL import Image, UnidentifiedImageError

# st.set_page_config(layout="wide")
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


texts = input_data["bs"]["paddleOCR"]["text"]
bounding_boxes = input_data["bs"]["paddleOCR"]["bbox"] 


# Load and store dataframe in session state
bs_df = display_editable_dataframe(input_data)

if bs_df is not None:
    if 'bs_df' not in st.session_state:
        st.session_state.bs_df = bs_df
    else:
        bs_df = st.session_state.bs_df

    st.markdown("### Column and Row Operations")

    # row_col1, row_col2 = st.columns([1, 1])

    row_col1, row_col2, row_col3 = st.columns([1, 1, 1])

    with row_col1:
        st.markdown('<div class="three-col-section">', unsafe_allow_html=True)
        st.subheader("🧩 Add Row / Rename Column")

        if 'selected_index' not in st.session_state:
            st.session_state.selected_index = len(bs_df)

        selected_index_input = st.text_input("Index to add row:", value=str(st.session_state.selected_index))

        if selected_index_input.isdigit():
            selected_index = int(selected_index_input)
            st.session_state.selected_index = selected_index
        else:
            selected_index = len(bs_df)
            st.warning("Please enter a valid integer index. Using end of dataframe as default.")

        if selected_index < 0 or selected_index > len(bs_df):
            st.error(f"Index {selected_index} is out of bounds. Using end of dataframe instead.")
            selected_index = len(bs_df)
            st.session_state.selected_index = selected_index

        if st.button("➕ Add Row", key="add_row_button"):
            empty_row = {col: '' for col in bs_df.columns}
            new_row_df = pd.DataFrame([empty_row])
            top_part = bs_df.iloc[:selected_index]
            bottom_part = bs_df.iloc[selected_index:]
            edited_df = pd.concat([top_part, new_row_df, bottom_part], ignore_index=True)
            st.session_state.bs_df = edited_df
            st.session_state.bs = edited_df.to_dict(orient='list')
            st.success(f"Empty row added at index {selected_index}!")

        col_to_rename = st.selectbox("Select column to rename", bs_df.columns, key="rename_selector")
        new_col_name = st.text_input("New column name", key="rename_input", max_chars=15)
        if st.button("✏️ Rename Column", key="rename_column_button"):
            if new_col_name.strip():
                bs_df.rename(columns={col_to_rename: new_col_name.strip()}, inplace=True)
                st.session_state.bs_df = bs_df
                st.session_state.bs = bs_df.to_dict(orient='list')
                st.success(f"Renamed '{col_to_rename}' to '{new_col_name.strip()}'")
            else:
                st.warning("Please enter a valid new column name.")

        st.markdown('</div>', unsafe_allow_html=True)

    with row_col2:
        st.markdown('<div class="three-col-section">', unsafe_allow_html=True)
        st.subheader("📐 Add / Delete Column")

        column_name_input = st.text_input("New column name", "New Column", max_chars=15, key="new_column_name")
        if st.button("➕ Add Column", key="add_column_button"):
            new_column_name = column_name_input.strip() or f"New Column {len(bs_df.columns) + 1}"
            bs_df[new_column_name] = ''
            st.session_state.bs_df = bs_df
            st.session_state.bs = bs_df.to_dict(orient='list')
            st.success(f"New column '{new_column_name}' added!")

        column_to_delete = st.selectbox("Select column to delete", bs_df.columns, key="delete_selector")
        if st.button("❌ Delete Column", key="delete_column_button"):
            if column_to_delete:
                bs_df.drop(columns=[column_to_delete], inplace=True)
                st.session_state.bs_df = bs_df
                st.session_state.bs = bs_df.to_dict(orient='list')
                st.success(f"Deleted column '{column_to_delete}'")

        st.markdown('</div>', unsafe_allow_html=True)

    with row_col3:
        st.markdown('<div class="three-col-section">', unsafe_allow_html=True)
        st.subheader("🖊️ Edit Cell")

        bs_df = st.session_state.bs_df
        edited_df_with_index = bs_df.reset_index(drop='level_0' in bs_df.columns)

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

    # # Columns for renaming and deleting columns
    # col_rename, col_delete = st.columns([1, 1])

    # with col_rename:
    #     st.markdown("#### Rename a Column", help="Select a column to rename.")
    #     col_to_rename = st.selectbox("Select a column to rename:", bs_df.columns, key="rename_selector", label_visibility="collapsed")
    #     new_col_name = st.text_input("New name:", key="rename_input", max_chars=15, label_visibility="collapsed")
    #     if st.button("Rename Column", key="rename_column_button"):
    #         if new_col_name.strip():
    #             bs_df.rename(columns={col_to_rename: new_col_name.strip()}, inplace=True)
    #             st.session_state.bs_df = bs_df
    #             st.session_state.bs = bs_df.to_dict(orient='list')
    #             st.success(f"Column '{col_to_rename}' renamed to '{new_col_name.strip()}'!")
    #         else:
    #             st.warning("Please enter a valid new column name.")

    # with col_delete:
    #     column_to_delete = st.selectbox("Select a column to delete:", bs_df.columns, key="delete_selector", label_visibility="collapsed")
    #     if st.button("Delete Column", key="delete_column_button"):
    #         if column_to_delete:
    #             bs_df.drop(columns=[column_to_delete], inplace=True)
    #             st.session_state.bs_df = bs_df
    #             st.session_state.bs = bs_df.to_dict(orient='list')
    #             st.success(f"Column '{column_to_delete}' deleted!")




# Two-column layout
col1, col2 = st.columns(2)

with col1:
    st.write("### Balance Sheet")

    def json2im(data) -> np.ndarray:
        """Convert a dict (or JSON string) back to a Numpy array"""
        if isinstance(data, str):
            data = json.loads(data)  # convert JSON string to dict
        imdata = base64.b64decode(data['image'])
        im = pickle.loads(imdata)
        return im

    img = json2im(input_data["bs"]["image_base64"])

    # type(img)  # Should be <class 'numpy.ndarray'>

    # Display the image using PIL
    bg_image = Image.fromarray(img)

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=2,
        background_image=bg_image,
        height=bg_image.height,
        width=bg_image.width,
        drawing_mode="rect",
        key="canvas",
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
                matched_bbox = bounding_boxes[closest_index]

                # Show index, text, bbox, and click coordinates
                st.success(f"Closest text: {st.session_state.clicked_text}")
                st.write(f"Matched BBox Index: {closest_index}")
                st.write(f"Matched BBox: {matched_bbox}")
                st.write(f"Clicked at: ({round(x_click)}, {round(y_click)})")


with col2:
    st.write("### Edit Financial Data")

    # bs_df = st.session_state.bs_df
    # edited_df_with_index = bs_df.reset_index(drop='level_0' in bs_df.columns)

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
        st.session_state.bs_df = edited_df
    else:
        edited_df = st.session_state.bs_df
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


    if st.button("Next"):
        if "index" in edited_df.columns:
            edited_df_no_index = edited_df.drop(columns=["index"])
        else:
            edited_df_no_index = edited_df.copy()

        # edited_df_no_index = edited_df.drop(columns=["index"])
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
                # page = importlib.import_module("pages.is")
                # page.app()

            except Exception as e:
                st.error("⚠️ Failed to update local variables file.")
                st.error(str(e))

        else:
            st.error("🚨 Failed to store data in the database.")
            st.error(storedb['error'])

    

    if st.button("Skip"):
        # if "index" in edited_df.columns:
        #     edited_df_no_index = edited_df.drop(columns=["index"])
        # else:
        #     edited_df_no_index = edited_df.copy()

        # # edited_df_no_index = edited_df.drop(columns=["index"])
        # edited_json = edited_df_no_index.to_dict(orient='list')
        # md = json_to_markdown_table(edited_json)

        # input_data['bs']['raw_response']['natural_text'] = md
        # st.session_state.bs_df = edited_df_no_index
        # st.session_state.bs = edited_json
        st.success("Changes saved successfully as JSON!")
        st.switch_page("pages/is.py")


