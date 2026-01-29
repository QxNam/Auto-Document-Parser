"""
Module quản lý Prometheus metrics cho Auto-Document-Parser

File này định nghĩa tất cả metrics được thu thập từ hệ thống ADP.
Metrics được chia thành 4 loại chính:
1. Counter: Đếm số lần event xảy ra (chỉ tăng, không giảm)
2. Histogram: Đo distribution của values (duration, size)
3. Gauge: Giá trị có thể tăng/giảm (current state)
4. Info: Metadata về service
"""
from prometheus_client import Counter, Histogram, Gauge, Info
import time

# =============================================================================
# COUNTER METRICS - Đếm số lần event xảy ra (chỉ tăng, không giảm)
# =============================================================================

# Đếm số file được upload thành công
# Labels:
#   - file_type: Loại file (pdf, docx, txt, jpg, png, etc.)
#   - status: Trạng thái (success, failed)
# Ví dụ query: rate(adp_file_upload_total[5m]) - tốc độ upload file/giây
file_upload_total = Counter(
    name='adp_file_upload_total',
    documentation='Total number of files uploaded',
    labelnames=['file_type', 'status']
)

# Đếm số task được xử lý bởi worker
# Labels:
#   - status: Trạng thái (completed, failed, processing)
# Ví dụ query: sum(adp_task_processed_total{status="completed"}) - tổng tasks thành công
task_processed_total = Counter(
    name='adp_task_processed_total',
    documentation='Total number of tasks processed by worker',
    labelnames=['status']
)

# Đếm số lần parse file
# Labels:
#   - parser_engine: Engine được dùng (text_layer, ocr, auto)
#   - file_type: Loại file
#   - status: Kết quả (success, failed)
# Ví dụ query: rate(adp_parse_operations_total{status="success"}[5m]) - success rate
parse_operations_total = Counter(
    name='adp_parse_operations_total',
    documentation='Total number of parse operations',
    labelnames=['parser_engine', 'file_type', 'status']
)


# =============================================================================
# HISTOGRAM METRICS - Đo distribution của values (duration, size, etc.)
# =============================================================================

# Đo thời gian xử lý file (parsing duration)
# Buckets: từ 0.1s đến 300s (5 phút)
# Labels:
#   - file_type: Loại file
#   - parser_engine: Engine được dùng
# Ví dụ query: 
#   - histogram_quantile(0.95, rate(adp_file_processing_duration_seconds_bucket[5m])) - p95 latency
#   - histogram_quantile(0.50, rate(adp_file_processing_duration_seconds_bucket[5m])) - p50 latency
file_processing_duration_seconds = Histogram(
    name='adp_file_processing_duration_seconds',
    documentation='Time spent processing files in seconds',
    labelnames=['file_type', 'parser_engine'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

# Đo kích thước file được upload (bytes)
# Buckets: từ 1KB đến 100MB
# Labels:
#   - file_type: Loại file
# Ví dụ query: histogram_quantile(0.95, rate(adp_file_size_bytes_bucket[5m])) - p95 file size
file_size_bytes = Histogram(
    name='adp_file_size_bytes',
    documentation='Size of uploaded files in bytes',
    labelnames=['file_type'],
    buckets=[1024, 10240, 102400, 1048576, 10485760, 104857600]  # 1KB, 10KB, 100KB, 1MB, 10MB, 100MB
)

# Đo số lượng pages trong document
# Buckets: từ 1 đến 200 pages
# Labels:
#   - file_type: Loại file
# Ví dụ query: avg(adp_document_pages_count_sum / adp_document_pages_count_count) - average pages
document_pages_count = Histogram(
    name='adp_document_pages_count',
    documentation='Number of pages in processed documents',
    labelnames=['file_type'],
    buckets=[1, 5, 10, 20, 50, 100, 200]
)


# =============================================================================
# GAUGE METRICS - Giá trị có thể tăng/giảm (current state)
# =============================================================================

# Số lượng workers đang active
# Ví dụ query: adp_active_workers - số workers đang chạy
active_workers = Gauge(
    name='adp_active_workers',
    documentation='Number of active worker processes'
)

# Số message trong Kafka queue (pending tasks)
# Labels:
#   - topic: Tên Kafka topic
# Ví dụ query: adp_kafka_queue_size{topic="upload"} - số tasks đang chờ xử lý
kafka_queue_size = Gauge(
    name='adp_kafka_queue_size',
    documentation='Number of messages in Kafka queue',
    labelnames=['topic']
)

# Số lượng documents theo status trong database
# Labels:
#   - status: Trạng thái (pending, processing, completed, failed)
# Ví dụ query: adp_documents_by_status{status="failed"} - số documents bị lỗi
documents_by_status = Gauge(
    name='adp_documents_by_status',
    documentation='Number of documents by processing status',
    labelnames=['status']
)

# Redis cache hit rate (%)
# Ví dụ query: adp_redis_cache_hit_rate - tỷ lệ cache hit
redis_cache_hit_rate = Gauge(
    name='adp_redis_cache_hit_rate',
    documentation='Redis cache hit rate percentage'
)


# =============================================================================
# INFO METRICS - Metadata về service
# =============================================================================

# Thông tin về service version và config
# Ví dụ query: adp_service_info - xem version và environment
service_info = Info(
    name='adp_service',
    documentation='Information about the ADP service'
)

# Set initial service info
# Có thể update bằng: service_info.info({'version': '0.0.2', 'environment': 'prod'})
service_info.info({
    'version': '0.0.1',
    'environment': 'dev'
})


# =============================================================================
# HELPER FUNCTIONS - Wrapper functions để dễ sử dụng
# =============================================================================

class MetricsHelper:
    """
    Helper class để track metrics một cách dễ dàng
    
    Class này cung cấp các wrapper methods để:
    - Tránh typo trong label names
    - Validate input parameters
    - Đơn giản hóa việc gọi metrics trong code
    
    Sử dụng:
        from adp.services.monitoring.metrics import metrics
        
        # Track file upload
        metrics.track_file_upload(file_type='pdf', status='success')
        
        # Track processing duration
        metrics.track_processing_duration(
            file_type='pdf',
            parser_engine='text_layer',
            duration_seconds=2.5
        )
    """
    
    @staticmethod
    def track_file_upload(file_type: str, status: str = 'success'):
        """
        Track file upload event
        
        Args:
            file_type (str): Loại file (pdf, docx, txt, jpg, png, etc.)
            status (str): Trạng thái upload (success, failed)
        
        Example:
            metrics.track_file_upload(file_type='pdf', status='success')
            metrics.track_file_upload(file_type='docx', status='failed')
        """
        # Increment counter với labels tương ứng
        # Counter chỉ có thể tăng, không thể giảm
        file_upload_total.labels(file_type=file_type, status=status).inc()
    
    @staticmethod
    def track_file_size(file_type: str, size_bytes: int):
        """
        Track file size distribution
        
        Args:
            file_type (str): Loại file
            size_bytes (int): Kích thước file (bytes)
        
        Example:
            metrics.track_file_size(file_type='pdf', size_bytes=1048576)  # 1MB
        """
        # Observe value vào histogram
        # Histogram tự động tính sum, count, và buckets
        file_size_bytes.labels(file_type=file_type).observe(size_bytes)
    
    @staticmethod
    def track_processing_duration(file_type: str, parser_engine: str, duration_seconds: float):
        """
        Track file processing duration
        
        Args:
            file_type (str): Loại file
            parser_engine (str): Engine được dùng (text_layer, ocr, auto)
            duration_seconds (float): Thời gian xử lý (seconds)
        
        Example:
            start_time = time.time()
            # ... process file ...
            duration = time.time() - start_time
            metrics.track_processing_duration(
                file_type='pdf',
                parser_engine='text_layer',
                duration_seconds=duration
            )
        """
        # Observe duration vào histogram
        # Dùng để tính p50, p95, p99 latency
        file_processing_duration_seconds.labels(
            file_type=file_type,
            parser_engine=parser_engine
        ).observe(duration_seconds)
    
    @staticmethod
    def track_document_pages(file_type: str, page_count: int):
        """
        Track số lượng pages trong document
        
        Args:
            file_type (str): Loại file
            page_count (int): Số pages
        
        Example:
            metrics.track_document_pages(file_type='pdf', page_count=25)
        """
        document_pages_count.labels(file_type=file_type).observe(page_count)
    
    @staticmethod
    def track_task_completion(status: str):
        """
        Track task completion
        
        Args:
            status (str): Trạng thái task (completed, failed)
        
        Example:
            try:
                # ... process task ...
                metrics.track_task_completion(status='completed')
            except Exception:
                metrics.track_task_completion(status='failed')
        """
        # Increment task counter
        task_processed_total.labels(status=status).inc()
    
    @staticmethod
    def track_parse_operation(parser_engine: str, file_type: str, status: str):
        """
        Track parse operation
        
        Args:
            parser_engine (str): Engine được dùng (text_layer, ocr, auto)
            file_type (str): Loại file
            status (str): Kết quả (success, failed)
        
        Example:
            try:
                result = parser.parse(file)
                metrics.track_parse_operation(
                    parser_engine='text_layer',
                    file_type='pdf',
                    status='success'
                )
            except Exception:
                metrics.track_parse_operation(
                    parser_engine='text_layer',
                    file_type='pdf',
                    status='failed'
                )
        """
        # Track parse operations với chi tiết labels
        parse_operations_total.labels(
            parser_engine=parser_engine,
            file_type=file_type,
            status=status
        ).inc()
    
    @staticmethod
    def update_queue_size(topic: str, size: int):
        """
        Update Kafka queue size
        
        Args:
            topic (str): Tên Kafka topic
            size (int): Số lượng messages trong queue
        
        Example:
            # Periodically update queue size
            queue_size = get_kafka_queue_size('upload')
            metrics.update_queue_size(topic='upload', size=queue_size)
        """
        # Set gauge value (có thể tăng hoặc giảm)
        # Gauge phản ánh current state, không phải cumulative
        kafka_queue_size.labels(topic=topic).set(size)
    
    @staticmethod
    def update_documents_count(status: str, count: int):
        """
        Update số lượng documents theo status
        
        Args:
            status (str): Trạng thái (pending, processing, completed, failed)
            count (int): Số lượng documents
        
        Example:
            # Periodically update document counts from database
            pending_count = db.query(Document).filter_by(status='pending').count()
            metrics.update_documents_count(status='pending', count=pending_count)
        """
        # Set gauge value cho document count
        documents_by_status.labels(status=status).set(count)
    
    @staticmethod
    def set_active_workers(count: int):
        """
        Set số lượng active workers
        
        Args:
            count (int): Số workers đang active
        
        Example:
            # When worker starts
            metrics.set_active_workers(1)
            
            # When worker stops
            metrics.set_active_workers(0)
        """
        # Set gauge cho worker count
        active_workers.set(count)
    
    @staticmethod
    def update_cache_hit_rate(hit_rate: float):
        """
        Update Redis cache hit rate
        
        Args:
            hit_rate (float): Cache hit rate (0-100%)
        
        Example:
            # Calculate hit rate: (hits / (hits + misses)) * 100
            hit_rate = (cache_hits / (cache_hits + cache_misses)) * 100
            metrics.update_cache_hit_rate(hit_rate)
        """
        # Set gauge cho cache hit rate
        redis_cache_hit_rate.set(hit_rate)

# Export helper instance để dùng trong code
# Sử dụng: from adp.services.monitoring.metrics import metrics
metrics = MetricsHelper()
