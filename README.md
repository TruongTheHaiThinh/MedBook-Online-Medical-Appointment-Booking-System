# 🏥 MedBook - Hướng dẫn khởi chạy ứng dụng (Dành cho Giáo viên chấm bài)

Tài liệu này hướng dẫn chi tiết cách cài đặt thư viện, khởi tạo cơ sở dữ liệu mẫu và khởi chạy nhanh ứng dụng **MedBook** trên bất kỳ máy tính nào chỉ bằng **một cú click chuột** hoặc các dòng lệnh đơn giản.

> [!NOTE]
> **TIỆN ÍCH CÓ SẴN:** Cơ sở dữ liệu SQLite cục bộ `medbook.db` đã được **nạp sẵn toàn bộ dữ liệu mẫu** (32 tài khoản, lịch hẹn mẫu, đơn thuốc mẫu và 20,316 loại thuốc). Giáo viên có thể khởi chạy ứng dụng và đăng nhập trải nghiệm ngay lập tức mà không bắt buộc phải chạy lại lệnh nạp dữ liệu (seed).

---

## 🔑 DANH SÁCH TÀI KHOẢN DÙNG THỬ (TEST ACCOUNTS)

Dưới đây là danh sách toàn bộ các tài khoản thử nghiệm đã được nạp sẵn trong hệ thống để Giáo viên dễ dàng chấm điểm tất cả các tính năng của đồ án:

### 1. Quản trị hệ thống (Admin)
> Quyền hạn: Quản trị toàn bộ hệ thống phòng khám, duyệt hồ sơ bác sĩ mới, **duyệt/từ chối các yêu cầu nghỉ phép của bác sĩ**, quản lý danh mục chuyên khoa, quản lý/khóa người dùng, xem toàn bộ **nhật ký giao dịch tài chính** và tra cứu **hồ sơ bệnh án bệnh nhân**...
*   **Email:** `admin@medbook.vn`
*   **Mật khẩu:** `123y`

### 2. Thu ngân phòng khám (Cashier Admin)
> Quyền hạn: Quản lý danh sách đón tiếp, check-in quét mã QR bệnh nhân đến khám, in phiếu khám kèm số thứ tự, thu phí dịch vụ y tế, in hóa đơn thuốc...
*   **Email:** `cashier@medbook.vn`
*   **Mật khẩu:** `Cashier@123`

### 3. Bác sĩ chuyên khoa (Doctor)
> Quyền hạn: Quản lý lịch làm việc, đăng ký lịch nghỉ phép (chờ HR duyệt), thực hiện khám bệnh, kê đơn thuốc tự động gợi ý từ danh mục 20,316 loại thuốc thực tế, in đơn thuốc mẫu A5 chuẩn y khoa...
*   **Danh sách tài khoản:** MedBook có sẵn **28 tài khoản bác sĩ** thuộc 14 chuyên khoa (từ `pk1@medbook.com` đến `pk14b@medbook.com`).
*   **Ví dụ đăng nhập:**
    *   *Khoa Tim mạch:* `pk1@medbook.com` (Bác sĩ Tim mạch A) hoặc `pk1b@medbook.com` (Bác sĩ Tim mạch B)
    *   *Khoa Tiêu hóa:* `pk2@medbook.com` (Bác sĩ Tiêu hóa A)
    *   *Khoa Chấn thương chỉnh hình:* `pk3@medbook.com` (Bác sĩ Chấn thương Chỉnh hình A)
*   **Mật khẩu chung:** `Doctor@123`

### 4. Bệnh nhân (Patient)
> Quyền hạn: Đăng ký tài khoản, xem hồ sơ bệnh án cá nhân, đặt lịch khám theo chuyên khoa/bác sĩ, thanh toán trực tuyến qua cổng **VNPAY Sandbox**...
*   **Email:** `patient1@medbook.vn` (Họ tên: **Trương Thế Hải Thịnh**)
*   **Email:** `patient2@medbook.vn` (Họ tên: **Nguyễn Văn B**)
*   **Mật khẩu chung:** `Patient@123`

---

## ⚡ CÁCH 1: KHỞI CHẠY TỰ ĐỘNG BẰNG SCRIPT (KHUYÊN DÙNG)
Để giúp Giáo viên dễ dàng khởi động toàn bộ hệ thống mà không cần gõ lệnh thủ công, MedBook đã tích hợp sẵn tệp kịch bản khởi chạy tự động **`run_all.bat`** ở thư mục gốc của dự án.

### Các bước thực hiện:
1. Đảm bảo máy tính đã cài đặt **Python (phiên bản từ 3.9 đến 3.12)** và đã thêm Python vào biến môi trường **PATH** lúc cài đặt.
2. Click đúp chuột vào tệp **`run_all.bat`** ở thư mục gốc của dự án.
3. Kịch bản sẽ tự động:
   - Cài đặt/cập nhật tất cả thư viện cần thiết từ tệp `requirements.txt`.
   - Khởi tạo cấu trúc bảng Database và tự động nạp (seed) dữ liệu mẫu đầy đủ.
   - Khởi động đồng thời **Backend API Server** (cổng 8000) và **Frontend Server** (cổng 5500) ở hai cửa sổ terminal riêng biệt.
   - Tự động mở trình duyệt dẫn trực tiếp đến trang chủ ứng dụng: [http://localhost:5500/frontend/index.html](http://localhost:5500/frontend/index.html)

---

## 🛠️ CÁCH 2: KHỞI CHẠY THỦ CÔNG (TỪNG BƯỚC)

Nếu Giáo viên muốn tự chạy từng bước thủ công bằng dòng lệnh, hãy mở terminal và thực hiện:

### 1. Cài đặt thư viện:
```powershell
pip install -r backend/requirements.txt
```

### 2. Làm sạch và nạp lại dữ liệu mẫu (Tùy chọn - chỉ chạy khi muốn reset database về trạng thái ban đầu):
```powershell
cd backend
python scripts/seed_all.py
cd ..
```

### 3. Khởi chạy Backend API Server (Terminal 1):
```powershell
cd backend
# Trên Windows PowerShell
$env:PYTHONPATH="."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Trên Windows Command Prompt (cmd)
set PYTHONPATH=.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Khởi chạy Frontend Server (Terminal 2 - Đứng ở thư mục gốc của dự án):
```powershell
python -m http.server 5500
```
*Sau khi chạy, truy cập ứng dụng tại địa chỉ:* [http://localhost:5500/frontend/index.html](http://localhost:5500/frontend/index.html)

---

## 🐳 CÁCH 3: KHỞI CHẠY BẰNG DOCKER (CONTAINERIZED)

Hệ thống đã được đóng gói container hóa hoàn chỉnh bằng **Docker** và **Docker Compose**, giúp triển khai nhanh chóng và đồng bộ:

### Các bước thực hiện:
1. Mở terminal tại thư mục gốc của dự án (nơi có file `docker-compose.yml`).
2. Khởi chạy toàn bộ hệ thống (PostgreSQL, Backend API, Frontend Nginx):
   ```bash
   docker-compose up --build -d
   ```
3. Sau khi các container khởi động hoàn tất, chạy lệnh sau để làm sạch và nạp dữ liệu mẫu vào container của Backend:
   ```bash
   docker-compose exec backend python scripts/seed_all.py
   ```
4. Truy cập ứng dụng tại địa chỉ:
   - **Giao diện Frontend:** [http://localhost:5500/frontend/index.html](http://localhost:5500/frontend/index.html)
   - **Tài liệu API Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)
5. Để dừng hệ thống:
   ```bash
   docker-compose down
   ```

---

## 💎 CÁC TÍNH NĂNG NỔI BẬT CỦA MEDBOOK
*   **Đặt lịch khám & Thanh toán VNPAY Sandbox**: Tích hợp cổng thanh toán Sandbox chuẩn VNPAY để người bệnh thanh toán phí đặt lịch trực tuyến, tự động cập nhật trạng thái lịch hẹn sau khi thanh toán thành công và sinh mã QR.
*   **Đón tiếp thông minh & Check-in quét mã QR**: Cho phép Thu ngân check-in quét mã QR của bệnh nhân đến khám trực tiếp ngay tại quầy bằng camera để đẩy vào hàng đợi khám của Bác sĩ.
*   **Duyệt lịch nghỉ phép an toàn**: Khi Bác sĩ xin nghỉ phép, hệ thống đưa vào hàng đợi chờ duyệt. Chỉ khi Admin hệ thống duyệt thì các lịch hẹn trùng trong ngày đó mới bị hủy và gửi email thông báo tự động cho người bệnh.
*   **Tự động gợi ý tên thuốc**: Kê đơn nhanh bằng gợi ý tự động (Autocomplete) lấy từ bộ từ điển 20,316 loại thuốc thực tế.
*   **Mẫu đơn thuốc chuẩn A5**: Tối ưu hiển thị, định dạng chuẩn y khoa và sẵn sàng kết nối máy in để in ra giấy.
*   **Đóng gói Docker hoàn chỉnh**: Sẵn sàng deploy lên các môi trường cloud staging/production một cách nhanh chóng nhất.
