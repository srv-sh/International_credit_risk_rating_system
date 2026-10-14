FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System libs for OpenCV, Paddle and pdf2image
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 libgomp1 poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --upgrade pip && pip install -r requirements-docker.txt

COPY . .

# src/GetTableFromImage.py loads YOLO weights from a hardcoded absolute path
RUN mkdir -p /home/sourav/workspace/CreditScoring-refined-/data \
    && cp runs/detect/train3/weights/best.pt /home/sourav/workspace/CreditScoring-refined-/data/best.pt

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
