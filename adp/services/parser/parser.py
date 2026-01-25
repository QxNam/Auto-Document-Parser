"""
Document Parser Service với Prometheus Metrics

Service này parse documents và track metrics về:
- Thời gian parse
- Số documents parse thành công/thất bại
- Loại file được parse
- Lỗi parsing
"""

import os
import time

from adp.configs.logger import get_logger
from adp.services.parser.parser_registry import ParserRegistry

# Import metrics
from adp.monitoring import (
    document_parsing_duration_seconds,
    document_parsing_total,
    document_parsing_errors_total,
    document_parsing_size_bytes,
)

logger = get_logger(__name__)


class Parser:
    """
    Document parsing service with Registry Pattern.
    """

    def parse_document(self, file_path):
        """
        Parse document và track metrics.
        
        Metrics tracked:
        - Thời gian parse (histogram)
        - Số documents parse (counter)
        - Kích thước file (histogram)
        - Lỗi parsing (counter)
        """
        # Lấy file extension để xác định file type
        _, extension = os.path.splitext(file_path)
        file_type = extension.lstrip('.').lower() or 'unknown'
        
        # Lấy file size nếu file tồn tại
        file_size = 0
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
        
        # Bắt đầu đếm thời gian parse
        start_time = time.time()
        parser_type = "unknown"
        
        try:
            # Lấy parser từ registry
            parser = ParserRegistry.get_parser(extension)
            parser_type = parser.__class__.__name__
            
            # Parse document
            result = parser.parse(file_path)
            
            # Tính thời gian parse
            duration = time.time() - start_time
            
            # ✅ TRACK METRICS - THÀNH CÔNG
            # 1. Ghi nhận thời gian parse
            document_parsing_duration_seconds.labels(
                file_type=file_type,
                parser_type=parser_type
            ).observe(duration)
            
            # 2. Tăng counter parse thành công
            document_parsing_total.labels(
                file_type=file_type,
                status="success"
            ).inc()
            
            # 3. Ghi nhận file size
            if file_size > 0:
                document_parsing_size_bytes.labels(
                    file_type=file_type
                ).observe(file_size)
            
            logger.info(f"Successfully parsed {file_path} in {duration:.2f}s")
            return result
            
        except FileNotFoundError as e:
            # ❌ TRACK METRICS - LỖI FILE NOT FOUND
            document_parsing_total.labels(
                file_type=file_type,
                status="failed"
            ).inc()
            
            document_parsing_errors_total.labels(
                file_type=file_type,
                error_type="FileNotFound"
            ).inc()
            
            logger.error(f"File not found: {file_path}")
            raise e
            
        except ValueError as e:
            # ❌ TRACK METRICS - LỖI UNSUPPORTED FORMAT
            document_parsing_total.labels(
                file_type=file_type,
                status="failed"
            ).inc()
            
            document_parsing_errors_total.labels(
                file_type=file_type,
                error_type="UnsupportedFormat"
            ).inc()
            
            logger.error(f"Unsupported file format: {file_path}")
            raise e
            
        except Exception as e:
            # ❌ TRACK METRICS - LỖI PARSE ERROR
            document_parsing_total.labels(
                file_type=file_type,
                status="failed"
            ).inc()
            
            document_parsing_errors_total.labels(
                file_type=file_type,
                error_type="ParseError"
            ).inc()
            
            logger.error(f"Failed to parse {file_path}: {str(e)}")
            raise e

