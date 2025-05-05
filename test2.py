import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import math
from input_data import input


# Add this at the top of your script (before any Streamlit commands)
st.set_page_config(layout="wide")

obj = input()

input_data = obj.get_data()

# Your image and OCR data
image_path = "test_images/aci1.png"
image = Image.open(image_path)

# Example input (replace these with your actual values)
texts = input_data["bs"]["paddleOCR"]["text"]
bounding_boxes = input_data["bs"]["paddleOCR"]["bbox"]  # each bbox: [[x1, y1], [x2, y2], ...]

# Streamlit canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 0, 0, 0.3)",
    stroke_width=1,
    background_image=image,
    update_streamlit=True,
    height=image.height,
    width=image.width,
    drawing_mode="point",
    key="canvas",
)

def get_bbox_center(bbox):
    # Reshape flat bbox to list of (x, y) tuples
    points = list(zip(bbox[::2], bbox[1::2]))
    x_coords = [pt[0] for pt in points]
    y_coords = [pt[1] for pt in points]
    return (sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords))


# Find the closest bbox to the clicked point
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

        # Draw the closest bounding box
        bbox = bounding_boxes[closest_index]
        annotated_img = image.copy()
        draw = ImageDraw.Draw(annotated_img)
        draw.polygon(list(zip(bbox[::2], bbox[1::2])), outline="red", width=3)

        # st.image(annotated_img, caption="Closest bounding box highlighted")

        # Show the matched text
        st.success(f"Closest text: {texts[closest_index]}")
        st.write(f"Clicked at: ({round(x_click)}, {round(y_click)})")
