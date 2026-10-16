# Build from the project root: docker build -f api/Dockerfile .
FROM python:3.12-slim
WORKDIR /app
COPY api/requirements.txt api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt
COPY api/ api/
COPY source/ source/
COPY json/ json/
COPY saved_responses/ saved_responses/
EXPOSE 8002
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8002"]
