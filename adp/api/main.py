"""
FastAPI API Service với Prometheus Monitoring

File này là entry point của API service.
Đã tích hợp:
- Prometheus metrics middleware
- /metrics endpoint để Prometheus scrape
- Tracking cho mỗi HTTP request
"""

import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

# Import metrics từ monitoring module
from adp.monitoring import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
)

app = FastAPI(
    title="API Auto Document Parser",
    description="API for Auto Document Parser project",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# PROMETHEUS MIDDLEWARE - Track metrics cho mỗi HTTP request
# ==============================================================================

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    """
    Middleware này sẽ chạy cho MỖI HTTP request.
    
    Nó sẽ:
    1. Tăng counter requests_in_progress (đang xử lý)
    2. Đo thời gian xử lý request
    3. Ghi nhận metrics vào Prometheus
    4. Giảm counter requests_in_progress
    """
    # Lấy thông tin request
    method = request.method
    endpoint = request.url.path
    
    # Tăng counter: đang xử lý request này
    http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
    
    # Bắt đầu đếm thời gian
    start_time = time.time()
    
    try:
        # Xử lý request (gọi endpoint handler)
        response = await call_next(request)
        status_code = response.status_code
        
    except Exception as e:
        # Nếu có lỗi, ghi nhận status 500
        status_code = 500
        raise e
        
    finally:
        # Tính thời gian xử lý
        duration = time.time() - start_time
        
        # Ghi nhận metrics
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        # Giảm counter: xử lý xong request
        http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
    
    return response


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@app.get("/")
async def root():
    """Root endpoint - Welcome message"""
    return {"message": "Welcome to the Auto Document Parser API!"}


@app.get("/health")
async def health_check():
    """Health check endpoint - Kiểm tra API có hoạt động không"""
    return {"status": "healthy"}


# ==============================================================================
# PROMETHEUS METRICS ENDPOINT
# ==============================================================================

# Mount Prometheus metrics endpoint tại /metrics
# Prometheus sẽ scrape endpoint này để lấy metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

"""
Cách hoạt động:
1. User gửi request đến API (ví dụ: GET /health)
2. Middleware prometheus_middleware chạy TRƯỚC khi xử lý request
3. Middleware track metrics (duration, status code, etc.)
4. Request được xử lý bởi endpoint handler (health_check)
5. Response trả về cho user
6. Prometheus định kỳ gọi GET /metrics để lấy tất cả metrics
7. Grafana query Prometheus để vẽ dashboard

Ví dụ metrics output tại /metrics:
    http_requests_total{method="GET",endpoint="/health",status_code="200"} 150
    http_request_duration_seconds_sum{method="GET",endpoint="/health"} 7.5
    http_request_duration_seconds_count{method="GET",endpoint="/health"} 150
"""
