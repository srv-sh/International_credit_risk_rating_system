
# def app():
# Standard Library Imports
import base64
import io
import math
import pickle
from io import BytesIO

# Third-Party Library Imports
import numpy as np
import pandas as pd
import requests
import json
import streamlit as st
from source import api_client
from PIL import Image, ImageDraw, UnidentifiedImageError
from streamlit_drawable_canvas import st_canvas


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

class InputData:
    def __init__(self):
        if 'input' not in st.session_state:
            st.error("Input data not found")
            st.stop()
        
        self.input_data = st.session_state.input
        self.processed_data = self.input_data['bs']['processed_response']
        self.texts = self.input_data['bs']['paddleOCR']['text']
        self.bounding_boxes = self.input_data['bs']['paddleOCR']['bbox']
        self.img_base64 = self.input_data['bs']['image_base64']
        self.raw_response = self.input_data['bs']['raw_response']


class DataFormationandStorage:
    def __init__(self, input_data: InputData):
        """Initialize with an InputData instance."""
        self.input = input_data

    def display_editable_dataframe(self) -> pd.DataFrame | None:
        """Returns an editable DataFrame with 'Particulars' as the first column."""
        # if not hasattr(self.input, 'processed_data'):
        #     return None
        
        processed_data = self.input.processed_data
        if not processed_data:
            return None

        df = pd.DataFrame(processed_data)
        
        # Ensure "Particulars" is the first column if it exists
        if "Particulars" in df.columns:
            cols = ["Particulars"] + [c for c in df.columns if c != "Particulars"]
            df = df[cols]
        
        return df

    def json_to_markdown_table(self, json_data):
        columns = list(json_data.keys())
        rows = zip(*[json_data[col] for col in columns])
        markdown = "| " + " | ".join(columns) + " |\n"
        markdown += "| " + " | ".join(["---"] * len(columns)) + " |\n"
        for row in rows:
            row_values = [str(cell) if cell != '' else ' ' for cell in row]
            markdown += "| " + " | ".join(row_values) + " |\n"
        return markdown
    

    def json2im(self, data) -> np.ndarray:
        """Convert a dict (or JSON string) back to a Numpy array"""
        # if isinstance(data, str):
        #     data = json.loads(data)  # convert JSON string to dict
        imdata = base64.b64decode(data)
        im = pickle.loads(imdata)
        return im
    
    def transform_and_send(self, data: dict, database_url: str):
            transformed_data = {
                "sheet": "bs",
                "image_base64": self.input.img_base64,
                "raw_response": self.input.raw_response,
                "page_number": 1,
                # "response": json.dumps(data['bs']['raw_response'])  # <-- double check server expects a string
                'response': md
            }

            # Debugging print
            print("📤 Sending this to the DB:")
            print(json.dumps(transformed_data, indent=2))

            return api_client.store(database_url, transformed_data)
            
    @staticmethod
    def update_json_file(key, value, filepath='json/variables.json'):
        with open(filepath, 'r') as file:
            data = json.load(file)
        data[key] = value
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)
    


class FrontEndHelper:
    def get_bbox_center(self, bbox):
        points = list(zip(bbox[::2], bbox[1::2]))
        x_coords = [pt[0] for pt in points]
        y_coords = [pt[1] for pt in points]
        return (sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords))
    
    def format_bold_html(self, val):
            if isinstance(val, str) and val.startswith('**') and val.endswith('**'):
                return f'<strong style="font-weight:900">{val.strip("*")}</strong>'
            return str(val)
    


input_obj = InputData()
data_formation = DataFormationandStorage(input_obj)
frontend_helper = FrontEndHelper()

st.title("Financial Data Table")

# Load and store dataframe in session state
bs_df = data_formation.display_editable_dataframe()

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



# Two-column layout
col1, col2 = st.columns(2)

with col1:
    st.write("### Balance Sheet")

    img = data_formation.json2im(input_obj.img_base64)

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

            for i, bbox in enumerate(input_obj.bounding_boxes):
                cx, cy = frontend_helper.get_bbox_center(bbox)
                dist = math.hypot(cx - x_click, cy - y_click)
                if dist < min_dist:
                    min_dist = dist
                    closest_index = i

            if closest_index != -1:
                st.session_state.clicked_text = input_obj.texts[closest_index]
                matched_bbox = input_obj.bounding_boxes[closest_index]

                # Show index, text, bbox, and click coordinates
                st.success(f"Closest text: {st.session_state.clicked_text}")
                st.write(f"Matched BBox Index: {closest_index}")
                st.write(f"Matched BBox: {matched_bbox}")
                st.write(f"Clicked at: ({round(x_click)}, {round(y_click)})")



with col2:
    st.write("### Edit Financial Data")
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
        

        html = edited_df_with_index.applymap(frontend_helper.format_bold_html).to_html(escape=False, index=False)
        st.markdown(f"""
        <div style="height: 800px; overflow-y: auto; margin: 1rem 0;">
            {html}
        </div>
        """, unsafe_allow_html=True)


    if st.button("Next"):
        if "index" in edited_df.columns:
            edited_df_no_index = edited_df.drop(columns=["index"])
        else:
            edited_df_no_index = edited_df.copy()

        # edited_df_no_index = edited_df.drop(columns=["index"])
        edited_json = edited_df_no_index.to_dict(orient='list')
        md = data_formation.json_to_markdown_table(edited_json)

        # input_data['bs']['raw_response']['natural_text'] = md
        st.session_state.bs_df = edited_df_no_index
        st.session_state.bs = edited_json
        st.success("Changes saved successfully as JSON!")


        url = "store_ocr_data"
        storedb = data_formation.transform_and_send(input_obj.input_data, url)
        print(f"📥 THE DATABASE RESPONSE IS: {storedb}")

        if storedb['status'] == 'success' and 'response' in storedb:
            balance_id = storedb['response']['id']
            data_formation.update_json_file('balance_id', balance_id)
            st.success("Changes saved and data stored successfully!")
            st.switch_page("pages/is.py")

        else:
            st.error(f"Database error: {storedb['error']}")

    

    if st.button("Skip"):
        st.success("Changes saved successfully as JSON!")
        st.switch_page("pages/is.py")

# if __name__ == "__main__":
# #     app()
#     if st.button("Load Page"):
#         pages()
#         st.success("Page loaded successfully!")
#         st.balloons()


