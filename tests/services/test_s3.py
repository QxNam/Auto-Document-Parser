from pathlib import Path

from adp.services.storage.s3 import S3Service

# Xác định đường dẫn file data.txt nằm cùng thư mục với file test này
DATA_FILE_PATH = Path(__file__).parent / "data.txt"


def test_upload_file_success(s3_mock, setup_test_bucket):
    """
    Test upload file thành công sử dụng fixture từ conftest.py
    s3_mock: fixture cung cấp client đã được mock
    setup_test_bucket: fixture cung cấp tên bucket đã được tạo sẵn
    """
    # Khởi tạo service
    service = S3Service()
    service.bucket_name = setup_test_bucket
    s3_key = "remote/data.txt"

    # Đảm bảo file data.txt tồn tại
    if not DATA_FILE_PATH.exists():
        DATA_FILE_PATH.write_text("Dữ liệu test mẫu")

    # 1. Thực hiện upload
    result = service.upload_file(str(DATA_FILE_PATH), s3_key)

    # 2. Kiểm tra kết quả trả về
    assert result is True

    # 3. Kiểm tra dữ liệu trên S3 mock
    obj = s3_mock.get_object(Bucket=setup_test_bucket, Key=s3_key)
    s3_content = obj["Body"].read().decode("utf-8")

    assert s3_content == DATA_FILE_PATH.read_text()


def test_delete_file_success(s3_mock, setup_test_bucket):
    """Test chức năng xóa file"""
    service = S3Service()
    service.bucket_name = setup_test_bucket
    s3_key = "delete_me.txt"

    # Tạo sẵn 1 file trên S3 mock để xóa
    s3_mock.put_object(Bucket=setup_test_bucket, Key=s3_key, Body="content")

    # Thực hiện xóa
    result = service.delete_file(s3_key)

    assert result is True

    # Kiểm tra file không còn tồn tại
    import botocore
    import pytest

    with pytest.raises(botocore.exceptions.ClientError):
        s3_mock.head_object(Bucket=setup_test_bucket, Key=s3_key)


def test_get_uri_logic(setup_test_bucket):
    """Test logic lấy URI không cần gọi tới mạng/mock s3 thực sự"""
    service = S3Service()
    service.bucket_name = setup_test_bucket
    s3_key = "path/to/file.zip"

    expected_uri = f"s3://{setup_test_bucket}/{s3_key}"
    assert service.get_uri(s3_key) == expected_uri


def test_upload_file_not_found(setup_test_bucket):  # Thêm fixture setup_test_bucket
    """Test xử lý lỗi khi file local không tồn tại"""
    service = S3Service()

    # Gán tên bucket từ fixture để vượt qua bước validate của Boto3
    service.bucket_name = setup_test_bucket

    # Thực hiện upload file không tồn tại
    result = service.upload_file("file_linh_tinh.txt", "remote.txt")

    # Kết quả mong đợi là False (do try-except trong S3Service bắt được lỗi FileNotFoundError)
    assert result is False
