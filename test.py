import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import io
import math
from input_data import input

# Add this at the top of your script (before any Streamlit commands)
st.set_page_config(layout="wide")

obj = input()

input_data = obj.get_data()

# Load original image
image_path = "test_images/aci1.png"
image = Image.open(image_path)
original_width, original_height = image.size
# print(f"Original image size: {original_width}x{original_height}")

# OCR Data (Replace with your actual data)
texts = input_data["bs"]["paddleOCR"]["text"]
bounding_boxes = input_data["bs"]["paddleOCR"]["bbox"]

# Show the image without resizing or cropping
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=2,
    stroke_color="red",
    background_image=image,
    update_streamlit=True,
    height=original_height,
    width=original_width,
    drawing_mode="point",
    key="canvas"
)

# Helper functions
def get_center(box):
    x, y, w, h = box
    return (x + w / 2, y + h / 2)

def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Handle canvas clicks
if canvas_result.json_data is not None:
    for obj in canvas_result.json_data["objects"]:
        click_point = (int(obj['left']), int(obj['top']))
        st.write(f"🖱️ Clicked at: {click_point}")

        # Find closest bounding box
        distances = []
        for i, box in enumerate(bounding_boxes):
            center = get_center(box)
            dist = euclidean_distance(click_point, center)
            distances.append((dist, i))
        
        # Get top 3 closest
        top_3 = sorted(distances)[:3]

        # Draw on a copy of the original image
        image_with_boxes = image.copy()
        draw = ImageDraw.Draw(image_with_boxes)

        for dist, idx in top_3:
            x, y, w, h = bounding_boxes[idx]
            draw.rectangle([(x, y), (x + w, y + h)], outline="green", width=3)
            draw.text((x, y - 10), texts[idx], fill="green")
            st.write(f"📌 Closest text: {texts[idx]} (distance: {dist:.2f})")
            st.write(f"📦 Bounding box: {bounding_boxes[idx]}")

        st.image(image_with_boxes, caption="📍 Closest bounding boxes")