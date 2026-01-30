import io
from pathlib import Path

import botocore
import pytest

from adp.services.storage.s3 import S3Service

# Xác định đường dẫn file data.txt để test
DATA_FILE_PATH = Path(__file__).parent / "data.txt"


@pytest.fixture(autouse=True)
def reset_s3_service_singleton():
    """
    Vì S3Service là Singleton, ta cần reset instance trước mỗi test case
    để đảm bảo s3_client luôn sử dụng mock từ fixture mới nhất.
    """
    S3Service._instance = None
    yield
    S3Service._instance = None


def test_upload_file_success(s3_mock, setup_test_bucket):
    """Test upload file thành công và kiểm tra dictionary trả về."""
    service = S3Service()
    s3_key = "remote/data.txt"

    # Đảm bảo file test tồn tại
    if not DATA_FILE_PATH.exists():
        DATA_FILE_PATH.write_text("Dữ liệu test mẫu")

    # 1. Thực hiện upload
    with open(DATA_FILE_PATH, "rb") as f:
        result = service.upload_fileobj(f, setup_test_bucket, s3_key)

    # 2. Kiểm tra kết quả trả về (Hàm trả về dict {'status': bool, 'uri': str})
    assert result["status"] is True
    assert result["uri"] == f"s3://{setup_test_bucket}/{s3_key}"

    # 3. Kiểm tra dữ liệu trên S3 mock bằng client trực tiếp
    obj = s3_mock.get_object(Bucket=setup_test_bucket, Key=s3_key)
    s3_content = obj["Body"].read().decode("utf-8")
    assert s3_content == DATA_FILE_PATH.read_text()


def test_delete_file_success(s3_mock, setup_test_bucket):
    """Test chức năng xóa file (Hàm trả về None)."""
    service = S3Service()
    s3_key = "delete_me.txt"

    # Tạo sẵn file trên S3 mock
    s3_mock.put_object(Bucket=setup_test_bucket, Key=s3_key, Body="content")

    # Thực hiện xóa (hàm delete_object trả về None)
    result = service.delete_object(setup_test_bucket, s3_key)
    assert result is None

    # Kiểm tra file không còn tồn tại
    with pytest.raises(botocore.exceptions.ClientError) as excinfo:
        s3_mock.head_object(Bucket=setup_test_bucket, Key=s3_key)
    assert excinfo.value.response["Error"]["Code"] == "404"


def test_get_uri_logic():
    """Test logic tạo chuỗi URI."""
    service = S3Service()
    bucket = "my-bucket"
    key = "file.pdf"
    assert service.get_s3_uri(bucket, key) == f"s3://{bucket}/{key}"


def test_download_fileobj_success(s3_mock, setup_test_bucket):
    """Test tải file về dưới dạng BytesIO."""
    service = S3Service()
    s3_key = "download_test.txt"
    content = b"hello world"
    s3_mock.put_object(Bucket=setup_test_bucket, Key=s3_key, Body=content)

    result_buffer = service.download_fileobj(setup_test_bucket, s3_key)

    assert isinstance(result_buffer, io.BytesIO)
    assert result_buffer.getvalue() == content


def test_upload_file_not_found(setup_test_bucket):
    """Test lỗi FileNotFoundError khi mở file không tồn tại."""
    service = S3Service()

    # Kiểm tra lỗi ngay tại bước mở file trước khi gọi service
    with pytest.raises(FileNotFoundError):
        with open("non_existent_file.txt", "rb") as f:
            service.upload_fileobj(f, setup_test_bucket, "any.txt")


def test_list_objects_empty(s3_mock, setup_test_bucket):
    """Nâng cao Coverage: Test liệt kê danh sách file khi bucket trống."""
    service = S3Service()
    files = service.list_objects(setup_test_bucket, prefix="test/")
    assert files == []
