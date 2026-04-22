# Project Proposal

## THÔNG TIN

### Nhóm

| **Thành viên 1** | Trương Thế Hải Thịnh – 23725051 |
| :--- | :--- |
| **Thành viên 2** | Nguyễn Thị Quỳnh Trang – 23676071 |
| **Git Repository** | https://github.com/TruongTheHaiThinh/MedBook-Online-Medical-Appointment-Booking-System |

### Cấu trúc nhánh Git

| Nhánh | Mục đích | Người phụ trách |
| :--- | :--- | :--- |
| `feature/auth` | Module 1 – Xác thực & Phân quyền (JWT, bcrypt, roles) | Thịnh |
| `feature/doctor-specialty` | Module 2 – Bác sĩ, Chuyên khoa & Lịch làm việc | Thịnh |
| `feature/appointment` | Module 3 – Luồng Đặt lịch & State Machine | Thịnh |
| `feature/admin-management` | Module 4 – Quản lý nhân sự & Kế toán thu ngân | Trang |
| `feature/medical-record` | Module 5 – Hồ sơ bệnh nhân & Sổ khám điện tử | Trang |
| `develop` | Tích hợp tất cả feature branch sau khi review | Cả nhóm |
| `main` | **Push cuối cùng – bản hoàn chỉnh để nộp/deploy** | Cả nhóm |

> **Quy trình làm việc:**
> 1. Mỗi thành viên làm việc trên nhánh `feature/*` riêng
> 2. Khi xong 1 module → tạo Pull Request vào `develop`
> 3. Thành viên còn lại review & approve PR
> 4. Sau khi toàn bộ tính năng ổn định trên `develop` → merge 1 lần duy nhất vào `main`
> 5. **`main` chỉ nhận push cuối cùng** – không commit trực tiếp lên `main` trong quá trình phát triển

---

# MÔ TẢ DỰ ÁN: MEDBOOK – HỆ THỐNG QUẢN LÝ VÀ ĐẶT LỊCH KHÁM BỆNH TRỰC TUYẾN (ONLINE MEDICAL MANAGEMENT & APPOINTMENT BOOKING SYSTEM)

## 1. Ý TƯỞNG DỰ ÁN (THE VISION)

**Tổng quan nền tảng**  
Trong bối cảnh hệ thống y tế Việt Nam đang chịu áp lực quá tải nghiêm trọng, nhóm chúng tôi quyết định xây dựng **MedBook** – một nền tảng Web full-stack chuyên biệt không chỉ giải quyết bài toán đặt lịch hẹn khám bệnh, mà còn tích hợp toàn bộ quy trình quản lý vận hành phòng khám. Đây là một **"Trung tâm quản lý y tế thông minh"** dành cho phòng khám tư nhân và trạm y tế địa phương.

**3 Trụ cột kỹ thuật của MedBook:**
- **Full-Stack Design:** Backend RESTful API (FastAPI + Python) kết hợp Frontend (HTML/CSS/JS thuần), tự động sinh tài liệu Swagger/OpenAPI.
- **Smart Scheduling Engine:** Thuật toán tự động tính slot khả dụng từ lịch làm việc của bác sĩ, xử lý đúng đắn khi bác sĩ đổi lịch đột xuất.
- **Integrated Clinical Workflow:** Toàn bộ quy trình từ đặt lịch → thu ngân xác nhận → bác sĩ khám → kê đơn thuốc → thu phí → phát thuốc được số hóa và liên thông.

---

## 2. VAI TRÒ NGƯỜI DÙNG & PHÂN QUYỀN

Hệ thống mở rộng lên **4 vai trò người dùng** với phân quyền rõ ràng:

| **Vai trò** | **Tên gọi** | **Mô tả** |
| :--- | :--- | :--- |
| Bệnh nhân | Patient | Đặt lịch, xem sổ khám bệnh điện tử, nhận mã QR/mã vạch |
| Admin Nhân sự | HR Admin | Quản lý tài khoản bác sĩ, nhân viên, phê duyệt hồ sơ, thống kê hệ thống |
| Admin Thu ngân | Cashier Admin | Tiếp nhận đặt lịch, xác nhận thông tin, quản lý đơn thuốc & thu phí |
| Bác sĩ | Doctor | Nhận thông báo ca khám, xem hồ sơ bệnh nhân, kê đơn thuốc, gửi đơn cho thu ngân |

---

## 3. CHI TIẾT NGHIỆP VỤ (BUSINESS LOGIC)

### 3.1 Quy trình khám bệnh tổng thể

| **Bước** | **Tác nhân** | **Hành động** |
| :---: | :--- | :--- |
| 1 | Bệnh nhân | Đăng ký tài khoản / đăng nhập → Chọn bác sĩ, chuyên khoa, ngày giờ → Đặt lịch hẹn |
| 2 | Admin Thu ngân | Nhận thông báo đặt lịch → Xem xét & xác nhận thông tin bệnh nhân → Cập nhật trạng thái CONFIRMED |
| 3 | Hệ thống | Tự động gửi Giấy hẹn khám cho bệnh nhân (ghi rõ lộ trình khám: phòng khám, bác sĩ, giờ, hướng dẫn chuẩn bị) |
| 4 | Hệ thống | Thông báo cho bác sĩ phụ trách về ca khám mới (khám mới / tái khám) |
| 5 | Bệnh nhân | Đến phòng khám → Trình mã QR / mã vạch để xác thực (sau khi thanh toán đặt lịch thành công) |
| 6 | Bác sĩ | Tiếp nhận bệnh nhân → Xem toàn bộ hồ sơ & lịch sử khám → Thực hiện khám bệnh |
| 7 | Bác sĩ | Kê đơn thuốc theo mẫu chuẩn → Chỉ định có/không tái khám (ghi trong đơn) → Gửi đơn thuốc cho thu ngân |
| 8 | Admin Thu ngân | Nhận đơn thuốc từ bác sĩ → Thu phí thuốc → Xác nhận thanh toán → Tiến hành phát thuốc |
| 9 | Bệnh nhân | Nhận thuốc → Lịch sử khám & đơn thuốc tự động cập nhật vào Sổ khám điện tử |

### 3.2 Module theo từng vai trò

**A. Bệnh nhân (Patient)**
- **Đặt lịch khám:** Tìm kiếm bác sĩ theo tên, chuyên khoa; chọn ngày giờ theo slot trống; nhập lý do khám (tùy chọn).
- **Nhận mã QR / mã vạch:** Sau khi thanh toán đặt lịch thành công, hệ thống tự động sinh mã QR / mã vạch định danh cho ca khám đó. Bệnh nhân xuất trình mã này khi đến phòng khám để xác thực nhanh.
- **Giấy hẹn khám:** Nhận giấy hẹn điện tử sau khi thu ngân xác nhận, có ghi đầy đủ: tên bác sĩ, phòng khám, giờ hẹn, lộ trình đến khám, các lưu ý chuẩn bị.
- **Sổ khám bệnh điện tử:** Xem toàn bộ lịch sử khám bệnh dưới dạng hồ sơ điện tử chuyên nghiệp (read-only): ngày khám, bác sĩ, chẩn đoán, đơn thuốc, ghi chú tái khám.

**B. Admin Nhân sự (HR Admin)**
- **Quản lý tài khoản:** Phê duyệt hoặc từ chối tài khoản bác sĩ sau khi xác minh thông tin. Khóa tài khoản vi phạm, reset mật khẩu khi cần.
- **Quản lý nhân sự:** CRUD bác sĩ, nhân viên thu ngân. Phân công bác sĩ theo chuyên khoa. Quản lý lịch làm việc tổng thể.
- **Quản lý chuyên khoa:** Tạo, sửa, xóa danh mục chuyên khoa (Tim mạch, Nội tổng quát, Da liễu...).
- **Thống kê hệ thống:** Dashboard tổng quan: tổng lịch hẹn theo ngày/tuần/tháng, tỷ lệ CONFIRMED/CANCELLED theo từng bác sĩ, số bệnh nhân mới.

**C. Admin Thu ngân (Cashier Admin)**
- **Tiếp nhận & xác nhận đặt lịch:** Xem danh sách lịch hẹn đang chờ (PENDING); xác minh thông tin bệnh nhân; xác nhận (CONFIRMED) hoặc từ chối kèm lý do.
- **Thông báo cho bác sĩ:** Sau khi xác nhận, hệ thống tự động push thông báo cho bác sĩ phụ trách, kèm thông tin: bệnh nhân khám mới hay tái khám.
- **Nhận đơn thuốc từ bác sĩ:** Sau khi bác sĩ gửi đơn thuốc, thu ngân nhận thông báo với đầy đủ danh sách thuốc, liều lượng, tổng chi phí.
- **Thu phí đơn thuốc:** Bệnh nhân đưa đơn thuốc hoặc quét mã QR thanh toán → Thu ngân xác nhận thu tiền → Tiến hành phát thuốc.
- **Quản lý doanh thu:** Ghi nhận và theo dõi các khoản thu: phí khám, phí thuốc, thống kê doanh thu theo ngày.

**D. Bác sĩ (Doctor)**
- **Nhận thông báo ca khám:** Được thông báo khi có ca mới được xác nhận, ghi rõ: bệnh nhân khám mới hay tái khám, thông tin cơ bản và lý do khám.
- **Xem hồ sơ bệnh nhân:** Tìm kiếm bệnh nhân theo tên → Xem hồ sơ đầy đủ → Bấm vào sẽ hiển thị toàn bộ lịch sử khám bệnh chi tiết theo thời gian.
- **Kê đơn thuốc chuẩn:** Điền đơn thuốc theo mẫu chuẩn đã có sẵn (in được khổ A5). Ghi chú tái khám hoặc không tái khám trực tiếp trong đơn.
- **Gửi đơn thuốc:** Gửi đơn thuốc cho thu ngân xử lý. Thu ngân thu phí và tiến hành phát thuốc theo đơn.
- **Block ngày nghỉ:** Tạm khóa ngày nghỉ đột xuất mà không cần xóa toàn bộ lịch làm việc.

### 3.3 State Machine – Vòng đời lịch hẹn

| **Trạng thái từ** | **Trạng thái đến** | **Điều kiện / Tác nhân** |
| :--- | :--- | :--- |
| PENDING | CONFIRMED | Thu ngân xác nhận thông tin bệnh nhân |
| PENDING | CANCELLED | Thu ngân từ chối (kèm lý do) hoặc bệnh nhân tự hủy (trước 24h) |
| CONFIRMED | IN_PROGRESS | Bệnh nhân đến khám, xuất trình mã QR/mã vạch |
| CONFIRMED | CANCELLED | Hủy bởi thu ngân hoặc bác sĩ (kèm lý do) |
| IN_PROGRESS | PRESCRIPTION_SENT | Bác sĩ hoàn thành khám, gửi đơn thuốc cho thu ngân |
| PRESCRIPTION_SENT | COMPLETED | Thu ngân xác nhận thu phí và phát thuốc |

```mermaid
stateDiagram-v2
    [*] --> PENDING : Bệnh nhân đặt lịch
    PENDING --> CONFIRMED : Thu ngân xác nhận
    PENDING --> CANCELLED : Thu ngân từ chối / Bệnh nhân hủy (trước 24h)
    CONFIRMED --> IN_PROGRESS : Bệnh nhân đến, xuất trình mã QR
    CONFIRMED --> CANCELLED : Thu ngân / Bác sĩ hủy (kèm lý do)
    IN_PROGRESS --> PRESCRIPTION_SENT : Bác sĩ gửi đơn thuốc
    PRESCRIPTION_SENT --> COMPLETED : Thu ngân thu phí & phát thuốc
    COMPLETED --> [*]
    CANCELLED --> [*]
```

---

## 4. CHI TIẾT CÁC MODULE KỸ THUẬT

### Module 1: Quản lý Tài khoản & Phân quyền
Hệ thống xác thực và phân quyền làm nền tảng bảo mật cho toàn bộ API. Hệ thống hỗ trợ **4 vai trò**: Bệnh nhân, Bác sĩ, Admin Nhân sự, Admin Thu ngân. Xác thực dựa trên JWT (Access Token 30 phút + Refresh Token 7 ngày). Tài khoản bác sĩ và thu ngân do Admin Nhân sự tạo và phê duyệt.

### Module 2: Bác sĩ, Chuyên khoa & Lịch làm việc
Bác sĩ định nghĩa lịch làm việc theo pattern tuần (VD: Thứ 2-4-6, 8:00–12:00, 30 phút/ca). Smart Scheduling Engine tự động sinh slot khả dụng on-demand, không pre-generate vào DB. Bác sĩ có thể block ngày nghỉ đột xuất.

### Module 3: Luồng Đặt lịch & Quản lý Trạng thái
Quản lý vòng đời hoàn chỉnh của lịch hẹn. Race condition check bằng `SELECT ... FOR UPDATE` để chống double-booking. Hệ thống tự động sinh mã QR / mã vạch sau khi bệnh nhân thanh toán và thu ngân xác nhận. Giấy hẹn khám được gửi tự động kèm lộ trình khám.

### Module 4: Hồ sơ Bệnh nhân & Sổ khám điện tử
Bác sĩ tra cứu hồ sơ bệnh nhân theo tên. Mỗi hồ sơ lưu đầy đủ: thông tin cá nhân, tiền sử bệnh, danh sách tất cả lần khám kèm đơn thuốc. Bệnh nhân xem sổ khám điện tử ở chế độ read-only với giao diện chuyên nghiệp.

### Module 5: Đơn thuốc & Thanh toán
Bác sĩ kê đơn thuốc theo mẫu chuẩn (render A5, in được). Đơn thuốc ghi rõ có/không tái khám, ngày tái khám (nếu có). Thu ngân nhận đơn thuốc, thu phí (trực tiếp hoặc qua quét mã QR), xác nhận phát thuốc.

### Module 6: Thống kê & Quản trị (HR Admin)
Dashboard tổng quan với biểu đồ Chart.js: lịch hẹn theo thời gian, tỷ lệ xác nhận/hủy, doanh thu theo ngày. Admin Nhân sự quản lý toàn bộ tài khoản và có thể can thiệp vào bất kỳ dữ liệu nào trong hệ thống.

---

## PHÂN TÍCH & THIẾT KẾ

> **Ghi chú:** Nhóm sử dụng phương pháp MoSCoW để phân định rõ phạm vi dự án, đảm bảo tính khả thi cho nhóm 2 người trong thời gian đồ án nhưng vẫn giữ được chiều sâu kỹ thuật của hệ thống.

### 1. Yêu cầu chức năng hệ thống – Phân loại MoSCoW

#### Nhóm MUST-HAVE (Bắt buộc – MVP):

- **Đăng ký/Đăng nhập 4 vai trò** (Patient, Doctor, HR Admin, Cashier Admin) với JWT. Tài khoản Doctor và Cashier do HR Admin tạo/phê duyệt.
- **Bệnh nhân:** Đặt lịch, nhận mã QR/mã vạch, xem giấy hẹn khám có lộ trình, xem sổ khám điện tử.
- **Thu ngân:** Tiếp nhận, xác nhận/từ chối đặt lịch, thông báo bác sĩ, nhận đơn thuốc, thu phí, phát thuốc.
- **Bác sĩ:** Nhận thông báo ca khám (mới/tái khám), xem hồ sơ & lịch sử bệnh nhân, kê đơn thuốc chuẩn A5, gửi đơn cho thu ngân.
- **HR Admin:** Phê duyệt tài khoản, CRUD chuyên khoa, quản lý nhân sự, xem thống kê.
- **State Machine đầy đủ:** `PENDING → CONFIRMED → IN_PROGRESS → PRESCRIPTION_SENT → COMPLETED`.
- **Email tự động:** Xác nhận đặt lịch, giấy hẹn khám, thông báo xác nhận/hủy.

#### Nhóm SHOULD-HAVE:
- **Email nhắc lịch tự động:** Background job (APScheduler) chạy mỗi giờ, gửi email nhắc trước 24h.
- **Phân trang (Pagination):** Tất cả list endpoint hỗ trợ `?page=1&size=20`.
- **Block date (Doctor):** Bác sĩ đánh dấu ngày nghỉ đột xuất.

#### Nhóm COULD-HAVE:
- **Đánh giá bác sĩ (Rating):** 1-5 sao sau khi ca khám COMPLETED.
- **Dashboard doanh thu chi tiết** theo tháng cho Admin Thu ngân.

---

### 2. Yêu cầu Phi chức năng

- **Bảo mật:**
  - Mật khẩu phải hash bằng `bcrypt` (cost factor ≥ 12) trước khi lưu Database.
  - Toàn bộ route API (ngoại trừ `/auth/register`, `/auth/login`, `GET /doctors`) phải xác thực JWT.
  - Rate limiting cho endpoint đăng nhập (tối đa 5 lần thất bại/phút/IP) để chống brute-force.
- **Tính nhất quán dữ liệu:**
  - Race condition khi nhiều bệnh nhân cùng đặt 1 slot: sử dụng DB transaction với **`SELECT ... FOR UPDATE`** (PostgreSQL syntax) để tránh double-booking.
  - Không thể xóa Doctor nếu còn appointment đang PENDING hoặc CONFIRMED.
- **Hiệu năng:**
  - Các list endpoint hỗ trợ pagination. Index DB trên các cột thường xuyên filter: `appointments.doctor_id`, `appointments.scheduled_date`, `appointments.status`.
  - Response time mục tiêu < 500ms cho 95% request trong điều kiện bình thường.
- **Tính bảo trì:**
  - Source code theo kiến trúc phân tầng Router → Service → Repository, dễ test từng layer độc lập.
  - Có file `README.md` với hướng dẫn cài đặt local, cấu hình biến môi trường `.env.example`, và lệnh chạy migration.

---

### 3. Mô hình Thực thể Dữ liệu (Entity Relationship – Lược đồ mức logic)

Hệ thống được mở rộng lên **8 thực thể (Entities)** cốt lõi:

| **Thực thể** | **Các trường chính** |
| :--- | :--- |
| Users | `id`, `email`, `password_hash`, `full_name`, `phone`, `role` (patient/doctor/hr_admin/cashier_admin), `is_active`, `created_at` |
| Doctors | `id`, `user_id` FK, `specialty_id` FK, `bio`, `experience_years`, `is_approved` |
| Specialties | `id`, `name` (Unique), `description` |
| Schedules | `id`, `doctor_id` FK, `day_of_week`, `start_time`, `end_time`, `slot_duration_min`, `max_slots` |
| Appointments | `id`, `patient_id` FK, `doctor_id` FK, `scheduled_date`, `scheduled_time`, `reason`, `status`, `is_revisit`, `qr_code`, `reminder_sent`, `created_at` |
| MedicalRecords | `id`, `appointment_id` FK, `patient_id` FK, `doctor_id` FK, `diagnosis`, `notes`, `revisit_date`, `revisit_required`, `created_at` |
| Prescriptions | `id`, `medical_record_id` FK, `drug_name`, `dosage`, `frequency`, `duration`, `notes` |
| Payments | `id`, `appointment_id` FK, `cashier_id` FK, `amount`, `payment_method`, `status`, `paid_at` |

```mermaid
erDiagram
    Users ||--o{ Appointments : "đặt lịch (patient)"
    Users ||--o| Doctors : "hồ sơ bác sĩ"
    Users ||--o{ Payments : "thu ngân xử lý"
    Doctors ||--o{ Appointments : "nhận ca khám"
    Doctors ||--o{ Schedules : "thiết lập lịch"
    Specialties ||--o{ Doctors : "phân loại"
    Appointments ||--o| MedicalRecords : "kết quả khám"
    Appointments ||--o| Payments : "thanh toán"
    MedicalRecords ||--o{ Prescriptions : "đơn thuốc"

    Users {
        uuid id PK
        varchar email "Unique, NOT NULL"
        varchar password_hash
        varchar full_name
        varchar phone
        varchar role "patient/doctor/hr_admin/cashier_admin"
        boolean is_active "Default true"
        timestamp created_at
    }

    Doctors {
        uuid id PK
        uuid user_id FK
        uuid specialty_id FK
        text bio
        int experience_years
        boolean is_approved "HR Admin phê duyệt"
    }

    Specialties {
        uuid id PK
        varchar name "Unique"
        varchar description
    }

    Schedules {
        uuid id PK
        uuid doctor_id FK
        int day_of_week "0=CN, 1=T2, ... 6=T7"
        time start_time
        time end_time
        int slot_duration_min
        int max_slots
    }

    Appointments {
        uuid id PK
        uuid patient_id FK
        uuid doctor_id FK
        date scheduled_date
        time scheduled_time
        varchar reason
        varchar status "PENDING/CONFIRMED/IN_PROGRESS/PRESCRIPTION_SENT/CANCELLED/COMPLETED"
        boolean is_revisit "Default false"
        varchar qr_code "Mã QR xác thực"
        boolean reminder_sent "Default false"
        timestamp created_at
    }

    MedicalRecords {
        uuid id PK
        uuid appointment_id FK
        uuid patient_id FK
        uuid doctor_id FK
        text diagnosis
        text notes
        date revisit_date
        boolean revisit_required
        timestamp created_at
    }

    Prescriptions {
        uuid id PK
        uuid medical_record_id FK
        varchar drug_name
        varchar dosage
        varchar frequency
        varchar duration
        text notes
    }

    Payments {
        uuid id PK
        uuid appointment_id FK
        uuid cashier_id FK
        decimal amount
        varchar payment_method
        varchar status
        timestamp paid_at
    }
```

---

### 4. Kiến trúc hệ thống

```mermaid
graph TD
    classDef client fill:#dbeafe,stroke:#3b82f6,stroke-width:2px,color:#1e3a8a;
    classDef frontend fill:#ede9fe,stroke:#7c3aed,stroke-width:2px,color:#3b0764;
    classDef backend fill:#dcfce7,stroke:#22c55e,stroke-width:2px,color:#14532d;
    classDef database fill:#fef08a,stroke:#eab308,stroke-width:2px,color:#713f12;
    classDef external fill:#f3f4f6,stroke:#9ca3af,stroke-width:2px,color:#374151,stroke-dasharray: 5 5;

    subgraph Client_Tier ["Tầng Client"]
        A["👤 Người dùng\n(Trình duyệt)"]:::client
    end

    subgraph Frontend_Tier ["Frontend – HTML/CSS/JS (Render Static Site)"]
        A --> |"HTTPS"| FE["Giao diện Web\nHTML/CSS/JS thuần\nPatient / Doctor / HR Admin / Cashier Admin pages"]:::frontend
        FE --> |"fetch() + JWT"| B
    end

    subgraph Application_Tier ["Backend API – FastAPI (Render Web Service)"]
        B("Router Layer\nĐịnh tuyến & Validate Input\n(Pydantic Schemas)"):::backend
        B --> C["Auth Middleware\nJWT Verify & Role Check\n(Dependency Injection)"]:::backend
        C --> D["Service Layer\nBusiness Logic thuần túy\n(Scheduling Engine, State Machine, QR Generator)"]:::backend
        D --> E["Repository Layer\nTruy vấn DB qua SQLAlchemy 2.0\n(asyncpg driver)"]:::backend
    end

    subgraph Data_Tier ["Database"]
        E --> |"ORM Query (async)"| F[("PostgreSQL\nRender managed DB\nUsers, Doctors, Schedules\nAppointments, MedicalRecords\nPrescriptions, Payments")]:::database
    end

    subgraph Background_Tier ["Background Tasks"]
        D -.-> |"Trigger khi tạo/cập nhật appointment"| G["Email Service\nFastAPI-Mail + Jinja2 Template\n(Xác nhận, Hủy, Giấy hẹn khám)"]:::external
        H["APScheduler\nJob chạy mỗi giờ\n(Nhắc lịch 24h trước)"]:::external --> F
        H --> G
    end
```

---

### 5. Use Case Diagram

```mermaid
graph LR
    classDef actor fill:#e0f2fe,stroke:#0284c7,stroke-width:2px
    classDef usecase fill:#f0fdf4,stroke:#16a34a,stroke-width:1px,rx:20

    Patient(["👤 Bệnh nhân"]):::actor
    Doctor(["👨‍⚕️ Bác sĩ"]):::actor
    HRAdmin(["🔧 HR Admin"]):::actor
    Cashier(["💰 Thu ngân"]):::actor

    subgraph MedBook System
        UC1["Đăng ký / Đăng nhập"]:::usecase
        UC2["Tìm kiếm bác sĩ\ntheo chuyên khoa"]:::usecase
        UC3["Xem slot trống\ntheo ngày"]:::usecase
        UC4["Đặt lịch hẹn"]:::usecase
        UC5["Nhận mã QR\n/ mã vạch"]:::usecase
        UC6["Xem giấy hẹn khám\n(có lộ trình)"]:::usecase
        UC7["Hủy lịch hẹn\n(trước 24h)"]:::usecase
        UC8["Xem sổ khám\nbệnh điện tử"]:::usecase
        UC9["Thiết lập\nlịch làm việc"]:::usecase
        UC10["Nhận thông báo\nca khám mới/tái khám"]:::usecase
        UC11["Xem hồ sơ\nbệnh nhân"]:::usecase
        UC12["Kê đơn thuốc\n(chuẩn A5)"]:::usecase
        UC13["Gửi đơn thuốc\ncho thu ngân"]:::usecase
        UC14["Block ngày nghỉ\nđột xuất"]:::usecase
        UC15["Tiếp nhận &\nxác nhận đặt lịch"]:::usecase
        UC16["Thông báo bác sĩ\n(mới/tái khám)"]:::usecase
        UC17["Nhận & xử lý\nđơn thuốc"]:::usecase
        UC18["Thu phí &\nphát thuốc"]:::usecase
        UC19["Quản lý doanh thu"]:::usecase
        UC20["Phê duyệt\ntài khoản bác sĩ"]:::usecase
        UC21["Quản lý nhân sự\n& chuyên khoa"]:::usecase
        UC22["Xem thống kê\nhệ thống"]:::usecase
        UC23["Nhận email\ntự động"]:::usecase
    end

    Patient --> UC1
    Patient --> UC2
    Patient --> UC3
    Patient --> UC4
    Patient --> UC5
    Patient --> UC6
    Patient --> UC7
    Patient --> UC8
    Patient --> UC23

    Doctor --> UC1
    Doctor --> UC9
    Doctor --> UC10
    Doctor --> UC11
    Doctor --> UC12
    Doctor --> UC13
    Doctor --> UC14
    Doctor --> UC23

    Cashier --> UC15
    Cashier --> UC16
    Cashier --> UC17
    Cashier --> UC18
    Cashier --> UC19
    Cashier --> UC23

    HRAdmin --> UC20
    HRAdmin --> UC21
    HRAdmin --> UC22
```

---

### 6. Công nghệ sử dụng (Tech Stack)

| Layer | Công nghệ | Ghi chú |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) | Không dùng framework – thuần JS với Fetch API |
| **Backend** | Python 3.11+, FastAPI | Framework chính |
| **ORM** | SQLAlchemy 2.0 (async) | Kết nối PostgreSQL qua `asyncpg` |
| **DB Driver** | `asyncpg` | Driver async cho PostgreSQL |
| **Database** | **PostgreSQL** (Render managed) | Free tier trên Render |
| **Migration** | Alembic | Quản lý schema version |
| **Authentication** | `python-jose` (JWT), `passlib` + `bcrypt` | Access Token 30 phút, Refresh 7 ngày |
| **QR Code** | `qrcode` (Python) / `jsQR` (Frontend) | Sinh và đọc mã QR/mã vạch xác thực |
| **Email** | FastAPI-Mail, Jinja2 | HTML email template |
| **Background Tasks** | APScheduler | Nhắc lịch 24h trước ca khám |
| **Chart** | Chart.js (CDN) | Render biểu đồ thống kê trên Admin frontend |
| **Testing** | Pytest, `httpx` (AsyncClient) | Coverage mục tiêu ≥ 70% |
| **Deployment – Backend** | **Render Web Service** | Free tier, auto-deploy từ GitHub nhánh `main` |
| **Deployment – Frontend** | **Render Static Site** | Free tier, auto-deploy từ GitHub |
| **Deployment – Database** | **Render PostgreSQL** | Free tier 90 ngày |
| **API Docs** | Swagger UI + ReDoc | Tự sinh từ FastAPI tại `/docs` và `/redoc` |

> **Lưu ý về kết nối Database trên Render:**  
> Render cung cấp PostgreSQL managed database tích hợp sẵn với Web Service. Connection string có dạng:  
> `postgresql+asyncpg://user:pass@host/dbname`  
> Render tự động inject biến môi trường `DATABASE_URL` vào Web Service khi link database – không cần cấu hình thủ công.

> **Lưu ý về CORS cho Frontend:**  
> Backend cần cấu hình CORS cho phép origin của Render Static Site. Trong `main.py`:
> ```python
> app.add_middleware(CORSMiddleware, allow_origins=["https://your-frontend.onrender.com"])
> ```

---

### 7. Cấu trúc thư mục dự án

```
MedBook/                          ← GitHub repository root
├── backend/
│   ├── app/
│   │   ├── main.py               ← Khởi tạo FastAPI app, CORS, router
│   │   ├── database.py           ← Async engine + session PostgreSQL
│   │   ├── config.py             ← Pydantic Settings (đọc .env)
│   │   ├── models/               ← SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── doctor.py
│   │   │   ├── specialty.py
│   │   │   ├── schedule.py
│   │   │   ├── appointment.py
│   │   │   ├── medical_record.py
│   │   │   ├── prescription.py
│   │   │   └── payment.py
│   │   ├── schemas/              ← Pydantic request/response schemas
│   │   ├── routers/              ← FastAPI routers (1 file = 1 module)
│   │   │   ├── auth.py
│   │   │   ├── doctors.py
│   │   │   ├── appointments.py
│   │   │   ├── medical_records.py
│   │   │   ├── prescriptions.py
│   │   │   ├── payments.py
│   │   │   ├── admin_hr.py
│   │   │   └── admin_cashier.py
│   │   ├── services/             ← Business logic (scheduling engine, state machine, QR)
│   │   └── core/                 ← JWT, security, email, scheduler
│   ├── alembic/                  ← Migration scripts
│   ├── tests/                    ← Pytest test files
│   ├── .env.example              ← Template biến môi trường
│   ├── requirements.txt
│   └── README.md
│
└── frontend/
    ├── index.html                ← Trang chủ / Login
    ├── patient/
    │   ├── dashboard.html        ← Danh sách lịch hẹn của bệnh nhân
    │   ├── booking.html          ← Tìm bác sĩ & đặt lịch
    │   └── medical-record.html   ← Sổ khám bệnh điện tử
    ├── doctor/
    │   ├── dashboard.html        ← Quản lý lịch hẹn & ca khám
    │   └── prescription.html     ← Kê đơn thuốc
    ├── admin_hr/
    │   └── dashboard.html        ← Phê duyệt bác sĩ, quản lý nhân sự & thống kê
    ├── admin_cashier/
    │   ├── dashboard.html        ← Xác nhận đặt lịch & quản lý doanh thu
    │   └── pharmacy.html         ← Xử lý đơn thuốc & phát thuốc
    ├── js/
    │   ├── config.js             ← BASE_URL backend
    │   ├── auth.js               ← Login, logout, lưu JWT vào localStorage
    │   └── api.js                ← Hàm fetch() dùng chung (tự gắn Authorization header)
    └── css/
        └── style.css             ← CSS chung toàn bộ trang
```

---

## KẾ HOẠCH

### MVP

**1. Mô tả các chức năng MVP (Đã hoàn thành: 12.04.2026)**

- **Hệ thống xác thực & Phân quyền:** 4 vai trò (Bệnh nhân, Bác sĩ, HR Admin, Cashier Admin), JWT, phê duyệt tài khoản bác sĩ.
- **Quy trình khám bệnh đầy đủ:** Đặt lịch → Thu ngân xác nhận → Thông báo bác sĩ → Khám → Kê đơn → Phát thuốc.
- **Mã QR / mã vạch xác thực** được sinh sau khi thanh toán thành công.
- **Giấy hẹn khám điện tử** có lộ trình chi tiết.
- **Sổ khám bệnh điện tử** cho bệnh nhân (read-only).
- **Đơn thuốc chuẩn A5** với chức năng in, có trường ghi chú tái khám.
- **4 Dashboard riêng biệt** với giao diện tối ưu cho từng vai trò.
- **Dữ liệu mẫu (Seed Data)** để demo ngay lập tức.

**2. Kế hoạch kiểm thử**

| Mã TC | Module | Hành động | Kết quả mong đợi |
| :--- | :--- | :--- | :--- |
| **TC-01** | Auth | Đăng ký với email sai format hoặc mật khẩu thiếu chữ hoa | `422 Unprocessable Entity`, thông báo lỗi cụ thể từng field |
| **TC-02** | Auth | Gọi API không có Authorization header | `401 Unauthorized` |
| **TC-03** | Auth | Patient gọi endpoint chỉ dành cho Cashier Admin | `403 Forbidden` |
| **TC-04** | QR Code | Bệnh nhân thanh toán thành công → kiểm tra mã QR | Mã QR được sinh và gắn vào appointment, có thể quét để xác thực |
| **TC-05** | Scheduling | Truy vấn slot bác sĩ ngày hợp lệ | Trả về đúng số slot theo lịch, loại trừ slot đã đặt |
| **TC-06** | Race Condition | 2 bệnh nhân đặt cùng 1 slot cùng lúc | Chỉ 1 thành công (`201`), bên còn lại nhận `409 Conflict` |
| **TC-07** | Flow | Thu ngân xác nhận → kiểm tra thông báo bác sĩ | Bác sĩ nhận thông báo có nhãn **Khám mới / Tái khám** |
| **TC-08** | Flow | Bác sĩ gửi đơn thuốc → kiểm tra thu ngân | Thu ngân nhận thông báo đơn thuốc với đầy đủ thông tin |
| **TC-09** | Email | Bệnh nhân đặt lịch thành công | Trong 30 giây, email xác nhận xuất hiện trong hộp thư |
| **TC-10** | Frontend | Bệnh nhân truy cập URL dashboard bác sĩ chưa đăng nhập | JS kiểm tra localStorage, redirect về trang login |

- **Unit & Integration Testing (Pytest):**  
  Viết Pytest với `httpx.AsyncClient` cho toàn bộ API endpoint. Mục tiêu coverage ≥ 70% trên các service và router chính.  
  Các test case tiêu biểu: Kiểm tra thuật toán slot generation, test race condition với DB transaction (`SELECT ... FOR UPDATE`), test state machine của appointment (PENDING → CONFIRMED → IN_PROGRESS → PRESCRIPTION_SENT → COMPLETED), test phân quyền từng vai trò.

**3. Phân công phát triển**

| **Module** | **Thịnh** | **Trang** |
| :--- | :---: | :---: |
| Module 1 – Auth & Phân quyền | ✔ Chính | – Hỗ trợ |
| Module 2 – Bác sĩ & Chuyên khoa | – Hỗ trợ | ✔ Chính |
| Module 3 – Đặt lịch & State Machine | ✔ Chính | – Hỗ trợ |
| Module 4 – HR Admin & Thống kê | – Hỗ trợ | ✔ Chính |
| Module 5 – Hồ sơ & Sổ khám điện tử | ✔ Chính | – Hỗ trợ |
| Module 6 – Đơn thuốc & Thanh toán (Cashier) | – Hỗ trợ | ✔ Chính |

**4. Các chức năng dự kiến thực hiện ở Phase tiếp theo**
- **Email nhắc lịch tự động:** Background job APScheduler quét và gửi email 24h trước ca khám.
- **Block date:** Bác sĩ đánh dấu ngày nghỉ đột xuất, slot của ngày đó tự động trả về trống.
- **Rating & Review:** Bệnh nhân đánh giá sau khi ca khám COMPLETED.
- **Dashboard thống kê Admin:** Biểu đồ lịch hẹn theo thời gian bằng Chart.js, tỷ lệ xác nhận/hủy, top bác sĩ bận nhất.

---

### Beta Version
**Thời hạn hoàn thành dự kiến:** 10.05.2026

- **Kết quả kiểm thử:**
  - Báo cáo tổng hợp độ phủ (Code Coverage) của Pytest – mục tiêu đạt > 70% cho các service và router chính.
  - Bảng danh sách lỗi phát hiện trong quá trình test MVP và tình trạng đã xử lý.
- **Triển khai:**
  - Backend chạy ổn định trên Render Web Service, kết nối Render PostgreSQL, có URL public để demo.
  - Frontend HTML/CSS/JS deploy trên Render Static Site, có URL public riêng.
  - Database trên môi trường production được migrate đúng bằng Alembic, không mất dữ liệu khi upgrade.
- **Viết báo cáo:**
  - Hoàn thiện tài liệu kỹ thuật: kiến trúc hệ thống, hướng dẫn cài đặt local, mô tả các quyết định thiết kế quan trọng.
  - Viết báo cáo tổng kết đồ án cuối kỳ, phân tích những điểm đã làm được, chưa làm được và hướng phát triển tương lai.

---

## CÂU HỎI

1. **Về xử lý race condition:** Nhóm dùng PostgreSQL `SELECT ... FOR UPDATE` bên trong DB transaction để chặn double-booking. Cách này có phù hợp quy mô đồ án không, hay có pattern nào đơn giản hơn mà vẫn đảm bảo nhất quán dữ liệu?

2. **Về Smart Scheduling Engine:** Nhóm thiết kế slot generation chạy **on-demand** (không lưu từng slot vào DB). Với quy mô đồ án (vài trăm appointment), approach nào phù hợp hơn để chấm điểm thiết kế DB?

3. **Về phạm vi kiểm thử:** Nhóm viết Pytest (integration test) cho ~70% endpoint quan trọng kết hợp manual test giao diện. Mức độ này đã đủ chưa, hay cần bổ sung thêm dạng test khác (VD: load test, contract test)?

4. **Về vai trò Admin Thu ngân:** Nghiệp vụ thu ngân xác nhận lịch hẹn và xử lý đơn thuốc trong một workflow liên tục. Nhóm có nên tách thành 2 endpoint riêng (xác nhận lịch và xử lý thuốc) hay gộp chung vào một flow duy nhất?
