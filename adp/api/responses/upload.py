from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """
    Response model for file upload endpoint.
    """

    metadata_id: str = Field(..., description="Unique identifier for the uploaded file")
    s3_uri: str = Field(..., description="S3 URI where the file is stored")
    status: str = Field(..., description="Status of the file upload")
    time: int = Field(..., description="Timestamp of the upload in epoch format")
    file_size: int = Field(..., description="Size of the uploaded file in bytes")
    file_name: str = Field(..., description="Name of the uploaded file")

    class Config:
        json_schema_extra = {
            "example": {
                "metadata_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "s3_uri": "s3://my-bucket/uploads/a1b2c3d4-e5f6-7890-1234-567890abcdef.pdf",
                "status": "pending",
                "time": 1700000000,
                "file_size": 204800,
                "file_name": "document.pdf"
            }
        }