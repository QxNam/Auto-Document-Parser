# Auto Document Parser

## Pipeline tổng quan
Hệ thống Auto Document Parser (ADP) được thiết kế để tự động trích xuất và xử lý tài liệu từ các nguồn khác nhau. Dưới đây là mô tả tổng quan về pipeline của hệ thống:
1. **Nhận tài liệu**: Hệ thống nhận tài liệu từ các nguồn như email, tải lên qua giao diện web, hoặc từ các dịch vụ lưu trữ đám mây.
2. **Xử lý hàng đợi tin nhắn**: Tài liệu được đưa vào hàng đợi tin nhắn để quản lý và xử lý tuần tự, điều này giúp cân bằng tải cho server xử lý.
3. **Trích xuất tài liệu**: Dịch vụ trích xuất tài liệu sử dụng các mô hình học máy và kỹ thuật xử lý ngôn ngữ tự nhiên để phân tích và trích xuất thông tin quan trọng từ tài liệu.
4. **Lưu trữ dữ liệu**: Thông tin trích xuất được lưu trữ trong cơ sở dữ liệu hoặc hệ thống lưu trữ đám mây để dễ dàng truy cập và quản lý.
5. **Quan sát và giám sát**: Hệ thống có các dịch vụ quan sát để theo dõi hiệu suất và trạng thái của quá trình xử lý tài liệu, đảm bảo rằng mọi thứ hoạt động trơn tru và hiệu quả.
6. **Xử lý chính**: Một worker xử lý chính sẽ điều phối các bước trên, đảm bảo rằng tài liệu được xử lý đúng cách và kịp thời.

![Pipeline Diagram](assets/pipeline.png)

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
