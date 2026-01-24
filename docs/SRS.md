# TÀI LIỆU YÊU CẦU PHẦN MỀM (System Requirements Specification - SRS)
## 1. Giới thiệu

### 1.1. Mục đích

Tài liệu này mô tả chi tiết các yêu cầu chức năng và phi chức năng cho hệ thống Auto document Parser. Hệ thống được xây dựng nhằm mục đích tự động hóa quy trình tiếp nhận, phân loại và trích xuất dữ liệu từ các tài liệu phi cấu trúc (PDF, Word, Excel, Image) thành dữ liệu có cấu trúc (Markdown// Text) để phục vụ cho các hệ thống  RAG 

### 1.2. Phạm vi
 
Hệ thống Auto Document Parser cung cấp nền tảng số hóa quy trình xử lý hồ sơ thông qua việc tự động trích xuất thông tin từ các file phi cấu trúc (.pdf,.pptx,.docsx,.png,.xlsx)

Hệ thống tập trung vào việc:
- Tiếp nhận đa định dạng: Xử lý hồ sơ giấy (ảnh chụp/scan) và file điện tử.
- Bóc tách thông tin: Sử dụng AI (ORC, Layout Analysis) để trích xuất văn bản và chỉ số tài chính
- Chuẩn hóa dữ liệu: Chuyển đổi dữ liệu đầu ra sang định dang Markdown/ JSON phục vụ cho RAG
- Quản lý quy trình: Theo dõi trạng thái xư lý hồ sơ ( Đang hoàn thành, Hoàn thành, Lỗi) và phát hiện hồ sơ trùng lặp

### 1.3. Tổng quát

Tài liệu này được viết dựa theo chuẩn của Tài liệu đặc tả yêu cầu phần mềm ( Software Requirements Specifications - SRS) được giải thích trong ""IEEE Recommended Practice for Software Requirements Specifications" và ""IEEE Guide for Developing System Requirements Specifications"

Với cấu trúc được chia thành ba phần: 

1. Cung cấp cái nhìn tông quan về các thành phần của SRS
2. Mô tả tổng quan các nhân tố, ràng buộc, đặc điểm người dùng, môi trường thực thi tác động lên hệ thống và các yêu cầu của nó. Cung cấp thông tin chi tiết các yêu cầu chức năng, cung cấp cho các nhà phát triển phần mềm thông tin để phát triển phần mềm đáp ứng được các yêu cầu đó
3. Các yêu cầu phi chức năng


## 2. Các yêu cầu chức năng:

### 2.1. Các tác nhân


- Người dùng (end user): Người dùng cuối, chịu trách nhiệm tải tài liệu lên hệ thống, theo dõi tiến dộ xử lý của các file tải lên, xem và kiểm tra kết quả bóc tách dữ liệu, thực hiện chỉnh sửa thủ công nếu AI nhận diện sai, xuất dữ liệu đã chuẩn hóa

- Quản trị viên hệ thống (admin): Người quản lý vận hành kỹ thuật, chịu trách nhiệm giám sát sức khỏe hệ thống qua Dashboard, theo dõi các chỉ số tài nguyên (CPU, RAM,...), Xử lý sự cố kỹ thuật và xem log lỗi

### 2.2. Các chức năng hệ thống
#### 2.2.1. Chức năng dành cho Người dùng
- Đăng nhập: cho phép người dùng đăng nhập bằng username và password
- Tải tài liệu (Upload Document): Cho phép người dùng tải lên một hoặc nhiều file cùng lúc, hỗ trợ kéo thả, hỗ trợ đa định dạng
- Theo dõi trạng thái (Track status): người dùng có thể xem được trạng thái danh sách các hồ sơ đã tải lên theo thời gian thực (Queued, Processing, Completed, Failed)
- Xem và đối chiếu (View & Verify): cho phép người dùng so sánh, đối chiếu giữa file gốc và kết quả bóc tách với giao diện chia đôi màn hìnd
- Chỉnh sửa kết quả: Cho phép người dùng chỉnh sửa trực tiếp nội dung văn bản nếu nhận diện sai
- Xuất dữ liệu: Cho phép tải xuống kết quả đã xử lý và chỉnh sửa
- Tìm kiếm hồ sơ (tùy chọn): Tìm kiếm lại các hồ sơ cũ đã xử lý dựa trên tên file, ngày tải lên hoặc trạng thái xử lý
#### 2.2.2. Chức năng dành cho Admin
- Quản lý người dùng: Tạo tài khoản cho người dùng, hiển thị danh sách người dùng. Hỗ trợ chức năng khóa hoặc xóa tài khoản 
- Giám sát dashboard: Truy cập dashboard tổng quan để xem các chỉ số sức khỏe hệ thống (số lượng file đang chờ trong hàng đợi, tốc độ xử lý trung bình, tỷ lệ lỗi của các Parser)
- Giám sát tài nguyên: Theo dõi mức độ tiêu thụ tài nguyên của các Worker Container (CPU Usage, RAM Usage, Dung lượng lưu trự tạm thời)
- Quản lý log lỗi: Xem chi tiết log lỗi của các file có trạng thái Failed
### 2.3. Biểu đồ use case tổng quan
<p align ="center">
    <img src="../docs/image/usecaseTQ.png" width="400" />
</p>

### 2.4. Biểu đồ use case phân rã
#### 2.4.1. Phân rã use case "Người dùng"
<p align ="center">
    <img src="../docs/image/usecaseND.drawio.png" width = "400" />
</p>

#### 2.4.2. Phân rã use case "Quản trị viên"
<p align = "center">
    <img src = "../docs/image/usecaseAD.png" width = "400" />
</p>

### 2.5. Quy trình nghiệp vụ
#### 2.5.1. Quy trình sử dụng phần mềm
Người dùng sử dụng tài khoản được cấp pháp trực tiếp bởi Quản trị viên để đăng nhập vào hệ thống. Trong quá trình sử dụng, nếu quên mẩ khẩu, người dùng có thể sử dụng chức năng "Quên mật khẩu" để yêu cầu hệ thống gửi liên kết thiết lập lại qua email. Sau khi đăng nhập thành công, người dùng có thể thực hiện các tác vụ quản lý tài khoản cá nhân và khai thác các chức năng nghiệp vụ theo đúng quyền hạn mà hệ thống đã phân cấp
<p align = "center">
    <img src = "../docs/image/QTVH-Page-2.drawio (1).png"  width = "400">
    <br>
    <em>Hình 4: Biểu đồ quy trình sử dụng phần mềm</em>
</p>


#### 2.5.2. Quy trình xử lý hồ sơ
Quy trình bắt đầu khi người dùng tải tài liệu (PDF, ảnh, Word...) lên hệ thống. Hệ thống sẽ tự động kiểm tra tính hợp lệ của file (định dạng, kích thước,...), nếu file không đạt yêu cầu hệ thống sẽ báo lỗi ngay lập tức. Nếu file hợp lệ, hệ thống sẽ đưa vào hàng đợi và thực hiện bóc tách dữ liệu ngầm. Trong quá trình này, người dùng theo dõi trạng thái hồ sơ trên bảng điều khiển. Khi trạng thái chuyển sang "Hoàn thành", người dùng truy cập chức năng xem chi tiết để đối chiếu kết quả trích xuất so với tài liệu gốc (giao diện chia đôi màn hình). Nếu phát hiện sai sót, người dùng thực hiện chỉnh sửa trực tiếp và lưu lại. Cuối cùng, người dùng xuất dữ liệu đã được chuẩn hóa ra file để kết thúc quy trình
<p align = "center">
    <img src = "../docs/image/QTSDPM.drawio (1).png" width = "400">
    <br>
    <em>Hình 4: Biểu đồ quy trình xử lý hồ sơ</em>
</p>

#### 2.5.3. Quy trình giám sát vận hành
Quản trị viên bắt đầu phiên làm việc bằng cách đăng nhập và truy cập Dashboard quản trị để giám sát sức khỏe hệ thống theo thời gian thực. Các chỉ số quan trọng cần theo dõi bao gồm trạng thái hàng đợi hồ sơ (Queue), mức tiêu thụ tài nguyên (CPU/RAM) và tỷ lệ lỗi xử lý. Trong trường hợp phát hiện các chỉ số bất thường hoặc cảnh báo quá tải, Quản trị viên sẽ tiến hành truy vết thông qua chức năng "Quản lý Log lỗi" để xác định nguyên nhân cụ thể từ các file bị từ chối. Dựa trên kết quả phân tích, Quản trị viên thực hiện các biện pháp can thiệp kỹ thuật hoặc báo cáo sự cố cho đội ngũ phát triển để xử lý triệt để trước khi đăng xuất khỏi hệ thống.

<p align = "center">
    <img src = "../docs/image/QTQTHT.drawio.png" width = "400">
    <br>
    <em>Hình 4: Biểu đồ quy trình giám sát hệ thống</em>
</p>


### 2.6. Đặc tả các use case
#### 2.6.1. UC-00: Đăng nhập hệ thống
**Tác nhân (Actor):** Tất cả người dùng (User, Admin)

| Mục | Nội dung |
| :--- | :--- |
| **Tên Use Case** | **Đăng nhập hệ thống (System Login)** |
| **Mô tả** | Cho phép người dùng xác thực danh tính để truy cập vào các chức năng của hệ thống dựa trên vai trò (User hoặc Admin). |
| **Tiền điều kiện** | 1. Người dùng đã có tài khoản được đăng ký/cấp phát hợp lệ.<br>2. Hệ thống đang hoạt động và kết nối mạng ổn định. |
| **Luồng sự kiện chính<br>(Main Flow)** | 1. Người dùng truy cập địa chỉ (URL) của hệ thống.<br>2. Hệ thống hiển thị màn hình Đăng nhập.<br>3. Người dùng nhập **Tên đăng nhập** (Email/Username) và **Mật khẩu**.<br>4. Người dùng nhấn nút "Đăng nhập".<br>5. Hệ thống mã hóa mật khẩu và đối chiếu với cơ sở dữ liệu.<br>6. Hệ thống xác thực thành công và kiểm tra vai trò (Role):<br>&nbsp;&nbsp;- *Nếu là User:* Chuyển hướng đến Dashboard cá nhân (Quản lý hồ sơ).<br>&nbsp;&nbsp;- *Nếu là Admin:* Chuyển hướng đến Dashboard quản trị (Giám sát hệ thống).<br>7. Hệ thống hiển thị thông báo "Đăng nhập thành công".<br>8. Use Case kết thúc. |
| **Luồng ngoại lệ<br>(Alternative Flow)** | <br>1a. Hệ thống không tìm thấy tài khoản hoặc mật khẩu không khớp.<br>2a. Hệ thống hiển thị thông báo lỗi: *"Tên đăng nhập hoặc mật khẩu không chính xác"*.<br>3. Hệ thống xóa trắng trường mật khẩu và giữ nguyên tên đăng nhập.<br>4. Quay lại bước 3 (Yêu cầu nhập lại).<br>5a. Hệ thống phát hiện tài khoản tồn tại nhưng trạng thái là "Vô hiệu hóa" (Inactive/Locked).<br>6a. Hệ thống thông báo: *"Tài khoản của bạn đã bị khóa. Vui lòng liên hệ Quản trị viên"*.<br> |
| **Hậu điều kiện** | Phiên làm việc (Session token) được khởi tạo. Người dùng có quyền truy cập vào các tài nguyên tương ứng với vai trò của mình. |

#### 2.6.2. UC-01: Tải lên và Xử lý tài liệu tự động
**Tác nhân (Actor):** Người dùng (User)

| Mục | Nội dung |
| :--- | :--- |
| **Tên Use Case** | **Tải lên và Xử lý tài liệu tự động** |
| **Mô tả** | Người dùng tải tài liệu lên hệ thống để thực hiện bóc tách dữ liệu ngầm. Hệ thống kiểm tra tính hợp lệ và đưa vào hàng đợi xử lý. |
| **Tiền điều kiện** | 1. Người dùng đã đăng nhập vào hệ thống.<br>2. Người dùng đang ở màn hình Dashboard hoặc màn hình tải tài liệu. |
| **Luồng sự kiện chính<br>(Main Flow)** | 1. Người dùng chọn chức năng "Tải tài liệu" và chọn file từ thiết bị (PDF, Ảnh, Word, Excel...).<br>2. Hệ thống kiểm tra tính hợp lệ của file (định dạng, kích thước, virus).<br>3. Hệ thống xác nhận file hợp lệ và thông báo "Tải lên thành công".<br>4. Hệ thống tự động đưa hồ sơ vào hàng đợi (Queue) và bắt đầu tiến trình bóc tách dữ liệu ngầm (Background Processing).<br>5. Hệ thống cập nhật trạng thái hồ sơ thành "Đang xử lý" trên Dashboard.<br>6. Người dùng theo dõi trạng thái trên Dashboard cho đến khi chuyển sang "Hoàn thành".<br>7. Use Case kết thúc. |
| **Luồng ngoại lệ<br>(Alternative Flow)** |2a. Hệ thống phát hiện file sai định dạng hoặc quá dung lượng cho phép.<br>3a. Hệ thống từ chối tiếp nhận file.<br>4a. Quay lại bước 1 (Người dùng chọn file khác). |
| **Hậu điều kiện** | Hồ sơ được lưu vào hệ thống, trạng thái chuyển sang "Hoàn thành" và dữ liệu thô đã được trích xuất sẵn sàng cho việc đối chiếu. |

---

#### 2.6.3. UC-02: Đối chiếu và Chuẩn hóa dữ liệu
**Tác nhân (Actor):** Người dùng (User)

| Mục | Nội dung |
| :--- | :--- |
| **Tên Use Case** | **Đối chiếu và Chuẩn hóa dữ liệu** |
| **Mô tả** | Người dùng xem lại kết quả trích xuất, so sánh với tài liệu gốc và chỉnh sửa các sai sót trước khi xuất dữ liệu cuối cùng. |
| **Tiền điều kiện** | 1. Hồ sơ đã có trạng thái "Hoàn thành" (kết quả của UC-01). |
| **Luồng sự kiện chính<br>(Main Flow)** | 1. Người dùng chọn hồ sơ có trạng thái "Hoàn thành" và nhấn "Xem chi tiết".<br>2. Hệ thống hiển thị giao diện chia đôi màn hình (Side-by-side): Bên trái là tài liệu gốc, bên phải là dữ liệu đã trích xuất.<br>3. Người dùng thực hiện đối chiếu dữ liệu giữa hai bên.<br>4. Người dùng xác nhận dữ liệu chính xác.<br>5. Người dùng nhấn nút "Xuất dữ liệu".<br>6. Hệ thống xuất file kết quả (Excel/JSON) đã được chuẩn hóa.<br>7. Use Case kết thúc. |
| **Luồng ngoại lệ<br>(Alternative Flow)** |<br>1a. Người dùng phát hiện trường thông tin bị trích xuất sai hoặc thiếu.<br>2a. Người dùng click trực tiếp vào ô dữ liệu trên giao diện và nhập lại giá trị đúng.<br>3a. Người dùng nhấn "Lưu thay đổi".<br>4a. Hệ thống cập nhật dữ liệu mới vào cơ sở dữ liệu.<br>5. Quay lại bước 4 của luồng chính. |
| **Hậu điều kiện** | Dữ liệu chính xác được xuất ra khỏi hệ thống. Quy trình xử lý hồ sơ hoàn tất. |

---

#### 2.6.4. UC-03: Giám sát và Xử lý sự cố hệ thống
**Tác nhân (Actor):** Quản trị viên (Admin)

| Mục | Nội dung |
| :--- | :--- |
| **Tên Use Case** | **Giám sát sức khỏe hệ thống và Xử lý sự cố** |
| **Mô tả** | Quản trị viên theo dõi các chỉ số tài nguyên và hàng đợi theo thời gian thực. Nếu có sự cố, Admin truy vết log để xử lý. |
| **Tiền điều kiện** | 1. Quản trị viên đã đăng nhập với quyền Admin.<br>2. Dashboard quản trị đang hoạt động. |
| **Luồng sự kiện chính<br>(Main Flow)** | 1. Quản trị viên truy cập Dashboard quản trị.<br>2. Hệ thống hiển thị biểu đồ thời gian thực các chỉ số: Hàng đợi (Queue), CPU/RAM, Tỷ lệ lỗi.<br>3. Quản trị viên giám sát và thấy các chỉ số ở mức ổn định (xanh).<br>4. Quản trị viên tiếp tục giám sát hoặc chọn đăng xuất để kết thúc phiên làm việc. |
| **Luồng ngoại lệ<br>(Alternative Flow)** | <br>1a. Hệ thống cảnh báo chỉ số bất thường (ví dụ: Queue bị tắc nghẽn, Tỷ lệ lỗi > 5%).<br>2a. Quản trị viên truy cập chức năng "Quản lý Log lỗi".<br>3a. Hệ thống hiển thị danh sách các file bị lỗi và mã lỗi tương ứng.<br>4a. Quản trị viên phân tích nguyên nhân từ log.<br>5a. Quản trị viên thực hiện hành động:<br>&nbsp;&nbsp;- *Nếu lỗi hạ tầng:* Can thiệp kỹ thuật (Restart service, tăng resource...).<br>&nbsp;&nbsp;- *Nếu lỗi code/logic:* Gửi báo cáo kèm log cho đội phát triển.<br>6. Hệ thống ghi nhận trạng thái sự cố đã được xử lý/báo cáo.<br>7a. Quay lại bước 3 (Tiếp tục giám sát). |
| **Hậu điều kiện** | Hệ thống duy trì trạng thái ổn định hoặc sự cố đã được khoanh vùng xử lý. |



## 3. Các yêu cầu phi chức năng

### 3.1. Hiệu năng (Performance)

- Thời gian xử lý: Hệ thống phải đảm bảo thời gian xử ls/ trang tài liệu
- Độ chính xác: Chất lượng text sau trích xuất đạt tối thiểu 80% (cho MVP) và hướng tới 98% ( cho bản hoàn chỉnh)
- Khả năng chịu tải: API có khả năng xử lý đồng thời nhiều request mà không bị treo

### 3.2. Giao diện người dùng

Hệ thống cần có giao diện trực quan, thân thiện với người dùng để đảm bảo trải nghiệm tốt nhất. Hỗ trợ hiển thị so sánh side-by-side (file gốc với kết quả trích xuất) để dễ dàng đối chiếu.Tốc độ phản hồi của hệ thống nhanh, đảm bảo hiện thị kết quả ngay lập tức khi người dùng thực hiện thao tác

### 3.3. Tính bảo mật

Người dùng chỉ có thể sử dụng các chức năng và truy cập các dữ liệu phù hợp với vai trò của người dùng đó

### 3.4. Ràng buộc

- Hệ thống dựa trên Web do vậy người dùng cần có các thiết bị có kết nối với intenet như máy vi tính và được cung cấp các dịch vụ như hình ảnh, văn bản, giao thức truyền thông siêu văn bản để có thể gửi và nhận thông tin, dữ liệu giữa máy khách và web server

- Bên phía máy khách - người dùng cần có phần mềm ứng dụng duyệt Web như Google Chrome, Internet Explore, Mozilla Firefox, Opera với phiên bản mới nhất
