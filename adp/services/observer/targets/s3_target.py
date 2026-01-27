
import io
from pathlib import Path
from adp.configs.settings import settings
from adp.services.observer.base_observer import BaseObserver
from adp.services.storage.s3 import s3_service
from adp.configs.logger import worker_logger as logger

S3_BUCKET_NAME_OUTPUT = settings.S3_BUCKET_NAME_OUTPUT

class S3Target(BaseObserver):
    def __init__(self):
        pass
    
    async def update(self, data: str, file_name: str) -> str:
        """
        Asynchronously send data to S3 as a markdown file.
        """
        
        file_name = Path(file_name).with_suffix('.md')

        # Convert markdown string to BytesIO
        md_file_obj = io.BytesIO(data.encode('utf-8'))
        
        # Upload markdown to S3
        upload_result = s3_service.upload_fileobj(
            file_obj=md_file_obj,
            bucket_name=S3_BUCKET_NAME_OUTPUT,
            object_key=str(file_name),
            extra_args={'ContentType': 'text/markdown'}
        )

        s3_output_uri = upload_result['uri']
        logger.info(f"[Observer] Saved parsed markdown to S3, URI: {s3_output_uri}")
        return s3_output_uri
    
    async def close(self):
        pass
