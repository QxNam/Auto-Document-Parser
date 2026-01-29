# TÀI LIỆU YÊU CẦU NGHIỆP VỤ (BUSINESS REQUIREMENTS DOCUMENT - BRD)
## PROJECT NAME: Auto Document Parser
## Tóm tắt
Trong hoạt động ngân hàng, việc xử lý hồ sơ khách hàng (chứng minh thu nhập, giấy tờ pháp lý, tài sản đảm bảo) hiện đang chiếm 60% thời gian của nhân viên nghiệp vụ do dữ liệu nằm rải rác ở nhiều định dạng phi cấu trúc. Đây là hệ thống trích xuất và phân tích tài liệu tự động sử dụng kiến trúc Hybrid các open source. Dự án nhằm số hóa quy trình phê duyệt tín dụng, giảm thiểu sai sót con người và tạo tiền đề dữ liệu sạch cho hệ thống tra cứu thông tin nội bộ (RAG).

## Mục tiêu
- Tối ưu hóa năng suất: Giảm thời gian nhập liệu thủ công từ trung bình 30 phút/bộ hồ sơ xuống còn dưới 2 phút.
- Chuẩn hóa dữ liệu: 100% tài liệu đầu ra được chuyển đổi sang định dạng **Markdown** để sẵn sàng tích hợp vào kho tri thức tập trung (Internal RAG).
- Độ chính xác nghiêm ngặt: Đạt tỷ lệ chính xác trích xuất dữ liệu định danh (PII) và số liệu tài chính trên 98%.
- Tiết kiệm tài nguyên: Sử dụng CPU hiệu quả, giảm 40% chi phí lưu trữ và tính toán thông qua cơ chế nhận diện hồ sơ trùng lặp (Deduplication).

## Phạm vi dự án
- Hoạt động: Thiết kế cổng API tiếp nhận file, xây dựng luồng Kafka điều phối xử lý, triển khai Worker OCR/Parser, và lưu trữ Metadata.
- Sản phẩm bàn giao: Hệ thống Parser hoàn chỉnh, Dashboard tra cứu cho nhân viên, Tài liệu API, và Cơ sở dữ liệu Metadata.
- Trách nhiệm: 
    * Nhóm Kỹ thuật: Phát triển và vận hành hệ thống.
    * Nhóm Nghiệp vụ: Cung cấp mẫu tài liệu ngân hàng và kiểm thử (UAT).

## Yêu cầu nghiệp vụ chính
STT|Yêu cầu nghiệp vụ|Mô tả|Mức độ ưu tiên
---|------------------|------|----------------
1|Số hóa đa định dạng tài liệu|"Hệ thống phải có khả năng đọc và hiểu được tất cả các loại hồ sơ giấy, ảnh chụp, và file điện tử mà không cần sự can thiệp thủ công của nhân viên."|Tối cao (Critical)
2|Tối ưu hóa tài nguyên xử lý|Hệ thống phải nhận diện được các hồ sơ khách hàng đã tồn tại trong hệ thống để tránh lãng phí thời gian xử lý lại và đảm bảo tính thống nhất dữ liệu.|Cao (High)
3|Bảo mật và Tuân thủ dữ liệu|"Đảm bảo thông tin cá nhân của khách hàng được bảo vệ nghiêm ngặt, chỉ những người có thẩm quyền mới được phép truy cập theo đúng quy định của Ngân hàng Nhà nước."|Tối cao (Critical)
4|Tự động hóa trích xuất chỉ số tài chính|"Hệ thống tự động bóc tách các con số then chốt (thu nhập, nợ, số dư) để phục vụ việc tính toán hạn mức tín dụng mà không cần nhân viên phải đọc và nhập số liệu thủ công."|Cao (High)
5|Theo dõi trạng thái thời gian thực|"Nhân viên tín dụng phải biết được hồ sơ của mình đang ở giai đoạn nào (Đang xử lý, Chờ duyệt, hoặc Lỗi) để kịp thời phản hồi cho khách hàng."|Trung bình (Medium)
6|Chuẩn hóa dữ liệu cho tra cứu nội bộ|Dữ liệu sau khi trích xuất phải được định dạng theo tiêu chuẩn chung của ngân hàng để có thể dễ dàng tìm kiếm và sử dụng cho các ứng dụng phân tích sau này.|Cao (High)

## Stakeholders và Vai trò
Vai trò|Thành phần|Trách nhiệm chính
---|----------|-----------------
Sponsor|Ban Giám đốc Khối Công nghệ/Khối Tín dụng|Phê duyệt ngân sách và định hướng chiến lược.
Business Owner|Trưởng phòng Vận hành Tín dụng|Định nghĩa các trường thông tin cần trích xuất và quy tắc nghiệp vụ.
Project Team|"BA, DA, DE, DS, FE, BE, DevOps"|"Thiết kế, xây dựng và triển khai hệ thống BDI."
End Users|"Nhân viên Tín dụng, Nhân viên Kiểm soát"|Sử dụng hệ thống để xử lý hồ sơ hàng ngày và phản hồi chất lượng.
Compliance/Legal|Phòng Pháp chế & Tuân thủ|Đảm bảo việc trích xuất dữ liệu tuân thủ bảo mật thông tin ngân hàng.

## Các ràng buộc
- Thời gian: MVP phải hoàn thành trong 1 tháng để kịp tiến độ chuyển đổi số năm 2026.

- Bảo mật: Dữ liệu không được phép rời khỏi hạ tầng Cloud riêng (Private Cloud/VPC) của ngân hàng.

- Hệ thống cũ (Legacy): API phải tương thích với các định dạng dữ liệu đầu vào từ hệ thống Core Banking cũ đã vận hành 10 năm.

- Tài nguyên: Engine Docling đòi hỏi tài nguyên tính toán (GPU/CPU) lớn, cần tối ưu hóa chi phí hạ tầng AWS.

## Chi phí - Lợi ích
- Chi phí (Costs):
    * Hạ tầng AWS (S3): Dự kiến \$5,000 - \$8,000/tháng.
    * Nhân sự: Chi phí cho đội ngũ 7 roles trong 1 tháng phát triển.

- Lợi ích (Benefits):
    * Hữu hình: Giảm 50 nhân sự nhập liệu thủ công, tiết kiệm ~ $300,000/năm. Loại bỏ rủi ro bồi thường do sai sót dữ liệu.
    * Vô hình: Tăng tốc độ phục vụ khách hàng (Customer Experience), tạo kho dữ liệu Markdown chuẩn hóa giúp các mô hình AI/RAG của ngân hàng thông minh hơn, hỗ trợ ra quyết định tín dụng chính xác.
    