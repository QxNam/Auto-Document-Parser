from adp.services.data_source.base_source import DataSourceBase
from adp.services.storage.s3 import s3_service


class S3DataSource(DataSourceBase):
    """
    DataSource service for handling S3-based data sources.
    """

    def __init__(self, name: str = "S3DataSource", config: dict = None):
        super().__init__(name, config)

    def pull(self, s3_uri: str) -> str:
        """Pull file from S3 and return file object."""

        bucket_name, object_key = s3_service.parse_s3_uri(uri=s3_uri)
        file_obj = s3_service.download_fileobj(bucket_name=bucket_name, object_key=object_key)
        return file_obj
