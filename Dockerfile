FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    TESSDATA_PREFIX=/app/weights/tessdata \
    DOCLING_MODEL_PATH=/app/weights/models_docling

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./adp ./adp
COPY ./tests ./tests
COPY pytest.ini ./
 
EXPOSE 8000

