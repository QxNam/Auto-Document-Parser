from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from adp.services.storage.s3 import S3Service
import os

# 1. Khởi tạo Router 
router = APIRouter(prefix="/thao/s3", tags=["Thao S3 Operations"])

# 2. Khởi tạo service S3 
s3_service = S3Service()

@router.post("/upload")
async def thao_upload_file(file: UploadFile = File(...), s3_key: str = Query(...)):

    temp_path = f"temp_{file.filename}"
    try:
        # Lưu file tạm xuống máy
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Gọi logic để đẩy lên S3
        success = s3_service.upload_file(temp_path, s3_key)
        
        if not success:
            raise HTTPException(status_code=400, detail="Upload không thành công!")
            
        return {"status": "success", "message": f"Đã upload {file.filename} thành công!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Dọn dẹp file tạm 
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.delete("/delete")
async def thao_delete_file(s3_key: str = Query(...)):
    
    #API Xóa file trên S3
    success = s3_service.delete_file(s3_key)
    if not success:
        raise HTTPException(status_code=400, detail="Không xóa được file, kiểm tra lại key!")
    return {"status": "success", "message": f"Đã xóa file {s3_key} khỏi hệ thống."}