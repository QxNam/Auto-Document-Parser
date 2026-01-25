"""
Observer Manager với Prometheus Metrics

Service này quản lý observers và track metrics về:
- Số notifications gửi đi
- Thời gian gửi notification
- Lỗi khi gửi notification
- Số observer targets active
"""

import asyncio
import time

from adp.configs.logger import get_logger

# Import metrics
from adp.monitoring import (
    observer_notifications_total,
    observer_notification_duration_seconds,
    observer_errors_total,
    observer_targets_active,
)

logger = get_logger(__name__)


class ObserverManager:
    """
    Singleton manager responsible for initializing and coordinating all observers.

    Each data source can have multiple observer targets (e.g., webhooks, APIs, storage services).
    This manager handles observer creation from configuration and provides
    an asynchronous interface to push updates to all relevant observers.
    """

    _instance = None

    def __new__(cls):
        """Ensure a single instance of `ObserverManager` and initialize observers once."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_observers()
        return cls._instance

    def _init_observers(self):
        """
        Initialize all observers based on configuration.

        Creates all corresponding observer targets using the `create_observer()` factory.

        Each observer is logged individually upon successful initialization.
        """

        self.observers = {}
        # code here
        
        # ✅ TRACK METRICS - Số observer targets được khởi tạo
        total_targets = sum(len(targets) for targets in self.observers.values())
        observer_targets_active.labels(source="config_file").set(total_targets)
        
        logger.info(f"Initialized {total_targets} observer targets")

    async def send(self, source: str = "default", message: dict = None):
        """
        Push a message asynchronously to all observer targets of a specific source.
        
        Metrics tracked:
        - Số notifications gửi (counter)
        - Thời gian gửi (histogram)
        - Lỗi gửi (counter)
        """
        # load all target push from settings
        targets = self.observers.get(source, [])
        
        if not targets:
            logger.warning(f"No observer targets found for source: {source}")
            return

        # Bắt đầu đếm thời gian
        start_time = time.time()
        
        # gather all push tasks
        tasks = [self._send_to_target(t, message) for t in targets if t]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Tính thời gian tổng
        total_duration = time.time() - start_time
        
        # handle results and log errors
        success_count = 0
        error_count = 0
        
        for i, result in enumerate(results):
            target = targets[i] if i < len(targets) else None
            target_type = target.__class__.__name__ if target else "unknown"
            
            if isinstance(result, Exception):
                error_count += 1
                error_type = result.__class__.__name__
                
                # ❌ TRACK METRICS - LỖI
                observer_notifications_total.labels(
                    target_type=target_type,
                    status="failed"
                ).inc()
                
                observer_errors_total.labels(
                    target_type=target_type,
                    error_type=error_type
                ).inc()
                
                logger.error(f"[Observer] Observer update failed for {target_type}: {str(result)}")
            else:
                success_count += 1
                
                # ✅ TRACK METRICS - THÀNH CÔNG
                observer_notifications_total.labels(
                    target_type=target_type,
                    status="success"
                ).inc()
        
        # Ghi nhận thời gian gửi notification (trung bình cho tất cả targets)
        if targets:
            avg_duration = total_duration / len(targets)
            for target in targets:
                target_type = target.__class__.__name__ if target else "unknown"
                observer_notification_duration_seconds.labels(
                    target_type=target_type
                ).observe(avg_duration)
        
        logger.info(f"[Observer] Sent notifications: {success_count} success, {error_count} failed in {total_duration:.2f}s")
    
    async def _send_to_target(self, target, message):
        """
        Helper method để gửi message đến một target.
        Wrap target.push() để track metrics riêng cho từng target.
        """
        try:
            # Gọi push method của target
            result = await target.push(message)
            return result
        except Exception as e:
            # Re-raise để gather() có thể catch
            raise e

