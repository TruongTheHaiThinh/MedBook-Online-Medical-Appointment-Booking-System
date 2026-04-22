# PROJECT PROPOSAL

## MEDBOOK – HỆ THỐNG QUẢN LÝ VÀ ĐẶT LỊCH KHÁM BỆNH TRỰC TUYẾN
**MedBook – Online Medical Management & Appointment Booking System**

| Vai trò / Thông tin | Chi tiết |
| :--- | :--- |
| Thành viên 1 | Trương Thế Hải Thịnh – 23725051 |
| Thành viên 2 | Nguyễn Thị Quỳnh Trang – 23676071 |
| Git Repository | [TruongTheHaiThinh/MedBook-Online-Medical-Appointment-Booking-System](https://github.com/TruongTheHaiThinh/MedBook-Online-Medical-Appointment-Booking-System) |

---

## CẤU TRÚC NHÁNH GIT

| Nhánh | Mục đích | Người phụ trách |
| :--- | :--- | :--- |
| `feature/auth` | Module 1 – Xác thực & Phân quyền (JWT, bcrypt, roles) | Thịnh |
| `feature/doctor-specialty` | Module 2 – Bác sĩ, Chuyên khoa & Lịch làm việc | Thịnh |
| `feature/appointment` | Module 3 – Luồng Đặt lịch & State Machine | Thịnh |
| `feature/admin-management` | Module 4 – Quản lý nhân sự & Kế toán thu ngân | Trang |
| `feature/medical-record` | Module 5 – Hồ sơ bệnh nhân & Sổ khám điện tử | Trang |
| `develop` | Tích hợp tất cả feature branch sau khi review | Cả nhóm |
| `main` | Push cuối cùng – bản hoàn chỉnh để nộp/deploy | Cả nhóm |

**Quy trình làm việc:**
* Mỗi thành viên làm việc trên nhánh feature/* riêng.
* Khi xong 1 module → tạo Pull Request vào develop.
* Thành viên còn lại review & approve PR.
* Sau khi toàn bộ tính năng ổn định trên develop → merge 1 lần duy nhất vào main.
* `main` chỉ nhận push cuối cùng – không commit trực tiếp lên main trong quá trình phát triển.

---

## MÔ TẢ DỰ ÁN

### 1. Ý TƯỞNG DỰ ÁN (THE VISION)

**Tổng quan nền tảng**
Trong bối cảnh hệ thống y tế Việt Nam đang chịu áp lực quá tải nghiêm trọng, nhóm chúng tôi quyết định xây dựng MedBook – một nền tảng Web full-stack chuyên biệt không chỉ giải quyết bài toán đặt lịch hẹn khám bệnh, mà còn tích hợp toàn bộ quy trình quản lý vận hành phòng khám. Đây là một Trung tâm quản lý y tế thông minh dành cho phòng khám tư nhân và trạm y tế địa phương.

**3 Trụ cột kỹ thuật của MedBook:**
* **Full-Stack Design:** Backend RESTful API (FastAPI + Python) kết hợp Frontend (HTML/CSS/JS thuần), tự động sinh tài liệu Swagger/OpenAPI.
* **Smart Scheduling Engine:** Thuật toán tự động tính slot khả dụng từ lịch làm việc của bác sĩ, xử lý đúng đắn khi bác sĩ đổi lịch đột xuất.
* **Integrated Clinical Workflow:** Toàn bộ quy trình từ đặt lịch → thu ngân xác nhận → bác sĩ khám → kê đơn thuốc → thu phí → phát thuốc được số hóa và liên thông.

### 2. VAI TRÒ NGƯỜI DÙNG & PHÂN QUYỀN

Hệ thống mở rộng lên 4 vai trò người dùng với phân quyền rõ ràng:

| Vai trò | Tên gọi | Mô tả |
| :--- | :--- | :--- |
| Bệnh nhân | Patient | Đặt lịch, xem sổ khám bệnh điện tử, nhận mã QR/mã vạch |
| Admin Nhân sự | HR Admin | Quản lý tài khoản bác sĩ, nhân viên, phê duyệt hồ sơ, thống kê hệ thống |
| Admin Thu ngân | Cashier Admin | Tiếp nhận đặt lịch, xác nhận thông tin, quản lý đơn thuốc & thu phí |
| Bác sĩ | Doctor | Nhận thông báo ca khám, xem hồ sơ bệnh nhân, kê đơn thuốc, gửi đơn cho thu ngân |

### 3. CHI TIẾT NGHIỆP VỤ (BUSINESS LOGIC)

**3.1 Quy trình khám bệnh tổng thể**
Quy trình hoạt động theo luồng tuần tự như sau:

| Bước | Tác nhân | Hành động |
| :--- | :--- | :--- |
| 1 | Bệnh nhân | Đăng ký tài khoản / đăng nhập → Chọn bác sĩ, chuyên khoa, ngày giờ → Đặt lịch hẹn |
| 2 | Admin Thu ngân | Nhận thông báo đặt lịch → Xem xét & xác nhận thông tin bệnh nhân → Cập nhật trạng thái CONFIRMED |
| 3 | Hệ thống | Tự động gửi Giấy hẹn khám cho bệnh nhân (ghi rõ lộ trình khám: phòng khám, bác sĩ, giờ, hướng dẫn chuẩn bị) |
| 4 | Hệ thống | Thông báo cho bác sĩ phụ trách về ca khám mới (khám mới / tái khám) |
| 5 | Bệnh nhân | Đến phòng khám → Trình mã QR / mã vạch để xác thực (sau khi thanh toán đặt lịch thành công) |
| 6 | Bác sĩ | Tiếp nhận bệnh nhân → Xem toàn bộ hồ sơ & lịch sử khám → Thực hiện khám bệnh |
| 7 | Bác sĩ | Kê đơn thuốc theo mẫu chuẩn → Chỉ định có/không tái khám (ghi trong đơn) → Gửi đơn thuốc cho thu ngân |
| 8 | Admin Thu ngân | Nhận đơn thuốc từ bác sĩ → Thu phí thuốc → Xác nhận thanh toán → Tiến hành phát thuốc |
| 9 | Bệnh nhân | Nhận thuốc → Lịch sử khám & đơn thuốc tự động cập nhật vào Sổ khám điện tử |

**3.2 Module theo từng vai trò**

**A. Bệnh nhân (Patient)**
* **Đặt lịch khám:** Tìm kiếm bác sĩ theo tên, chuyên khoa; chọn ngày giờ theo slot trống; nhập lý do khám (tùy chọn).
* **Nhận mã QR / mã vạch:** Sau khi thanh toán đặt lịch thành công, hệ thống tự động sinh mã QR / mã vạch định danh cho ca khám đó. Bệnh nhân xuất trình mã này khi đến phòng khám để xác thực nhanh.
* **Giấy hẹn khám:** Nhận giấy hẹn điện tử sau khi thu ngân xác nhận, có ghi đầy đủ: tên bác sĩ, phòng khám, giờ hẹn, lộ trình đến khám, các lưu ý chuẩn bị.
* **Sổ khám bệnh điện tử:** Xem toàn bộ lịch sử khám bệnh dưới dạng hồ sơ điện tử chuyên nghiệp (read-only): ngày khám, bác sĩ, chẩn đoán, đơn thuốc, ghi chú tái khám.

**B. Admin Nhân sự (HR Admin)**
* **Quản lý tài khoản:** Phê duyệt hoặc từ chối tài khoản bác sĩ sau khi xác minh thông tin. Khóa tài khoản vi phạm, reset mật khẩu khi cần.
* **Quản lý nhân sự:** CRUD bác sĩ, nhân viên thu ngân. Phân công bác sĩ theo chuyên khoa. Quản lý lịch làm việc tổng thể.
* **Quản lý chuyên khoa:** Tạo, sửa, xóa danh mục chuyên khoa (Tim mạch, Nội tổng quát, Da liễu...).
* **Thống kê hệ thống:** Dashboard tổng quan: tổng lịch hẹn theo ngày/tuần/tháng, tỷ lệ CONFIRMED/CANCELLED theo từng bác sĩ, số bệnh nhân mới.

**C. Admin Thu ngân (Cashier Admin)**
* **Tiếp nhận & xác nhận đặt lịch:** Xem danh sách lịch hẹn đang chờ (PENDING); xác minh thông tin bệnh nhân; xác nhận (CONFIRMED) hoặc từ chối kèm lý do.
* **Thông báo cho bác sĩ:** Sau khi xác nhận, hệ thống tự động push thông báo cho bác sĩ phụ trách, kèm thông tin: bệnh nhân khám mới hay tái khám.
* **Nhận đơn thuốc từ bác sĩ:** Sau khi bác sĩ gửi đơn thuốc, thu ngân nhận thông báo với đầy đủ danh sách thuốc, liều lượng, tổng chi phí.
* **Thu phí đơn thuốc:** Bệnh nhân đưa đơn thuốc hoặc quét mã QR thanh toán → Thu ngân xác nhận thu tiền → Tiến hành phát thuốc.
* **Quản lý doanh thu:** Ghi nhận và theo dõi các khoản thu: phí khám, phí thuốc, thống kê doanh thu theo ngày.

**D. Bác sĩ (Doctor)**
* **Nhận thông báo ca khám:** Được thông báo khi có ca mới được xác nhận, ghi rõ: bệnh nhân khám mới hay tái khám, thông tin cơ bản và lý do khám.
* **Xem hồ sơ bệnh nhân:** Tìm kiếm bệnh nhân theo tên → Xem hồ sơ đầy đủ → Bấm vào sẽ hiển thị toàn bộ lịch sử khám bệnh chi tiết theo thời gian.
* **Kê đơn thuốc chuẩn:** Điền đơn thuốc theo mẫu chuẩn đã có sẵn (in được khổ A5). Ghi chú tái khám hoặc không tái khám trực tiếp trong đơn.
* **Gửi đơn thuốc:** Gửi đơn thuốc cho thu ngân xử lý. Thu ngân thu phí và tiến hành phát thuốc theo đơn.
* **Block ngày nghỉ:** Tạm khóa ngày nghỉ đột xuất mà không cần xóa toàn bộ lịch làm việc.

**3.3 State Machine – Vòng đời lịch hẹn**
Trạng thái lịch hẹn được quản lý theo sơ đồ sau:

| Trạng thái từ | Trạng thái đến | Điều kiện / Tác nhân |
| :--- | :--- | :--- |
| PENDING | CONFIRMED | Thu ngân xác nhận thông tin bệnh nhân |
| PENDING | CANCELLED | Thu ngân từ chối (kèm lý do) hoặc bệnh nhân tự hủy (trước 24h) |
| CONFIRMED | IN_PROGRESS | Bệnh nhân đến khám, xuất trình mã QR/mã vạch |
| CONFIRMED | CANCELLED | Hủy bởi thu ngân hoặc bác sĩ (kèm lý do) |
| IN_PROGRESS | PRESCRIPTION_SENT | Bác sĩ hoàn thành khám, gửi đơn thuốc cho thu ngân |
| PRESCRIPTION_SENT | COMPLETED | Thu ngân xác nhận thu phí và phát thuốc |

---

### 4. CHI TIẾT CÁC MODULE KỸ THUẬT

* **Module 1: Quản lý Tài khoản & Phân quyền:** Hệ thống xác thực và phân quyền làm nền tảng bảo mật cho toàn bộ API. Hệ thống hỗ trợ 4 vai trò: Bệnh nhân, Bác sĩ, Admin Nhân sự, Admin Thu ngân. Xác thực dựa trên JWT (Access Token 30 phút + Refresh Token 7 ngày). Tài khoản bác sĩ và thu ngân do Admin Nhân sự tạo và phê duyệt.
* **Module 2: Bác sĩ, Chuyên khoa & Lịch làm việc:** Bác sĩ định nghĩa lịch làm việc theo pattern tuần (VD: Thứ 2-4-6, 8:00–12:00, 30 phút/ca). Smart Scheduling Engine tự động sinh slot khả dụng on-demand, không pre-generate vào DB. Bác sĩ có thể block ngày nghỉ đột xuất.
* **Module 3: Luồng Đặt lịch & Quản lý Trạng thái:** Quản lý vòng đời hoàn chỉnh của lịch hẹn. Race condition check bằng `SELECT ... FOR UPDATE` để chống double-booking. Hệ thống tự động sinh mã QR / mã vạch sau khi bệnh nhân thanh toán và thu ngân xác nhận. Giấy hẹn khám được gửi tự động kèm lộ trình khám.
* **Module 4: Hồ sơ Bệnh nhân & Sổ khám điện tử:** Bác sĩ tra cứu hồ sơ bệnh nhân theo tên. Mỗi hồ sơ lưu đầy đủ: thông tin cá nhân, tiền sử bệnh, danh sách tất cả lần khám kèm đơn thuốc. Bệnh nhân xem sổ khám điện tử ở chế độ read-only với giao diện chuyên nghiệp.
* **Module 5: Đơn thuốc & Thanh toán:** Bác sĩ kê đơn thuốc theo mẫu chuẩn (render A5, in được). Đơn thuốc ghi rõ có/không tái khám, ngày tái khám (nếu có). Thu ngân nhận đơn thuốc, thu phí (trực tiếp hoặc qua quét mã QR), xác nhận phát thuốc.
* **Module 6: Thống kê & Quản trị (HR Admin):** Dashboard tổng quan với biểu đồ Chart.js: lịch hẹn theo thời gian, tỷ lệ xác nhận/hủy, doanh thu theo ngày. Admin Nhân sự quản lý toàn bộ tài khoản và có thể can thiệp vào bất kỳ dữ liệu nào trong hệ thống.

---

### 5. PHÂN TÍCH & THIẾT KẾ

**5.1 Yêu cầu chức năng – Phân loại MoSCoW**

**MUST-HAVE (Bắt buộc – MVP):**
* Đăng ký/Đăng nhập 4 vai trò (Patient, Doctor, HR Admin, Cashier Admin) với JWT.
* Bệnh nhân: Đặt lịch, nhận mã QR/mã vạch, xem giấy hẹn khám có lộ trình, xem sổ khám điện tử.
* Thu ngân: Tiếp nhận, xác nhận/từ chối đặt lịch, thông báo bác sĩ, nhận đơn thuốc, thu phí, phát thuốc.
* Bác sĩ: Nhận thông báo ca khám (mới/tái khám), xem hồ sơ & lịch sử bệnh nhân, kê đơn thuốc, gửi đơn cho thu ngân.
* HR Admin: Phê duyệt tài khoản, CRUD chuyên khoa, quản lý nhân sự, xem thống kê.
* State Machine đầy đủ: PENDING → CONFIRMED → IN_PROGRESS → PRESCRIPTION_SENT → COMPLETED.
* Email tự động: xác nhận đặt lịch, giấy hẹn khám, thông báo xác nhận/hủy.

**SHOULD-HAVE:**
* Email nhắc lịch tự động 24h trước ca khám (APScheduler).
* Phân trang (pagination) cho tất cả list endpoint.
* Block date: Bác sĩ đánh dấu ngày nghỉ đột xuất.

**COULD-HAVE:**
* Đánh giá bác sĩ (Rating 1-5 sao) sau khi ca khám COMPLETED.
* Dashboard doanh thu chi tiết theo tháng cho Admin Thu ngân.

**5.2 Mô hình Thực thể Dữ liệu (ERD – Lược đồ mức logic)**
Hệ thống được mở rộng lên 8 thực thể cốt lõi:

| Thực thể | Các trường chính |
| :--- | :--- |
| Users | id, email, password_hash, full_name, phone, role (patient/doctor/hr_admin/cashier_admin), is_active, created_at |
| Doctors | id, user_id FK, specialty_id FK, bio, experience_years, is_approved |
| Specialties | id, name (Unique), description |
| Schedules | id, doctor_id FK, day_of_week, start_time, end_time, slot_duration_min, max_slots |
| Appointments | id, patient_id FK, doctor_id FK, scheduled_date, scheduled_time, reason, status, is_revisit, qr_code, reminder_sent, created_at |
| MedicalRecords | id, appointment_id FK, patient_id FK, doctor_id FK, diagnosis, notes, revisit_date, revisit_required, created_at |
| Prescriptions | id, medical_record_id FK, drug_name, dosage, frequency, duration, notes |
| Payments | id, appointment_id FK, cashier_id FK, amount, payment_method, status, paid_at |

**5.3 Kiến trúc hệ thống**
Hệ thống theo kiến trúc phân tầng 4 lớp:
* **Client Tier:** Trình duyệt web của người dùng (4 loại dashboard riêng biệt).
* **Frontend Tier:** HTML/CSS/JS thuần – Render Static Site (Render.com).
* **Backend API Tier:** FastAPI + Python – Router → Auth Middleware → Service → Repository → DB.
* **Data Tier:** PostgreSQL (Render managed) + Background Tasks (APScheduler + Email Service).

**5.4 Cấu trúc thư mục dự án**
Dưới đây là cấu trúc thư mục chi tiết của dự án:

```text
MedBook/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── config.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── doctor.py
│   │   │   ├── specialty.py
│   │   │   ├── schedule.py
│   │   │   ├── appointment.py
│   │   │   ├── medical_record.py
│   │   │   ├── prescription.py
│   │   │   └── payment.py
│   │   ├── schemas/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── doctors.py
│   │   │   ├── appointments.py
│   │   │   ├── medical_records.py
│   │   │   ├── prescriptions.py
│   │   │   ├── payments.py
│   │   │   ├── admin_hr.py
│   │   │   └── admin_cashier.py
│   │   ├── services/
│   │   └── core/
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── patient/
    │   ├── dashboard.html
    │   ├── booking.html
    │   └── medical-record.html
    ├── doctor/
    │   ├── dashboard.html
    │   └── prescription.html
    ├── admin_hr/
    │   └── dashboard.html
    ├── admin_cashier/
    │   ├── dashboard.html
    │   └── pharmacy.html
    ├── js/
    │   ├── config.js
    │   ├── auth.js
    │   └── api.js
    └── css/
        └── style.css
```

---

### 6. CÔNG NGHỆ SỬ DỤNG (TECH STACK)

| Layer | Công nghệ | Ghi chú |
| :--- | :--- | :--- |
| Frontend | HTML5, CSS3, JavaScript (ES6+) | Không dùng framework – thuần JS với Fetch API |
| Backend | Python 3.11+, FastAPI | Framework chính |
| ORM | SQLAlchemy 2.0 (async) | Kết nối PostgreSQL qua asyncpg |
| Database | PostgreSQL (Render managed) | Free tier trên Render |
| Migration | Alembic | Quản lý schema version |
| Authentication | python-jose (JWT), passlib + bcrypt | Access Token 30 phút, Refresh 7 ngày |
| QR Code | qrcode (Python) / jsQR (Frontend) | Sinh và đọc mã QR/mã vạch xác thực |
| Email | FastAPI-Mail, Jinja2 | HTML email template |
| Background Tasks | APScheduler | Nhắc lịch 24h trước ca khám |
| Chart | Chart.js (CDN) | Render biểu đồ thống kê trên Admin frontend |
| Testing | Pytest, httpx (AsyncClient) | Coverage mục tiêu >= 70% |
| Deployment | Render Web Service + Static Site + PostgreSQL | Free tier, auto-deploy từ GitHub nhánh main |
| API Docs | Swagger UI + ReDoc | Tự sinh từ FastAPI tại /docs và /redoc |

---

### 7. KẾ HOẠCH PHÁT TRIỂN

**7.1 MVP (Đã hoàn thành: 12.04.2026)**
* Hệ thống xác thực & Phân quyền: 4 vai trò, JWT, phê duyệt tài khoản bác sĩ.
* Quy trình khám bệnh đầy đủ: Đặt lịch → Thu ngân xác nhận → Thông báo bác sĩ → Khám → Kê đơn → Phát thuốc.
* Mã QR / mã vạch xác thực được sinh sau khi thanh toán thành công.
* Giấy hẹn khám điện tử có lộ trình chi tiết.
* Sổ khám bệnh điện tử cho bệnh nhân (read-only).
* Đơn thuốc chuẩn A5 với chức năng in, có trường ghi chú tái khám.
* 4 Dashboard riêng biệt với giao diện tối ưu cho từng vai trò.
* Dữ liệu mẫu (Seed Data) để demo ngay lập tức.

**7.2 Test Cases trọng tâm**

| Mã TC | Module | Hành động | Kết quả mong đợi |
| :--- | :--- | :--- | :--- |
| TC-01 | Auth | Đăng ký với email sai format hoặc mật khẩu thiếu chữ hoa | 422 Unprocessable Entity, thông báo lỗi cụ thể từng field |
| TC-02 | Auth | Gọi API không có Authorization header | 401 Unauthorized |
| TC-03 | Auth | Patient gọi endpoint chỉ dành cho Cashier Admin | 403 Forbidden |
| TC-04 | QR Code | Bệnh nhân thanh toán thành công → kiểm tra mã QR | Mã QR được sinh và gắn vào appointment, có thể quét để xác thực |
| TC-05 | Scheduling | Truy vấn slot bác sĩ ngày hợp lệ | Trả về đúng số slot theo lịch, loại trừ slot đã đặt |
| TC-06 | Race Condition | 2 bệnh nhân đặt cùng 1 slot cùng lúc | Chỉ 1 thành công (201), bên còn lại nhận 409 Conflict |
| TC-07 | Flow | Thu ngân xác nhận → kiểm tra thông báo bác sĩ | Bác sĩ nhận thông báo có nhãn Khám mới / Tái khám |
| TC-08 | Flow | Bác sĩ gửi đơn thuốc → kiểm tra thu ngân | Thu ngân nhận thông báo đơn thuốc với đầy đủ thông tin |
| TC-09 | Email | Bệnh nhân đặt lịch thành công | Trong 30 giây, email xác nhận xuất hiện trong hộp thư |
| TC-10 | Frontend | Bệnh nhân truy cập URL dashboard bác sĩ chưa đăng nhập | JS kiểm tra localStorage, redirect về trang login |

**7.3 Beta Version (Dự kiến: 10.05.2026)**
* **Kiểm thử:** Báo cáo Code Coverage Pytest >= 70%; danh sách lỗi MVP và tình trạng xử lý.
* **Triển khai:** Backend trên Render Web Service, Frontend trên Render Static Site, Database trên Render PostgreSQL – tất cả có URL public để demo.
* **Tài liệu:** Báo cáo kỹ thuật đầy đủ: kiến trúc, hướng dẫn cài đặt local, quyết định thiết kế, tổng kết đồ án.

**7.4 Phân công phát triển**

| Module | Thịnh | Trang |
| :--- | :--- | :--- |
| Module 1 – Auth & Phân quyền | ✔ Chính | – Hỗ trợ |
| Module 2 – Bác sĩ & Chuyên khoa |  ✔ Chính | – Hỗ trợ |
| Module 3 – Đặt lịch & State Machine | ✔ Chính | – Hỗ trợ |
| Module 4 – HR Admin & Thống kê | – Hỗ trợ | ✔ Chính |
| Module 5 – Hồ sơ & Sổ khám điện tử | – Hỗ trợ |  ✔ Chính |
| Module 6 – Đơn thuốc & Thanh toán (Cashier) | – Hỗ trợ | ✔ Chính |

---

### 8. CÂU HỎI

* **Về xử lý race condition:** Nhóm dùng PostgreSQL `SELECT ... FOR UPDATE` bên trong DB transaction để chặn double-booking. Cách này có phù hợp quy mô đồ án không, hay có pattern nào đơn giản hơn mà vẫn đảm bảo nhất quán dữ liệu?
* **Về Smart Scheduling Engine:** Nhóm thiết kế slot generation chạy on-demand (không lưu từng slot vào DB). Với quy mô đồ án (vài trăm appointment), approach nào phù hợp hơn để chấm điểm thiết kế DB?
* **Về phạm vi kiểm thử:** Nhóm viết Pytest (integration test) cho ~70% endpoint quan trọng kết hợp manual test giao diện. Mức độ này đã đủ chưa, hay cần bổ sung thêm dạng test khác (VD: load test, contract test)?
* **Về vai trò Admin Thu ngân:** Nghiệp vụ thu ngân xác nhận lịch hẹn và xử lý đơn thuốc trong một workflow liên tục. Nhóm có nên tách thành 2 endpoint riêng (xác nhận lịch và xử lý thuốc) hay gộp chung vào một flow duy nhất?
```
