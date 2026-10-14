# CredirScoring

OCR-to-LLM pipeline for table images. The app reads an image, extracts table text with PaddleOCR, then formats the result with OpenAI or Gemini.

## Docker Setup
1. Create your env file:
```powershell
copy .env.example .env
```

2. Edit `.env` and add your API key and provider settings.

3. Build the image:
```powershell
docker build -t ocr-table-api .
```

4. Run the API:
```powershell
docker run -p 8000:8000 --env-file .env ocr-table-api
```

5. Open Swagger:
```text
http://127.0.0.1:8000/docs
```

## API Usage
- `GET /health` checks the server.
- `POST /extract` expects exactly 3 uploaded image files: `file1`, `file2`, `file3`.
- Add `?provider=openai` or `?provider=gemini` to choose the LLM.

Example:
```bash
curl -X POST "http://127.0.0.1:8000/extract?provider=gemini" \
  -F "file1=@image1.jpg" \
  -F "file2=@image2.jpg" \
  -F "file3=@image3.jpg"
```

## Local Run
If you want to run without Docker:
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirement.txt
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

## Environment Variables
`.env.example` contains the supported values:
- `LLM_PROVIDER`
- `GOOGLE_API_KEY`
- `GEMINI_MODEL`
- `GEMINI_FALLBACK_MODEL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`

## Notes
- Use `provider=openai` only if `OPENAI_API_KEY` is set.
- Use `provider=gemini` only if `GOOGLE_API_KEY` is set.
- The batch endpoint processes the 3 files one by one for simpler debugging.
