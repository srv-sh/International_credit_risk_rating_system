from PIL import Image
from io import BytesIO

from .GetDataFromTablePaddle import getData


class TablePipeline:
    """Single entry point for table detection, Paddle OCR, and LLM formatting."""

    def __init__(self):
        self.extractor = getData()

    def process_image(self, image: Image.Image):
        """Return the structured table output for a PIL image."""
        return self.extractor.get_stucture_data(image)

    def process_image_bytes(self, image_bytes: bytes):
        """Return the structured table output for raw image bytes."""
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        return self.process_image(image)
