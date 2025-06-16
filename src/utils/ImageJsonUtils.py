import cv2
import numpy as np
import base64
import json
import pickle
from PIL import Image
import os
import uuid


class imageUtils():
    def im2json(self, im):
        """Convert a Numpy array to a JSON-serializable dict"""
        imdata = pickle.dumps(im)
        encoded = base64.b64encode(imdata).decode('ascii')
        return {"image": encoded}

    def json2im(self, data) -> np.ndarray:
        """Convert a dict (or JSON string) back to a Numpy array"""
        if isinstance(data, str):
            data = json.loads(data)  # convert JSON string to dict
        imdata = base64.b64decode(data['image'])
        im = pickle.loads(imdata)
        return im
    def save_encoded_image(self, encoded_image_str, save_dir="encoded_images"):
        """Save base64-encoded image string (pickled) to a file"""
        os.makedirs(save_dir, exist_ok=True)
        filename = f"{uuid.uuid4().hex}.txt"  # or .bin depending on your preference
        file_path = os.path.join(save_dir, filename)

        with open(file_path, "w") as f:
            f.write(encoded_image_str)

        return file_path