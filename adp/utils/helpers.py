import hashlib


def get_file_hash(file_bytes: bytes) -> str:
    """
    Calculate the SHA256 hash of the given file bytes.
    """
    sha256 = hashlib.sha256()
    sha256.update(file_bytes)
    return sha256.hexdigest()
