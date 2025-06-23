
# def app():
# Standard Library Imports
import base64
import io
import os
import math
import time
import pickle
from io import BytesIO

# Third-Party Library Imports
import numpy as np
import pandas as pd
import requests
import json
import streamlit as st
import streamlit.components.v1 as components
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

def pages(sheet):
    class InputData:
        def __init__(self):
            # with open('response_1750229417480.json', 'r', encoding='utf-8') as file:
            #     self.input_data = json.load(file)

            if 'input' not in st.session_state:
                st.error("Input data not found")
                st.stop()
            
            self.input_data = st.session_state.input

            self.processed_data = self.input_data[sheet]['processed_response']
            self.texts = self.input_data[sheet]['paddleOCR']['text']
            self.bounding_boxes = self.input_data[sheet]['paddleOCR']['bbox']
            self.img_base64 = self.input_data[sheet]['image_base64']
            self.raw_response = self.input_data[sheet]['raw_response']
            

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
    frontend_helper = FrontEndHelper()

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
            
            # # Ensure "Particulars" is the first column if it exists
            # if "Particulars" in df.columns:
            #     cols = ["Particulars"] + [c for c in df.columns if c != "Particulars"]
            # df = df[cols]
            
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
            try:
                imdata = base64.b64decode(data)
                im = pickle.loads(imdata)
                return im
            except Exception as e:
                st.error(f"Image loading failed: {e}")
                return None
            
        def draw_canvas(self, bg_image, max_width=800):
            """Fixed canvas drawing function with proper session state management and image resizing"""
            
            # Resize image while maintaining aspect ratio
            if bg_image.width > max_width:
                aspect_ratio = bg_image.height / bg_image.width
                new_width = max_width
                new_height = int(new_width * aspect_ratio)
                try:
                    resample = Image.Resampling.LANCZOS
                except AttributeError:
                    resample = Image.LANCZOS  # fallback for older versions

                bg_image = bg_image.resize((new_width, new_height), resample)
            else:
                new_width = bg_image.width
                new_height = bg_image.height

            # Ensure unique canvas key with timestamp or counter
            canvas_key_state = f"canvas_key_{sheet}"
            if canvas_key_state not in st.session_state:
                canvas_key = f"canvas_{sheet}_{int(time.time() * 1000) % 10000}"
                st.session_state[canvas_key_state] = canvas_key
            else:
                canvas_key = st.session_state[canvas_key_state]

            canvas_result = st_canvas(
                fill_color="rgba(255, 165, 0, 0.3)",
                stroke_width=2,
                stroke_color="#000000",
                background_color="#eee",
                background_image=bg_image,
                update_streamlit=True,
                height=new_height,
                width=new_width,
                drawing_mode="rect",
                point_display_radius=0,
                key=canvas_key,
            )
            
            # Rest of your canvas logic...
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

                        st.success(f"Closest text: {st.session_state.clicked_text}")
                        st.write(f"Matched BBox Index: {closest_index}")
                        st.write(f"Matched BBox: {matched_bbox}")
                        st.write(f"Clicked at: ({round(x_click)}, {round(y_click)})")

        def save_image_and_get_path(self, image_base64: str, sheet: str, output_dir="saved_images") -> str:
            os.makedirs(output_dir, exist_ok=True)
            
            # Remove base64 header if present
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]
            
            image_path = os.path.join(output_dir, f"{sheet}.png")
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image_base64))
            
            return image_path

        
        def transform_and_send(self, data: dict, database_url: str):

            self.img_path = self.save_image_and_get_path(self.input.img_base64, sheet)

            transformed_data = {
                "image_base64": self.img_path,
                "raw_response": self.input.raw_response,
                "page_number": 1,
                # "response": json.dumps(data['bs']['raw_response'])  # <-- double check server expects a string
                'response': md
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
            
        def update_json_file(self, key, value):
            # Ensure directory exists

            filepath='json/variables.json'
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Load existing JSON if available
            try:
                with open(filepath, 'r') as file:
                    data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {}

            # Update and write
            data[key] = value
            with open(filepath, 'w') as file:
                json.dump(data, file, indent=4)
        


    data_formation = DataFormationandStorage(input_obj)

    st.title("Financial Data Table")

    # Load and store dataframe in session state
    df = data_formation.display_editable_dataframe()

    img_array = data_formation.json2im(input_obj.img_base64)
    
    if img_array is not None:
        try:
            bg_image = Image.fromarray(img_array)
            
            # Store image in session state with proper key
            image_key = f"{sheet}_image"
            if image_key not in st.session_state:
                st.session_state[image_key] = bg_image
            else:
                # Always use the stored image to maintain consistency
                bg_image = st.session_state[image_key]
                
        except UnidentifiedImageError:
            st.error("Failed to convert image array to PIL image.")
            st.stop()
    else:
        st.stop()


    if sheet == "bs":
        if 'bs_image' not in st.session_state:
            st.session_state.bs_image = bg_image
        bg_image = st.session_state.bs_image
    elif sheet == "is":
        if 'is_image' not in st.session_state:
            st.session_state.is_image = bg_image
        bg_image = st.session_state.is_image
    elif sheet == "cfs":
        if 'cfs_image' not in st.session_state:
            st.session_state.cfs_image = bg_image
        bg_image = st.session_state.cfs_image




    if df is not None:
        if sheet =="bs":
            if 'bs_df' not in st.session_state:
                st.session_state.bs_df = df
            else:
                df = st.session_state.bs_df

        if sheet =="is":
            if 'is_df' not in st.session_state:
                st.session_state.is_df = df
            else:
                df = st.session_state.is_df

        if sheet =="cfs":
            if 'cfs_df' not in st.session_state:
                st.session_state.cfs_df = df
            else:
                df = st.session_state.cfs_df

        st.markdown("### Column and Row Operations")

        # row_col1, row_col2 = st.columns([1, 1])

        row_col1, row_col2, row_col3 = st.columns([1, 1, 1])

        with row_col1:
            st.markdown('<div class="three-col-section">', unsafe_allow_html=True)
            st.subheader("🧩 Add Row / Rename Column")

            if 'selected_index' not in st.session_state:
                st.session_state.selected_index = len(df)

            selected_index_input = st.text_input("Index to add row:", value=str(st.session_state.selected_index), key=f"index_add_row_input_{sheet}")

            if selected_index_input.isdigit():
                selected_index = int(selected_index_input)
                st.session_state.selected_index = selected_index
            else:
                selected_index = len(df)
                st.warning("Please enter a valid integer index. Using end of dataframe as default.")

            if selected_index < 0 or selected_index > len(df):
                st.error(f"Index {selected_index} is out of bounds. Using end of dataframe instead.")
                selected_index = len(df)
                st.session_state.selected_index = selected_index

            if st.button("➕ Add Row", key=f"add_row_button_{sheet}"):
                empty_row = {col: '' for col in df.columns}
                new_row_df = pd.DataFrame([empty_row])
                top_part = df.iloc[:selected_index]
                bottom_part = df.iloc[selected_index:]
                edited_df = pd.concat([top_part, new_row_df, bottom_part], ignore_index=True)

                if sheet == "bs":
                    st.session_state.bs_df = edited_df
                    st.session_state.bs = edited_df.to_dict(orient='list')
                elif sheet == "is":
                    st.session_state.is_df = edited_df
                    st.session_state.Is = edited_df.to_dict(orient='list')
                elif sheet == "cfs":
                    st.session_state.cfs_df = edited_df
                    st.session_state.cfs = edited_df.to_dict(orient='list')
                st.success(f"Empty row added at index {selected_index}!")

            col_to_rename = st.selectbox("Select column to rename", df.columns, key=f"rename_selector_{sheet}")
            new_col_name = st.text_input("New column name", key=f"rename_input_{sheet}", max_chars=15)
            if st.button("✏️ Rename Column", key=f"rename_column_button_{sheet}"):
                if new_col_name.strip():
                    df.rename(columns={col_to_rename: new_col_name.strip()}, inplace=True)
                    if sheet == "bs":
                        st.session_state.bs_df = df
                        st.session_state.bs = df.to_dict(orient='list')
                        st.success(f"Renamed '{col_to_rename}' to '{new_col_name.strip()}'")
                    elif sheet == "is":
                        st.session_state.is_df = df
                        st.session_state.Is = df.to_dict(orient='list')
                        st.success(f"Renamed '{col_to_rename}' to '{new_col_name.strip()}'")
                    elif sheet == "cfs":
                        st.session_state.cfs_df = df
                        st.session_state.cfs = df.to_dict(orient='list')
                        st.success(f"Renamed '{col_to_rename}' to '{new_col_name.strip()}'")
                else:
                    st.warning("Please enter a valid new column name.")

            st.markdown('</div>', unsafe_allow_html=True)

        with row_col2:
            st.markdown('<div class="three-col-section">', unsafe_allow_html=True)
            st.subheader("📐 Add / Delete Column")

            column_name_input = st.text_input("New column name", "New Column", max_chars=15, key=f"new_column_name_input_{sheet}")
            if st.button("➕ Add Column", key=f"add_column_button_{sheet}"):
                new_column_name = column_name_input.strip() or f"New Column {len(df.columns) + 1}"
                df[new_column_name] = ''
                if sheet == "bs":
                    st.session_state.bs_df = df
                    st.session_state.bs = df.to_dict(orient='list')
                    st.success(f"New column '{new_column_name}' added!")
                elif sheet == "is":
                    st.session_state.is_df = df
                    st.session_state.Is = df.to_dict(orient='list')
                    st.success(f"New column '{new_column_name}' added!")
                elif sheet == "cfs":
                    st.session_state.cfs_df = df
                    st.session_state.cfs = df.to_dict(orient='list')
                    st.success(f"New column '{new_column_name}' added!")

            column_to_delete = st.selectbox("Select column to delete", df.columns, key=f"delete_selector_{sheet}")
            if st.button("❌ Delete Column", key=f"delete_column_button_{sheet}"):
                if column_to_delete:
                    df.drop(columns=[column_to_delete], inplace=True)

                    if sheet == "bs":
                        st.session_state.bs_df = df
                        st.session_state.bs = df.to_dict(orient='list')
                        st.success(f"Deleted column '{column_to_delete}'")
                    elif sheet == "is":
                        st.session_state.is_df = df
                        st.session_state.Is = df.to_dict(orient='list')
                        st.success(f"Deleted column '{column_to_delete}'")
                    elif sheet == "cfs":
                        st.session_state.cfs_df = df
                        st.session_state.cfs = df.to_dict(orient='list')
                        st.success(f"Deleted column '{column_to_delete}'")

            st.markdown('</div>', unsafe_allow_html=True)

        with row_col3:
            st.markdown('<div class="three-col-section">', unsafe_allow_html=True)
            st.subheader("🖊️ Edit Cell")

            if sheet == "bs":
                df = st.session_state.bs_df
            elif sheet == "is":
                df = st.session_state.is_df
            elif sheet == "cfs":
                df = st.session_state.cfs_df
            edited_df_with_index = df.reset_index(drop=True)

            # Initialize clicked text in session state
            if "clicked_text" not in st.session_state:
                st.session_state.clicked_text = ""

            selected_row = st.number_input("Row", min_value=0, max_value=len(edited_df_with_index)-1, step=1)
            selected_column = st.selectbox("Column", edited_df_with_index.columns)

            st.info(f"Inserting {st.session_state.clicked_text} in Row {selected_row}, Column '{selected_column}'")

            if st.button("📥 Insert Text", key=f"insert_{sheet}"):
                if selected_column in edited_df_with_index.columns:
                    edited_df_with_index.at[selected_row, selected_column] = st.session_state.clicked_text

                    # Save back to session_state
                    if sheet == "bs":
                        st.session_state.bs_df = edited_df_with_index
                        st.session_state.bs = edited_df_with_index.to_dict(orient='list')
                    elif sheet == "is":
                        st.session_state.is_df = edited_df_with_index
                        st.session_state.Is = edited_df_with_index.to_dict(orient='list')
                    elif sheet == "cfs":
                        st.session_state.cfs_df = edited_df_with_index
                        st.session_state.cfs = edited_df_with_index.to_dict(orient='list')

                    st.success(f"Inserted '{st.session_state.clicked_text}' into row {selected_row}, column '{selected_column}'")

            st.markdown('</div>', unsafe_allow_html=True)



    # Two-column layout
    col1, col2 = st.columns(2)

    with col1:
        if sheet == "bs":
            st.write("### Balance Sheet")
            # image = st.session_state.bs_image
        elif sheet == "is":
            st.write("### Income Statement")
            # image = st.session_state.is_image
        elif sheet == "cfs":
            st.write("### Cash Flow Statement")
            # image = st.session_state.cfs_image
        st.markdown("##### Click on the image to select text")

        data_formation.draw_canvas(bg_image)

        # Add a button to clear canvas state for testing
        if st.button(f"Clear Canvas State - {sheet}"):
            keys_to_clear = [k for k in st.session_state.keys() if f"canvas_{sheet}" in k]
            for key in keys_to_clear:
                del st.session_state[key]
            st.rerun()
        


    with col2:
        st.write("### Edit Financial Data")
        # Toggle editor
        on = st.toggle("Edit Table", key=f"toggle_editor_{sheet}")

        if on:
            edited_df = st.data_editor(
                edited_df_with_index,
                use_container_width=True,
                num_rows="dynamic",
                hide_index=False
            )
            if sheet == "bs":
                st.session_state.bs_df = edited_df
            elif sheet == "is":
                st.session_state.is_df = edited_df
            elif sheet == "cfs":
                st.session_state.cfs_df = edited_df
        else:
            if sheet == "bs":
                edited_df = st.session_state.bs_df
            elif sheet == "is":
                edited_df = st.session_state.is_df
            elif sheet == "cfs":
                edited_df = st.session_state.cfs_df
            

            html = edited_df.map(frontend_helper.format_bold_html).to_html(escape=False, index=True, justify='left')
            st.markdown(f"""
            <div style="max-height: 800px; overflow-y: auto; margin: 1rem 0;">
                {html}
            </div>
            """, unsafe_allow_html=True)



        if st.button("Next", key=f"next_button_{sheet}"):
            if "index" in edited_df.columns:
                edited_df_no_index = edited_df.drop(columns=["index"])
            else:
                edited_df_no_index = edited_df.copy()

            # edited_df_no_index = edited_df.drop(columns=["index"])
            edited_json = edited_df_no_index.to_dict(orient='list')
            md = data_formation.json_to_markdown_table(edited_json)

            if sheet == "bs":
                st.session_state.bs_df = edited_df_no_index
                st.session_state.bs = edited_json
                st.success("Changes saved successfully as JSON!")
            elif sheet == "is":
                st.session_state.is_df = edited_df_no_index
                st.session_state.Is = edited_json
                st.success("Changes saved successfully as JSON!")
            elif sheet == "cfs":
                st.session_state.cfs_df = edited_df_no_index
                st.session_state.cfs = edited_json
                st.success("Changes saved successfully as JSON!")
            
            
            url = "http://192.168.10.50:8000/store_ocr_data"
            storedb = data_formation.transform_and_send(input_obj.input_data, url)
            print(f"📥 THE DATABASE RESPONSE IS: {storedb}")

            if sheet == "bs":
                if storedb['status'] == 'success' and 'response' in storedb:
                    balance_id = storedb['response']['id']
                    print(f"[DEBUG] balance_id: {balance_id}, type: {type(balance_id)}")
                    data_formation.update_json_file('balance_id', balance_id)
                    st.success("Changes saved and data stored successfully!")

            elif sheet == "is":
                if storedb['status'] == 'success' and 'response' in storedb:
                    income_id = storedb['response']['id']
                    print(f"[DEBUG] income_id: {income_id}, type: {type(income_id)}")
                    data_formation.update_json_file('income_id', income_id)
                    st.success("Changes saved and data stored successfully!")

            elif sheet == "cfs":
                if storedb['status'] == 'success' and 'response' in storedb:
                    cash_id = storedb['response']['id']
                    print(f"[DEBUG] cash_id: {cash_id}, type: {type(cash_id)}")
                    data_formation.update_json_file('cash_id', cash_id)
                    st.success("Changes saved and data stored successfully!")

            
                # st.switch_page("pages/is.py")

            else:
                st.error(f"Database error: {storedb['error']}")

        

        # if st.button("Skip", key=f"skip_button_{sheet}"):
        #     st.success("Changes saved successfully as JSON!")
            # st.switch_page("pages/is.py")


st.title("Financial Data Processing App")
st.markdown("This app processes financial data from images and allows you to edit and store it.")
# Optional: Add navigation hints
st.markdown("""
### 📝 Instructions:
1. Select the financial statement type from the dropdown above
2. Click on the image to select text elements
3. Edit the data table as needed
4. Click 'Next' to save and proceed, or 'Skip' to move forward without saving
""")

# tab1, tab2, tab3 = st.tabs(["Balance Sheet", "Income Sheet", "Cash Flow Sheet"])

# with tab1:
#     st.write("Balance Sheet Section")
#     pages("bs")  # Your existing pages function

# with tab2:
#     st.write("Income Statement Section")
#     pages("is")

# with tab3:
#     st.write("Cash Flow Statement Section")
#     pages("cfs")

sheet_options = {
    "bs": "📊 Balance Sheet",
    "is": "💰 Income Statement", 
    "cfs": "💸 Cash Flow Statement"
}

selected_sheet = st.selectbox(
    "Select Financial Statement to Process:",
    options=list(sheet_options.keys()),
    format_func=lambda x: sheet_options[x],
    index=0  # Default to Balance Sheet
)

# Display current selection
st.info(f"Currently processing: **{sheet_options[selected_sheet]}**")

# Call the pages function with selected sheet
if selected_sheet:
    # try:
    pages(selected_sheet)
    # except Exception as e:
    #     st.error(f"Error loading {sheet_options[selected_sheet]}: {e}")
    #     st.write("Error details:", str(e))


