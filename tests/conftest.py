import os
import pytest
import boto3
from moto import mock_aws

@pytest.fixture(scope="session", autouse=True)
def aws_credentials():
    """Giả lập biến môi trường AWS trước khi các test chạy."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-1"

@pytest.fixture(scope="function")
def s3_mock():
    """
    Fixture này bật giả lập S3 cho từng hàm test.
    Sau khi test xong, mọi dữ liệu giả lập sẽ bị xóa sạch.
    """
    with mock_aws():
        yield boto3.client("s3", region_name="ap-southeast-1")

@pytest.fixture(scope="function")
def setup_test_bucket(s3_mock):
    """
    Tạo sẵn một bucket mẫu cho các bài test cần S3.
    """
    bucket_name = "test-storage-bucket"
    s3_mock.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-1'}
    )
    return bucket_name
