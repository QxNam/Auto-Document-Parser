FROM python:3.12-slim


WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    TESSDATA_PREFIX=/app/weights/tessdata \
    DOCLING_MODEL_PATH=/app/weights/models_docling


RUN pip install docling==2.60.1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
        # dependency for docling
        libgl1 \
        libglx0 \
        libxcb1 \
        libx11-6 \
        libglib2.0-0 \
        # OCR components (Tesseract 5)
        tesseract-ocr \
        tesseract-ocr-vie \
        tesseract-ocr-eng \
        # pdf/image process
        poppler-utils \
        libpng16-16 \
        libxslt1.1 && \
    # free image
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* \
           /tmp/* \
           /var/tmp/* \
           /usr/share/doc/* \
           /usr/share/man/*

COPY ./adp ./adp
COPY ./tests ./tests
COPY pytest.ini ./
 
EXPOSE 8000

