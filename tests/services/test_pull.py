import os

from adp.services.storage.s3 import s3_service

bucket_name, object_key = s3_service.parse_s3_uri("s3://pbl-bulk/upload/20260121_044729_abc.jpg")

file_obj = s3_service.download_fileobj(bucket_name=bucket_name, object_key=object_key)

# check size of file_obj
file_obj.seek(0, os.SEEK_END)
size = file_obj.tell()
file_obj.seek(0)

print(f"Downloaded file size: {size} bytes")

file_path = s3_service.download_file(bucket_name=bucket_name, key=object_key, output_path="/tmp/abc.jpg")
print(f"File downloaded to: {file_path}")
