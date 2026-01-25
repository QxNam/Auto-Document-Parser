"""
Monitoring Module - Export tất cả metrics

File này export tất cả metrics để các service khác có thể import dễ dàng.

Cách sử dụng:
    from adp.monitoring import http_requests_total, kafka_messages_produced_total
    
    # Thay vì phải:
    from adp.monitoring.metrics import http_requests_total, kafka_messages_produced_total
"""

# API Metrics
from adp.monitoring.metrics import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
    document_uploads_total,
    document_upload_size_bytes,
)

# Kafka Metrics
from adp.monitoring.metrics import (
    kafka_messages_produced_total,
    kafka_messages_consumed_total,
    kafka_message_lag,
    kafka_produce_duration_seconds,
    kafka_consumer_offset,
    kafka_produce_errors_total,
)

# Worker Metrics
from adp.monitoring.metrics import (
    worker_tasks_active,
    worker_tasks_queue_size,
    worker_task_duration_seconds,
    worker_tasks_total,
    worker_health,
)

# Parser Metrics
from adp.monitoring.metrics import (
    document_parsing_duration_seconds,
    document_parsing_total,
    document_parsing_errors_total,
    document_parsing_size_bytes,
)

# S3 Storage Metrics
from adp.monitoring.metrics import (
    s3_operation_duration_seconds,
    s3_operations_total,
    s3_upload_size_bytes,
    s3_errors_total,
)

# PostgreSQL Database Metrics
from adp.monitoring.metrics import (
    db_query_duration_seconds,
    db_queries_total,
    db_connections_active,
    db_connections_total,
    db_transactions_total,
    db_errors_total,
)

# Observer Service Metrics
from adp.monitoring.metrics import (
    observer_notifications_total,
    observer_notification_duration_seconds,
    observer_errors_total,
    observer_targets_active,
)

# Export all metrics
__all__ = [
    # API
    "http_requests_total",
    "http_request_duration_seconds",
    "http_requests_in_progress",
    "document_uploads_total",
    "document_upload_size_bytes",
    # Kafka
    "kafka_messages_produced_total",
    "kafka_messages_consumed_total",
    "kafka_message_lag",
    "kafka_produce_duration_seconds",
    "kafka_consumer_offset",
    "kafka_produce_errors_total",
    # Worker
    "worker_tasks_active",
    "worker_tasks_queue_size",
    "worker_task_duration_seconds",
    "worker_tasks_total",
    "worker_health",
    # Parser
    "document_parsing_duration_seconds",
    "document_parsing_total",
    "document_parsing_errors_total",
    "document_parsing_size_bytes",
    # S3
    "s3_operation_duration_seconds",
    "s3_operations_total",
    "s3_upload_size_bytes",
    "s3_errors_total",
    # Database
    "db_query_duration_seconds",
    "db_queries_total",
    "db_connections_active",
    "db_connections_total",
    "db_transactions_total",
    "db_errors_total",
    # Observer
    "observer_notifications_total",
    "observer_notification_duration_seconds",
    "observer_errors_total",
    "observer_targets_active",
]
