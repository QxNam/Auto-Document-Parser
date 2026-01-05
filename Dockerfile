FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m -u 1000 adp && \
    update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.12 20 && \
    update-alternatives --set python3 /usr/local/bin/python3.12 && \
    ln -sf /usr/local/bin/python3.12 /usr/bin/python
COPY --chown=adp:adp ./adp ./adp

USER adp
EXPOSE 8000
CMD ["/app/docker-entrypoint.sh"]