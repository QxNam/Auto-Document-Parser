# api/v1/routes/view.py
import time
from fastapi import APIRouter, UploadFile, File, HTTPException

from configs.settings import settings
from services.parser.manager import ParserManager  # đổi import nếu bạn dùng parser.py / manager.py


router = APIRouter(prefix="/api/v1", tags=["File"])


def _validate_view_file(file: UploadFile, content: bytes):
    # View API: bạn yêu cầu giới hạn nhỏ hơn (<10MB). Mình dùng đúng 10MB theo config.
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail={"status": "error", "message": "File too large for direct preview"},
        )


@router.post("/view")
async def view_parse_file(file: UploadFile = File(...)):
    started = time.time()

    # 1) Read file
    content = await file.read()

    # 2) Validate size (sync endpoint)
    _validate_view_file(file, content)

    # 3) Parse in-memory
    try:
        pm = ParserManager()
        # tuỳ manager bạn: thường sẽ chọn parser theo ext/mime
        parsed = pm.parse_bytes(
            data=content,
            file_name=file.filename or "file",
            content_type=file.content_type,
        )
        # parsed nên là dict/json-serializable
    except TimeoutError:
        raise HTTPException(status_code=504, detail={"status": "error", "message": "Parsing process took too long"})
    except Exception:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Cannot parse this file format"})

    elapsed = round(time.time() - started, 4)
    return {"status": "success", "data": {"content": parsed, "time": elapsed}}
