"""Pydantic models for API request and response schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """Response model for file upload."""

    success: bool
    message: str
    s3_key: str
    s3_uri: str
    presigned_url: Optional[str] = None


class FileDeleteResponse(BaseModel):
    """Response model for file deletion."""

    success: bool
    message: str
    s3_key: str


class PresignedUrlResponse(BaseModel):
    """Response model for presigned URL generation."""

    s3_key: str
    presigned_url: str
    expires_in: int


class FileMetadata(BaseModel):
    """File metadata model."""

    s3_key: str
    s3_uri: str
    bucket: str
    size: Optional[int] = None


class ErrorResponse(BaseModel):
    """Error response model."""

    success: bool = False
    error: str
    detail: Optional[str] = None
