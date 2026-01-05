# Document parser

## Cấu trúc thư mục
```bash
.
├── adp
│   ├── api
│   │   └── routers
│   ├── configs
│   │   ├── logger.py           # cấu hình logging
│   │   ├── models              # các mô hình cấu hình
│   │   │   └── observer.py
│   │   └── settings.py         # cấu hình ứng dụng loại singleton
│   ├── main.py
│   ├── services
│   │   ├── message_queue       # dịch vụ hàng đợi tin nhắn
│   │   ├── observer            # dịch vụ trả về
│   │   ├── parser              # dịch vụ trích xuất tài liệu
│   │   └── storage             # dịch vụ lưu trữ
│   └── workers
│       └── processor.py        # xử lý chính
├── docker-compose.yml
├── Dockerfile
├── docs                        # tài liệu dự án  
├── pyproject.toml
├── README.md
├── requirements.txt
└── tests                       # thư mục kiểm thử
```
