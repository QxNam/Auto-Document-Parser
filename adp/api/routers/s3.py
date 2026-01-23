"""FastAPI router for S3 CRUD operations."""

import os
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse

from adp.api.models import (
    FileUploadResponse,
    FileDeleteResponse,
    PresignedUrlResponse,
    ErrorResponse,
)
from adp.configs.logger import get_logger
from adp.services.storage.s3 import S3Service

logger = get_logger(__name__)

router = APIRouter(prefix="/api/s3", tags=["S3 Operations"])

# Initialize S3 service
s3_service = S3Service()


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def upload_file(
    file: UploadFile = File(...),
    s3_key: str = Query(..., description="S3 object key/path"),
    bucket: Optional[str] = Query(None, description="S3 bucket name (optional)"),
    generate_url: bool = Query(False, description="Generate presigned URL after upload"),
) -> FileUploadResponse:
    """
    Upload a file to S3.

    - **file**: The file to upload (multipart/form-data)
    - **s3_key**: The S3 object key (path) where the file will be stored
    - **bucket**: Optional bucket name (defaults to configured bucket)
    - **generate_url**: If True, generates and returns a presigned URL
    """
    temp_file_path = None
    try:
        # Save uploaded file temporarily
        temp_file_path = f"/tmp/{file.filename}"
        os.makedirs("/tmp", exist_ok=True)

        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Upload to S3
        success = s3_service.upload_file(temp_file_path, s3_key, bucket)

        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to upload file to S3",
            )

        s3_uri = s3_service.get_uri(s3_key, bucket)
        presigned_url = None

        if generate_url:
            presigned_url = s3_service.get_presigned_url(s3_key, bucket=bucket)

        return FileUploadResponse(
            success=True,
            message=f"File '{file.filename}' uploaded successfully",
            s3_key=s3_key,
            s3_uri=s3_uri,
            presigned_url=presigned_url,
        )

    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError as e:
                logger.warning(f"Failed to clean up temp file: {e}")


@router.delete(
    "/delete",
    response_model=FileDeleteResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def delete_file(
    s3_key: str = Query(..., description="S3 object key to delete"),
    bucket: Optional[str] = Query(None, description="S3 bucket name (optional)"),
) -> FileDeleteResponse:
    """
    Delete a file from S3.

    - **s3_key**: The S3 object key to delete
    - **bucket**: Optional bucket name (defaults to configured bucket)
    """
    try:
        success = s3_service.delete_file(s3_key, bucket)

        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to delete file from S3",
            )

        return FileDeleteResponse(
            success=True,
            message=f"File '{s3_key}' deleted successfully",
            s3_key=s3_key,
        )

    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )


@router.get(
    "/presigned-url",
    response_model=PresignedUrlResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_presigned_url(
    s3_key: str = Query(..., description="S3 object key"),
    expiration: int = Query(3600, ge=1, le=604800, description="URL expiration in seconds (1s - 7d)"),
    bucket: Optional[str] = Query(None, description="S3 bucket name (optional)"),
) -> PresignedUrlResponse:
    """
    Generate a presigned URL for accessing a file in S3.

    - **s3_key**: The S3 object key
    - **expiration**: URL expiration time in seconds (default: 3600 = 1 hour, max: 604800 = 7 days)
    - **bucket**: Optional bucket name (defaults to configured bucket)
    """
    try:
        presigned_url = s3_service.get_presigned_url(s3_key, expiration, bucket)

        if not presigned_url:
            raise HTTPException(
                status_code=400,
                detail="Failed to generate presigned URL",
            )

        return PresignedUrlResponse(
            s3_key=s3_key,
            presigned_url=presigned_url,
            expires_in=expiration,
        )

    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )


@router.get(
    "/exists",
    responses={200: {"description": "File existence check result"}, 500: {"model": ErrorResponse}},
)
async def check_file_exists(
    s3_key: str = Query(..., description="S3 object key to check"),
    bucket: Optional[str] = Query(None, description="S3 bucket name (optional)"),
):
    """
    Check if a file exists in S3.

    - **s3_key**: The S3 object key to check
    - **bucket**: Optional bucket name (defaults to configured bucket)
    """
    try:
        target_bucket = bucket or s3_service.bucket_name

        response = s3_service.s3_client.head_object(Bucket=target_bucket, Key=s3_key)
        return {
            "exists": True,
            "s3_key": s3_key,
            "size": response.get("ContentLength"),
            "last_modified": response.get("LastModified"),
            "content_type": response.get("ContentType"),
        }

    except s3_service.s3_client.exceptions.NoSuchKey:
        return {
            "exists": False,
            "s3_key": s3_key,
        }
    except Exception as e:
        logger.error(f"Error checking file existence: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )


@router.get(
    "/list",
    responses={200: {"description": "List of files in S3"}, 500: {"model": ErrorResponse}},
)
async def list_objects(
    prefix: str = Query("", description="S3 key prefix to filter results"),
    max_keys: int = Query(100, ge=1, le=1000, description="Maximum number of objects to return"),
    bucket: Optional[str] = Query(None, description="S3 bucket name (optional)"),
):
    """
    List objects in S3 bucket with optional prefix filtering.

    - **prefix**: S3 key prefix to filter results (e.g., 'documents/')
    - **max_keys**: Maximum number of objects to return (1-1000)
    - **bucket**: Optional bucket name (defaults to configured bucket)
    """
    try:
        target_bucket = bucket or s3_service.bucket_name

        response = s3_service.s3_client.list_objects_v2(
            Bucket=target_bucket,
            Prefix=prefix,
            MaxKeys=max_keys,
        )

        objects = []
        if "Contents" in response:
            for obj in response["Contents"]:
                objects.append(
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                        "storage_class": obj["StorageClass"],
                    }
                )

        return {
            "bucket": target_bucket,
            "prefix": prefix,
            "objects": objects,
            "count": len(objects),
            "is_truncated": response.get("IsTruncated", False),
        }

    except Exception as e:
        logger.error(f"Error listing objects: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )
