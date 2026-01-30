from fastapi import APIRouter, Depends, HTTPException, status

from adp.api.security.api_key import validate_api_key
from adp.services.storage.s3 import s3_service  # Giả định file S3Service nằm ở đây

router = APIRouter(
    prefix="/api/v1/s3",
    tags=["S3"],
    responses={
        status.HTTP_200_OK: {"description": "OK"},
        status.HTTP_204_NO_CONTENT: {"description": "Deleted"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
        status.HTTP_404_NOT_FOUND: {"description": "Object not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "S3 operation failed"},
    },
)


@router.delete("/object", status_code=status.HTTP_204_NO_CONTENT)
async def delete_object(bucket_name: str, object_key: str, _=Depends(validate_api_key)):
    """
    Delete a specific object from an S3 bucket.
    """
    try:
        s3_service.delete_object(bucket_name, object_key)
        return None
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete("/objects", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_objects(bucket_name: str, prefix: str = "", _=Depends(validate_api_key)):
    """
    Delete all objects in an S3 bucket with the given prefix.
    """
    try:
        s3_service.delete_all_objects(bucket_name, prefix)
        return None
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/list")
async def list_objects(bucket_name: str, prefix: str = "", _=Depends(validate_api_key)):
    """
    Fetch all object keys in an S3 bucket with the given prefix.
    """
    objects = s3_service.list_objects(bucket_name, prefix)
    return objects
