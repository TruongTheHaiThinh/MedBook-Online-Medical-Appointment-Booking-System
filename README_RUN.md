# 🏥 MedBook - Hướng dẫn khởi chạy ứng dụng (Dành cho thầy giáo chấm bài)

Tài liệu này hướng dẫn cách cài đặt thư viện, khởi tạo cơ sở dữ liệu mẫu và khởi chạy nhanh ứng dụng **MedBook** chỉ bằng **một cú click chuột**.

---

## ⚡ CÁCH 1: KHỞI CHẠY TỰ ĐỘNG BẰNG SCRIPT (KHUYÊN DÙNG)
Để giúp thầy dễ dàng khởi động toàn bộ hệ thống mà không cần gõ lệnh thủ công, bạn đã có sẵn tệp kịch bản khởi chạy tự động **`run_all.bat`** ở thư mục gốc của dự án.

### Các bước thực hiện:
1. Đảm bảo máy tính đã cài đặt **Python (3.9 - 3.12)** và đã thêm Python vào biến môi trường **PATH** lúc cài đặt.
2. Click đúp chuột vào tệp **`run_all.bat`** ở thư mục gốc của dự án.
3. Kịch bản sẽ tự động:
   - Cài đặt/cập nhật tất cả thư viện cần thiết từ tệp `requirements.txt`.
   - Khởi tạo cấu trúc bảng Database và tự động nạp (seed) dữ liệu mẫu (các chuyên khoa, tài khoản admin, bác sĩ, bệnh nhân, bộ từ điển thuốc...).
   - Khởi động đồng thời **Backend API Server** (cổng 8000) và **Frontend Server** (cổng 5500) ở hai cửa sổ riêng biệt.
   - Tự động mở trình duyệt dẫn trực tiếp đến trang chủ ứng dụng: [http://localhost:5500/frontend/index.html](http://localhost:5500/frontend/index.html)

---

## 🛠️ CÁCH 2: KHỞI CHẠY THỦ CÔNG (TỪNG BƯỚC)

Nếu thầy muốn tự chạy từng bước thủ công bằng dòng lệnh, hãy mở terminal và thực hiện:

### 1. Cài đặt thư viện & Khởi tạo dữ liệu mẫu (Chỉ cần chạy lần đầu):
```powershell
pip install -r backend/requirements.txt
cd backend
python scripts/seed_all.py
cd ..
```

### 2. Khởi chạy Backend (Terminal 1):
```powershell
cd backend
$env:PYTHONPATH="."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Khởi chạy Frontend (Terminal 2 - Đứng ở thư mục gốc của dự án):
```powershell
python -m http.server 5500
```

---

## 🔑 DANH SÁCH TÀI KHOẢN DÙNG THỬ (TEST ACCOUNTS)

Dưới đây là danh sách các tài khoản đã được nạp sẵn vào cơ sở dữ liệu mẫu để thầy dễ dàng đăng nhập và chấm điểm tất cả các tính năng của đồ án:

### 1. Quản lý Nhân sự (HR Admin)
> Giúp duyệt hồ sơ bác sĩ, **duyệt các yêu cầu nghỉ phép của bác sĩ**, xem thống kê toàn hệ thống...
*   **Email:** `admin@medbook.vn`
*   **Mật khẩu:** `123y` (hoặc `Admin@123` tùy phiên bản database)

### 2. Thu ngân phòng khám (Cashier Admin)
> Giúp thu phí cuộc hẹn khi bệnh nhân đến khám, in hóa đơn...
*   **Email:** `cashier@medbook.vn`
*   **Mật khẩu:** `Cashier@123`

### 3. Bác sĩ (Doctor)
> Đăng ký lịch làm việc, **đăng ký nghỉ phép (chờ HR duyệt)**, thực hiện khám bệnh, kê đơn thuốc in mẫu A5...
*   **Email:** `pk1@medbook.com` (Bác sĩ Tim mạch A - Khoa Tim mạch)
*   **Email:** `vietnam.175@medbook.vn` (Bác sĩ Nguyễn Việt Nam - Chấn thương Chỉnh hình)
*   **Mật khẩu:** `Doctor@123`

### 4. Bệnh nhân (Patient)
> Đăng ký tài khoản, xem hồ sơ bệnh án cá nhân, đặt lịch khám theo chuyên khoa/bác sĩ, thanh toán trực tuyến (VNPAY)...
*   **Email:** `patient1@medbook.vn` (Trương Thế Hải Thịnh)
*   **Mật khẩu:** `Patient@123`

---

## 🐳 CÁCH 3: KHỞI CHẠY BẰNG DOCKER (DÀNH CHO DEPLOY)

Hệ thống đã được đóng gói container hóa hoàn chỉnh bằng **Docker** và **Docker Compose**, giúp triển khai nhanh trên môi trường Staging/Production một cách đồng bộ nhất:

### Các bước thực hiện:
1. Mở terminal tại thư mục gốc của dự án (nơi có file `docker-compose.yml`).
2. Khởi chạy toàn bộ hệ thống (PostgreSQL, Backend API, Frontend Nginx):
   ```bash
   docker-compose up --build -d
   ```
3. Sau khi các container khởi động hoàn tất, chạy lệnh sau để khởi tạo cơ sở dữ liệu và nạp dữ liệu mẫu vào container của Backend:
   ```bash
   docker-compose exec backend python scripts/seed_all.py
   ```
4. Truy cập ứng dụng tại địa chỉ quen thuộc:
   - **Frontend:** [http://localhost:5500/frontend/index.html](http://localhost:5500/frontend/index.html)
   - **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
5. Để dừng hệ thống:
   ```bash
   docker-compose down
   ```

---

## 💎 Các tính năng đặc biệt của ứng dụng
*   **Tự động gợi ý tên thuốc**: Kê đơn nhanh bằng gợi ý tự động (Autocomplete) lấy từ dataset 4000 loại thuốc thực tế.
*   **Mẫu đơn thuốc chuẩn A5**: Tối ưu hiển thị, định dạng chuẩn y khoa và sẵn sàng kết nối máy in để in ra giấy.
*   **Đặt lịch và Thanh toán VNPAY**: Tích hợp cổng thanh toán Sandbox chuẩn VNPAY để người bệnh thanh toán hóa đơn khám bệnh.
*   **Duyệt lịch nghỉ phép an toàn**: Khi Bác sĩ xin nghỉ phép, hệ thống đưa vào hàng đợi chờ duyệt. Chỉ khi HR duyệt thì các lịch hẹn trùng trong ngày đó mới bị hủy và gửi email tự động cho người bệnh.
*   **Container hóa hoàn chỉnh (Docker)**: Triển khai nhanh chóng, cấu hình Nginx tối ưu cho web tĩnh ở cổng 5500 và uvicorn cho API ở cổng 8000.
