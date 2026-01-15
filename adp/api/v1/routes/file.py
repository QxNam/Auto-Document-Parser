# api/v1/routes/file.py
import json
import time
import uuid
import re
from typing import Optional, Dict, Any

from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException

from configs.settings import settings
from services.storage.s3 import S3Storage
from services.message_queue.kafka_producer import KafkaQueue  # bạn đổi tên nếu khác
from services.repository.db import SessionLocal
from services.repository.models import DocumentMetadata


router = APIRouter(prefix="/api/v1", tags=["File"])

# ---------------------------
# In-memory rate limit store
# api_key -> {"window": int, "count": int}
# ---------------------------
_rate_store: Dict[str, Dict[str, Any]] = {}


def _check_api_key(x_api_key: Optional[str]):
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail={"error": "Invalid or missing API key"})


def _rate_limit_or_429(x_api_key: str):
    """
    Rate limit: 100 req/min (simple in-memory)
    Return 429 with reset epoch if exceeded
    """
    now = int(time.time())
    window = now // 60
    entry = _rate_store.get(x_api_key)

    if not entry or entry["window"] != window:
        _rate_store[x_api_key] = {"window": window, "count": 1}
        return

    entry["count"] += 1
    if entry["count"] > settings.RATE_LIMIT_PER_MIN:
        reset = (window + 1) * 60
        raise HTTPException(
            status_code=429,
            detail={"error": "Rate limit exceeded", "limit": settings.RATE_LIMIT_PER_MIN, "reset": reset},
        )


def _sanitize_filename(name: str) -> str:
    # remove path traversal and unsafe chars
    name = name.replace("\\", "/").split("/")[-1]
    name = re.sub(r"[^a-zA-Z0-9.\-_ ]", "_", name)
    # avoid empty
    return name or "file"


def _validate_file(file: UploadFile, content: bytes):
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail={"error": f"Invalid file format. Max size is {settings.MAX_FILE_SIZE_MB}MB"},
        )

    filename = file.filename or ""
    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in {
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".png", ".jpg", ".jpeg"
    }:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid file format. Support PDF, DOC/DOCX, XLS/XLSX, PPT/PPTX allowed"},
        )


def _parse_metadata(metadata: Optional[str]) -> Optional[dict]:
    if not metadata:
        return None
    try:
        obj = json.loads(metadata)
        if not isinstance(obj, dict):
            raise ValueError("metadata must be a JSON object")
        return obj
    except Exception:
        raise HTTPException(status_code=400, detail={"error": "metadata must be a valid JSON object string"})


@router.post("/file")
async def upload_file_to_queue(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    # 1) Auth + Rate limit
    _check_api_key(x_api_key)
    _rate_limit_or_429(x_api_key)

    # 2) Read file bytes (for validation + upload)
    content = await file.read()

    # 3) Validation
    _validate_file(file, content)

    # 4) Parse metadata (optional)
    metadata_obj = _parse_metadata(metadata)

    # 5) Storage: upload to S3
    request_id = str(uuid.uuid4())
    safe_name = _sanitize_filename(file.filename or "file")
    # S3 key includes request_id to avoid collisions
    s3_key = f"{settings.S3_PREFIX}/{request_id}/{safe_name}"

    s3 = S3Storage()
    try:
        s3_uri = s3.upload_bytes(
            key=s3_key,
            data=content,
            content_type=file.content_type,
        )
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "Upload failed due to internal storage error"})

    # 6) Storage: save metadata to Postgres
    db = SessionLocal()
    try:
        row = DocumentMetadata(
            original_filename=safe_name,
            content_type=file.content_type,
            s3_uri=s3_uri,
            metadata_json=json.dumps(metadata_obj) if metadata_obj else None,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        metadata_id = row.id
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail={"error": "Upload failed due to internal storage error"})
    finally:
        db.close()

    # 7) Messaging: push to Kafka
    # message format requested:
    # {
    #   "uri_s3": "",
    #   "metadata_id": "",
    #   "created_at": ""
    # }
    msg = {
        "uri_s3": s3_uri,
        "metadata_id": str(metadata_id),
        "created_at": int(time.time()),
        "request_id": request_id,
        "metadata": metadata_obj or {},
    }

    try:
        mq = KafkaQueue()
        mq.publish(topic=settings.KAFKA_TOPIC, value=msg)
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "Upload failed due to internal storage error"})
    return {"message": "Document upload accepted", "request_id": request_id}
