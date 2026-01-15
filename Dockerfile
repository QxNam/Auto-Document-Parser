FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY requirements.txt .
# RUN apk add --no-cache krb5-dev krb5-libs krb5
RUN pip install --no-cache-dir -r requirements.txt

COPY ./adp ./adp
COPY ./tests ./tests
COPY pytest.ini ./
 
EXPOSE 8000
