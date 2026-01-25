"""
Celery Worker với Prometheus Metrics

Worker này xử lý document processing tasks và track metrics về:
- Số tasks đang xử lý
- Thời gian xử lý task
- Số tasks thành công/thất bại
- Worker health status

HƯỚNG DẪN SỬ DỤNG:
Khi bạn implement Celery worker, hãy wrap task handler với metrics tracking như ví dụ dưới đây.
"""

import time
from adp.configs.logger import get_logger

# Import metrics
from adp.monitoring import (
    worker_tasks_active,
    worker_task_duration_seconds,
    worker_tasks_total,
    worker_health,
)

logger = get_logger(__name__)

# Giả sử bạn sẽ dùng Celery
# from celery import Celery
# celery_app = Celery('adp_worker')


def track_worker_metrics(worker_id="worker-1"):
    """
    Decorator để track metrics cho Celery tasks.
    
    Sử dụng:
        @celery_app.task
        @track_worker_metrics(worker_id="worker-1")
        def process_document(file_path):
            # Your processing logic here
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            task_name = func.__name__
            
            # 1. Tăng counter: đang xử lý task
            worker_tasks_active.labels(worker_id=worker_id).inc()
            
            # 2. Bắt đầu đếm thời gian
            start_time = time.time()
            
            try:
                # 3. Xử lý task
                result = func(*args, **kwargs)
                
                # 4. Tính thời gian xử lý
                duration = time.time() - start_time
                
                # ✅ TRACK METRICS - THÀNH CÔNG
                worker_task_duration_seconds.labels(
                    task_name=task_name
                ).observe(duration)
                
                worker_tasks_total.labels(
                    task_name=task_name,
                    status="success"
                ).inc()
                
                logger.info(f"Task {task_name} completed successfully in {duration:.2f}s")
                return result
                
            except Exception as e:
                # ❌ TRACK METRICS - THẤT BẠI
                worker_tasks_total.labels(
                    task_name=task_name,
                    status="failed"
                ).inc()
                
                logger.error(f"Task {task_name} failed: {str(e)}")
                raise e
                
            finally:
                # 5. Giảm counter: xử lý xong task
                worker_tasks_active.labels(worker_id=worker_id).dec()
        
        return wrapper
    return decorator


# ============================================================================
# VÍ DỤ SỬ DỤNG
# ============================================================================

# @celery_app.task
# @track_worker_metrics(worker_id="worker-1")
# def process_document(file_path):
#     """
#     Task xử lý document.
#     Metrics sẽ được track tự động nhờ decorator.
#     """
#     from adp.services.parser.parser import Parser
#     from adp.services.storage.s3 import S3Service
#     
#     # Parse document
#     parser = Parser()
#     result = parser.parse_document(file_path)
#     
#     # Upload to S3
#     s3 = S3Service()
#     s3.upload_file(file_path, f"parsed/{file_path}")
#     
#     return result


def set_worker_health(worker_id="worker-1", is_healthy=True):
    """
    Set worker health status.
    
    Gọi function này khi:
    - Worker start: set_worker_health(worker_id="worker-1", is_healthy=True)
    - Worker stop: set_worker_health(worker_id="worker-1", is_healthy=False)
    """
    health_value = 1 if is_healthy else 0
    worker_health.labels(worker_id=worker_id).set(health_value)
    logger.info(f"Worker {worker_id} health set to: {'healthy' if is_healthy else 'unhealthy'}")


# ============================================================================
# WORKER LIFECYCLE HOOKS (Celery signals)
# ============================================================================

# from celery.signals import worker_ready, worker_shutdown
#
# @worker_ready.connect
# def on_worker_ready(sender, **kwargs):
#     """Được gọi khi worker start"""
#     worker_id = sender.hostname
#     set_worker_health(worker_id=worker_id, is_healthy=True)
#     logger.info(f"Worker {worker_id} is ready")
#
# @worker_shutdown.connect
# def on_worker_shutdown(sender, **kwargs):
#     """Được gọi khi worker shutdown"""
#     worker_id = sender.hostname
#     set_worker_health(worker_id=worker_id, is_healthy=False)
#     logger.info(f"Worker {worker_id} is shutting down")
