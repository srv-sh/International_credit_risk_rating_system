import json
import os
import sys
from pathlib import Path

from PIL import Image

from src.GetDataFromTablePaddle import getData


def run(image_path: str, provider: str | None = None):
    extractor = getData(provider=provider)
    image = Image.open(image_path).convert("RGB")
    return extractor.get_stucture_data(image)


if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else "data/aci1.jpg"
    provider = sys.argv[2] if len(sys.argv) > 2 else os.getenv("LLM_PROVIDER", "gemini")
    output = run(image_path, provider=provider)
    Path("result.json").write_text(json.dumps(output, indent=4, default=str))
    print(f"Wrote result.json from {image_path} using {provider}")
