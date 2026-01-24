import io
from pypdf import PdfReader
# from docx import Document
from adp.configs.logger import worker_logger as logger
from adp.configs.settings import settings

API_TIMEOUT_INTERVAL=settings.API_TIMEOUT_INTERVAL
MAX_FILE_SIZE_MB=settings.MAX_FILE_SIZE_MB
MAX_PAGE_COUNT=settings.MAX_PAGE_COUNT
ALLOWED_FILE_EXTENSIONS=settings.ALLOWED_FILE_EXTENSIONS

def valid_file_extension(file_name: str) -> bool:
    """Check if the file has a valid extension."""
    extension = file_name.split('.')[-1].lower()
    return extension in ALLOWED_FILE_EXTENSIONS

def valid_file_size(file_obj: io.BytesIO) -> bool:
    """Check if the file size is within the allowed limit."""
    file_obj.seek(0, io.SEEK_END)
    size_mb = file_obj.tell() / (1024 * 1024)
    file_obj.seek(0)
    return size_mb <= MAX_FILE_SIZE_MB

def valid_page_count(file_obj: io.BytesIO, file_name: str) -> bool:
    """Check if the file has a valid number of pages."""
    extension = file_name.split('.')[-1].lower()
    page_count = 0

    if extension == 'pdf':
        reader = PdfReader(file_obj)
        page_count = len(reader.pages)
    # elif extension in ['docx', 'doc']:
    #     document = Document(file_obj)
    #     page_count = len(document.paragraphs) // 30  # Rough estimate: 30 paragraphs per page

    return page_count <= MAX_PAGE_COUNT

def check(file_obj: io.BytesIO, file_name: str) -> bool:
    """Perform all validations on the file."""
    if not valid_file_extension(file_name):
        logger.error(f"Invalid file extension for file: {file_name}")
        return False
    if not valid_file_size(file_obj):
        logger.error(f"File size exceeds limit for file: {file_name}")
        return False
    if not valid_page_count(file_obj, file_name):
        logger.error(f"Page count exceeds limit for file: {file_name}")
        return False
    return True