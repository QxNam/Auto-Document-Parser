#!/bin/bash
set -e

# -------------------------------------------------------
# Load environment file nếu tồn tại
# -------------------------------------------------------
if [ -f /mnt/secrets/.env ]; then
    echo "[entrypoint] Loading /mnt/secrets/.env"
    set -a
    . /mnt/secrets/.env
    set +a
fi

# -------------------------------------------------------
# Ensure LibreOffice + dconf directories exist
# -------------------------------------------------------
echo "[entrypoint] Ensure LibreOffice + dconf directories exist..."
mkdir -p /tmp/.cache/dconf /tmp/lo_profile
chmod -R 777 /tmp/.cache /tmp/lo_profile

# -------------------------------------------------------
# Optional: set HOME cho LibreOffice
# -------------------------------------------------------
export HOME=/tmp
export USERPROFILE=/tmp
export LO_USER_PROFILE=/tmp/lo_profile

# -------------------------------------------------------
# Download models (block until done)
# -------------------------------------------------------
# echo "[entrypoint] Downloading and extracting Docling models..."
# python /app/src/scripts/download_models_docling.py || echo "[entrypoint] Warning: download_models_docling.py failed"

# -------------------------------------------------------
# Start parser_worker với auto-restart
# -------------------------------------------------------
echo "[entrypoint] Starting parser_worker with auto-restart..."
(
  while true; do
    python -m src.main 2>&1
    echo "[entrypoint] parser_worker crashed. Restarting in 5s..."
    sleep 5
  done
) &

# -------------------------------------------------------
# Start API server với auto-restart
# -------------------------------------------------------
echo "[entrypoint] Starting API server with auto-restart..."
(
  while true; do
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 1 2>&1
    echo "[entrypoint] API server crashed. Restarting in 5s..."
    sleep 5
  done
) &

# -------------------------------------------------------
# Wait tất cả process background
# -------------------------------------------------------
wait
