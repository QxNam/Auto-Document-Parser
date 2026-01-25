"""
Prometheus Metrics Definitions for Auto-Document-Parser

File này định nghĩa TẤT CẢ metrics cho hệ thống monitoring.
Mỗi service sẽ import metrics từ đây để track performance.

Các loại metrics:
- Counter: Đếm số lần xảy ra (chỉ tăng, không giảm)
- Histogram: Đo phân bố giá trị (duration, size)
- Gauge: Giá trị có thể tăng/giảm (active connections, queue size)
"""

from prometheus_client import Counter, Histogram, Gauge

# ==============================================================================
# 1️⃣ FASTAPI API METRICS
# ==============================================================================

# Tổng số HTTP requests
# Labels: method (GET/POST), endpoint (/upload, /health), status_code (200, 500)
http_requests_total = Counter(
    name="http_requests_total",
    documentation="Total number of HTTP requests",
    labelnames=["method", "endpoint", "status_code"]
)

# Thời gian xử lý HTTP request (histogram để tính p50, p95, p99)
# Labels: method, endpoint
http_request_duration_seconds = Histogram(
    name="http_request_duration_seconds",
    documentation="HTTP request duration in seconds",
    labelnames=["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]  # Buckets cho latency
)

# Số requests đang xử lý (real-time)
# Labels: method, endpoint
http_requests_in_progress = Gauge(
    name="http_requests_in_progress",
    documentation="Number of HTTP requests currently being processed",
    labelnames=["method", "endpoint"]
)

# Tổng số documents được upload
# Labels: file_type (pdf, docx, txt), status (success, failed)
document_uploads_total = Counter(
    name="document_uploads_total",
    documentation="Total number of document uploads",
    labelnames=["file_type", "status"]
)

# Kích thước file upload (bytes)
# Labels: file_type
document_upload_size_bytes = Histogram(
    name="document_upload_size_bytes",
    documentation="Size of uploaded documents in bytes",
    labelnames=["file_type"],
    buckets=[1024, 10240, 102400, 1048576, 10485760, 52428800]  # 1KB -> 50MB
)

# ==============================================================================
# 2️⃣ KAFKA MESSAGE QUEUE METRICS
# ==============================================================================

# Tổng số messages được produce vào Kafka
# Labels: topic (document-processing)
kafka_messages_produced_total = Counter(
    name="kafka_messages_produced_total",
    documentation="Total number of messages produced to Kafka",
    labelnames=["topic"]
)

# Tổng số messages được consume từ Kafka
# Labels: topic, consumer_group
kafka_messages_consumed_total = Counter(
    name="kafka_messages_consumed_total",
    documentation="Total number of messages consumed from Kafka",
    labelnames=["topic", "consumer_group"]
)

# Kafka lag - số messages chưa được xử lý
# Labels: topic, partition, consumer_group
kafka_message_lag = Gauge(
    name="kafka_message_lag",
    documentation="Number of messages not yet consumed (lag)",
    labelnames=["topic", "partition", "consumer_group"]
)

# Thời gian produce message vào Kafka
# Labels: topic
kafka_produce_duration_seconds = Histogram(
    name="kafka_produce_duration_seconds",
    documentation="Time taken to produce message to Kafka",
    labelnames=["topic"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

# Offset hiện tại của consumer
# Labels: topic, partition, consumer_group
kafka_consumer_offset = Gauge(
    name="kafka_consumer_offset",
    documentation="Current offset of Kafka consumer",
    labelnames=["topic", "partition", "consumer_group"]
)

# Số lỗi khi produce message
# Labels: topic, error_type
kafka_produce_errors_total = Counter(
    name="kafka_produce_errors_total",
    documentation="Total number of Kafka produce errors",
    labelnames=["topic", "error_type"]
)

# ==============================================================================
# 3️⃣ CELERY WORKER METRICS
# ==============================================================================

# Số tasks đang được xử lý (active)
# Labels: worker_id (worker-1, worker-2)
worker_tasks_active = Gauge(
    name="worker_tasks_active",
    documentation="Number of tasks currently being processed",
    labelnames=["worker_id"]
)

# Số tasks trong queue chờ xử lý
# Labels: queue_name (default, high-priority)
worker_tasks_queue_size = Gauge(
    name="worker_tasks_queue_size",
    documentation="Number of tasks waiting in queue",
    labelnames=["queue_name"]
)

# Thời gian xử lý task
# Labels: task_name (process_document, parse_pdf)
worker_task_duration_seconds = Histogram(
    name="worker_task_duration_seconds",
    documentation="Time taken to process a task",
    labelnames=["task_name"],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]  # 1s -> 5 phút
)

# Tổng số tasks đã xử lý
# Labels: task_name, status (success, failed, retry)
worker_tasks_total = Counter(
    name="worker_tasks_total",
    documentation="Total number of tasks processed",
    labelnames=["task_name", "status"]
)

# Worker health status (1 = healthy, 0 = dead)
# Labels: worker_id
worker_health = Gauge(
    name="worker_health",
    documentation="Worker health status (1=healthy, 0=dead)",
    labelnames=["worker_id"]
)

# ==============================================================================
# 4️⃣ PARSER SERVICE METRICS
# ==============================================================================

# Thời gian parse document
# Labels: file_type (pdf, docx, txt), parser_type (PyPDFParser, DocxParser)
document_parsing_duration_seconds = Histogram(
    name="document_parsing_duration_seconds",
    documentation="Time taken to parse a document",
    labelnames=["file_type", "parser_type"],
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0]
)

# Tổng số documents đã parse
# Labels: file_type, status (success, failed)
document_parsing_total = Counter(
    name="document_parsing_total",
    documentation="Total number of documents parsed",
    labelnames=["file_type", "status"]
)

# Số lỗi khi parse
# Labels: file_type, error_type (FileNotFound, ParseError, UnsupportedFormat)
document_parsing_errors_total = Counter(
    name="document_parsing_errors_total",
    documentation="Total number of parsing errors",
    labelnames=["file_type", "error_type"]
)

# Kích thước file được parse
# Labels: file_type
document_parsing_size_bytes = Histogram(
    name="document_parsing_size_bytes",
    documentation="Size of documents being parsed",
    labelnames=["file_type"],
    buckets=[1024, 10240, 102400, 1048576, 10485760, 52428800]
)

# ==============================================================================
# 5️⃣ S3 STORAGE METRICS
# ==============================================================================

# Thời gian S3 operations (upload/download)
# Labels: bucket, operation (upload, download, delete)
s3_operation_duration_seconds = Histogram(
    name="s3_operation_duration_seconds",
    documentation="Time taken for S3 operations",
    labelnames=["bucket", "operation"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# Tổng số S3 operations
# Labels: bucket, operation, status (success, failed)
s3_operations_total = Counter(
    name="s3_operations_total",
    documentation="Total number of S3 operations",
    labelnames=["bucket", "operation", "status"]
)

# Kích thước file upload lên S3
# Labels: bucket
s3_upload_size_bytes = Histogram(
    name="s3_upload_size_bytes",
    documentation="Size of files uploaded to S3",
    labelnames=["bucket"],
    buckets=[1024, 10240, 102400, 1048576, 10485760, 52428800]
)

# Số lỗi S3
# Labels: bucket, operation, error_type (AccessDenied, NoSuchBucket, NetworkError)
s3_errors_total = Counter(
    name="s3_errors_total",
    documentation="Total number of S3 errors",
    labelnames=["bucket", "operation", "error_type"]
)

# ==============================================================================
# 6️⃣ POSTGRESQL DATABASE METRICS
# ==============================================================================

# Thời gian thực thi query
# Labels: operation (SELECT, INSERT, UPDATE, DELETE), table (documents, users)
db_query_duration_seconds = Histogram(
    name="db_query_duration_seconds",
    documentation="Database query execution time",
    labelnames=["operation", "table"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

# Tổng số queries
# Labels: operation, table, status (success, failed)
db_queries_total = Counter(
    name="db_queries_total",
    documentation="Total number of database queries",
    labelnames=["operation", "table", "status"]
)

# Số connections đang active
db_connections_active = Gauge(
    name="db_connections_active",
    documentation="Number of active database connections"
)

# Tổng số connections
# Labels: status (success, failed)
db_connections_total = Counter(
    name="db_connections_total",
    documentation="Total number of database connections",
    labelnames=["status"]
)

# Tổng số transactions
# Labels: status (commit, rollback)
db_transactions_total = Counter(
    name="db_transactions_total",
    documentation="Total number of database transactions",
    labelnames=["status"]
)

# Số lỗi database
# Labels: error_type (DeadlockDetected, ConnectionTimeout, IntegrityError)
db_errors_total = Counter(
    name="db_errors_total",
    documentation="Total number of database errors",
    labelnames=["error_type"]
)

# ==============================================================================
# 7️⃣ OBSERVER SERVICE METRICS
# ==============================================================================

# Tổng số notifications gửi đi
# Labels: target_type (webhook, api, email), status (success, failed)
observer_notifications_total = Counter(
    name="observer_notifications_total",
    documentation="Total number of notifications sent",
    labelnames=["target_type", "status"]
)

# Thời gian gửi notification
# Labels: target_type
observer_notification_duration_seconds = Histogram(
    name="observer_notification_duration_seconds",
    documentation="Time taken to send notification",
    labelnames=["target_type"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Số lỗi khi gửi notification
# Labels: target_type, error_type (TimeoutError, ConnectionError, HTTPError)
observer_errors_total = Counter(
    name="observer_errors_total",
    documentation="Total number of observer errors",
    labelnames=["target_type", "error_type"]
)

# Số observer targets đang hoạt động
# Labels: source (config_file, database)
observer_targets_active = Gauge(
    name="observer_targets_active",
    documentation="Number of active observer targets",
    labelnames=["source"]
)
