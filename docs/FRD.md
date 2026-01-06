# TÀI LIỆU YÊU CẦU CHỨC NĂNG (Functional Requirements Document - FRD)
## FUNCTIONAL REQUIREMENTS DOCUMENT (FRD)
## 1. Thông tin tài liệu 
| Field | Description|
|------|------------|
| Project Name | Auto Document Parser |
| Document Type | Functional Requirements DOcument |
| Version | 1.0 |
| Author | Thảo |
| Date | 2026-01-06 |
| Status | Draft |
## 2. Mục đích
Tài liệu FRD này mô tả các yêu cầu chức năng chi tiết của hệ thống Auto Document Parser trong ngữ cảnh nghiệp vụ ngân hàng, nhằm chuyển hóa các yêu cầu nghiệp vụ trong BRD thành các chức năng hệ thống có thể triển khai kỹ thuật.
## 3. Phạm vi
### 3.1 Phạm vi bao gồm

- Tiếp nhận hồ sơ ngân hàng dạng số
- Tiền xử lý tài liệu
- OCR trích xuất văn bản
- Phân loại tài liệu
- Trích xuất dữ liệu theo schema ngân hàng
- Kiểm tra và xác thực dữ liệu
- Xuất dữ liệu có cấu trúc

### 3.2 Phạm vi không bao gồm

- Quyết định nghiệp vụ (approval, scoring)
- Xử lý ngoại lệ thủ công
- Tích hợp Core Banking (giai đoạn hiện tại)

## 4. Các bên liên quan 

| Role              | Responsibility              |
| ----------------- | --------------------------- |
| Business Analyst  | Xác định yêu cầu nghiệp vụ  |
| System Analyst    | Thiết kế chức năng hệ thống |
| Backend Developer | Triển khai pipeline         |
| QA Engineer       | Kiểm thử chức năng          |
| End User          | Upload và sử dụng kết quả   |

## 5. Giả thuyết và ràng buộc

### Giả thuyết

- Tài liệu đầu vào tuân theo mẫu ngân hàng ban hành
- Người dùng đã được phân quyền hợp lệ

### Ràng buộc 

- Kích thước file tối đa: 20MB
- Định dạng hỗ trợ: PDF, JPG, PNG
- Ngôn ngữ: Tiếng Việt, Tiếng Anh
- Pipeline xử lý bất đồng bộ

## 6. Tổng quan chức năng (Pipeline)

Hệ thống xử lý tài liệu theo pipeline sau:

1. Tải tài liệu lên
2. Tiền xử lý
3. Nhận dang ký tự quang học 
4. Phân loại tài liệu
5. Trích xuất dữ liệu  
6. Kiểm tra và xác thực dữ liệu
7. Xuất dữ liệu

## 7. Yêu cầu chức năng 

### FR-01: Tải tài liệu lên

**Description:**
Hệ thống cho phép người dùng upload hồ sơ ngân hàng để xử lý tự động.

**Input:**

- File PDF / JPG / PNG

**Process:**

- Kiểm tra định dạng file
- Kiểm tra kích thước file
- Lưu file vào storage

**Output:**

- Document ID
- Upload status

### FR-02: Tiền xử lý tài liệu

**Description:**
Hệ thống thực hiện tiền xử lý nhằm cải thiện chất lượng tài liệu trước OCR.

**Input:**

- Document ID

**Process:**

- Chuẩn hóa orientation
- Loại bỏ nhiễu
- Tăng độ tương phản

**Output:**

- Pre-processed document

### FR-03: Nhận dạng ký tự quang học (OCR)

**Description:**
Hệ thống thực hiện OCR để trích xuất nội dung văn bản từ tài liệu.

**Input:**

- Pre-processed document

**Process:**

- Thực thi OCR engine
- Trích xuất raw text

**Output:**
- OCR text result

### FR-04: Phân loại tài liệu 

**Description:**
Hệ thống phân loại tài liệu theo loại hồ sơ ngân hàng.

**Input:**

- OCR text

**Process:**
- Áp dụng rule / model phân loại
- Xác định document type (CMND, CCCD, Hợp đồng, Đơn vay, …)

**Output:**

- Document type

### FR-05: Trích xuất dữ liệu

**Description:**
Hệ thống trích xuất dữ liệu từ tài liệu theo schema tương ứng.

**Input:**

- OCR text
- Document type

**Process:**

- Mapping field theo schema
- Trích xuất key-value

**Output:**

- Extracted data

### FR-06: Kiểm tra và xác thực dữ liệu

**Description:**
Hệ thống kiểm tra tính hợp lệ của dữ liệu theo rule ngân hàng.

**Input:**

- Extracted data

**Validation Rules (Examples):**

- CCCD phải đủ 12 số
- Ngày cấp < ngày hiện tại
- Tên khách hàng không rỗng

**Output:**

- Validation status
- Error details (nếu có)

### FR-07: Xuất dữ liệu 

**Description:**
Hệ thống xuất dữ liệu đã xử lý sang định dạng chuẩn để sử dụng tiếp.

**Input:**

- Validated data

**Output Formats:**

- JSON (bắt buộc)
- CSV (tùy chọn)

## 8. Xử lý lỗi

| Error Code | Description             |
| ---------- | ----------------------- |
| ERR_01     | Unsupported file format |
| ERR_02     | File size exceeded      |
| ERR_03     | OCR processing failed   |
| ERR_04     | Data validation failed  |

## 9. Yêu cầu chi phí chức năng (NFRs)

Các yêu cầu phi chức năng (performance, security, scalability) được mô tả chi tiết trong tài liệu SRS.

## 10. Ma trận truy vết yêu cầu

| BRD ID | FR ID |
| ------ | ----- |
| BRD-01 | FR-01 |
| BRD-02 | FR-03 |
| BRD-03 | FR-05 |
| BRD-04 | FR-06 |

## 11. Open Questions

- OCR engine cụ thể được sử dụng?
- Schema dữ liệu có thay đổi theo từng ngân hàng không?
- Có hỗ trợ multi-document trong một batch không?

## 12. Phụ lục (Appendix)

- Pipeline Diagram: `pipeline.drawio`
