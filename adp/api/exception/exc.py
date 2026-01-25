class FileValidationError(Exception):
    """Error not validating file type or size."""
    pass

class FileDuplicateError(Exception):
    """Error when a duplicate file is detected."""
    pass

class S3UploadError(Exception):
    """Error when unable to upload file to S3."""
    pass

class DatabaseError(Exception):
    """Error when interacting with the database."""
    pass

class MessageQueueError(Exception):
    """Error when unable to send message to Kafka."""
    pass