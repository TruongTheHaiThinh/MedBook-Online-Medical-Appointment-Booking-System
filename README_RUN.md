# 🚀 Hướng dẫn Chạy ứng dụng MedBook

Tài liệu này hướng dẫn bạn cách khởi động toàn bộ hệ thống MedBook (bao gồm Backend FastAPI và Giao diện Frontend) trên máy tính cá nhân.

## 📋 Điều kiện tiên quyết
*   Đã cài đặt **Python 3.9+**
*   Máy tính chạy Windows (theo môi trường hiện tại của bạn)

---

## 🛠️ Bước 1: Thiết lập Backend
Backend được xây dựng bằng FastAPI và sử dụng SQLite làm cơ sở dữ liệu.

1.  **Mở Terminal** và di chuyển vào thư mục `backend`:
    ```powershell
    cd backend
    ```

2.  **Kích hoạt môi trường ảo (Virtual Environment)**:
    ```powershell
    .\venv\Scripts\activate
    ```

3.  **Cài đặt thư viện (nếu cần)**:
    ```powershell
    pip install -r requirements.txt
    ```

4.  **Khởi tạo Cơ sở dữ liệu (Nếu chạy lần đầu hoặc muốn reset)**:
    ```powershell
    $env:PYTHONPATH="."
    python scratch/init_db.py
    ```
    *Lưu ý: Thao tác này sẽ xóa sạch dữ liệu cũ và tạo lại các tài khoản mẫu.*

5.  **Khởi chạy Server**:
    ```powershell
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    *   *Server sẽ chạy tại:* **http://localhost:8000**
    *   *Tài liệu API:* **http://localhost:8000/docs**

---

## 🌐 Bước 2: Thiết lập Frontend
Frontend là các trang HTML/JS tĩnh, bạn cần chạy một web server đơn giản để truy cập.

1.  **Mở một Terminal mới** và di chuyển vào thư mục `frontend`:
    ```powershell
    cd frontend
    ```

2.  **Chạy server tĩnh bằng Python**:
    ```powershell
    python -m http.server 5500
    ```
    *   *Giao diện sẽ chạy tại:* **http://localhost:5500**

---

## 🚦 Hướng dẫn Truy cập các vai trò

Sau khi cả hai server đã chạy, bạn mở trình duyệt và truy cập **http://localhost:5500**.

### 1. Vai trò Bệnh nhân (Màu Xanh lá)
*   **Tài khoản**: `0912345678` (hoặc `patient1@gmail.com`)
*   **Mật khẩu**: `Patient@123`

### 2. Vai trò Bác sĩ (Bệnh viện MedBook)
Tài khoản đăng nhập chung cho các bác sĩ:
*   **Mật khẩu**: `Doctor@123` (Cho tất cả các khoa bên dưới)
*   **Danh sách tài khoản theo khoa**:
    1.  Khoa Tim mạch: `pk1@medbook.com`
    2.  Khoa Tiêu hóa: `pk2@medbook.com`
    3.  Khoa Chấn thương chỉnh hình: `pk3@medbook.com`
    4.  Khoa Nội Thần kinh: `pk4@medbook.com`
    5.  Khoa Truyền nhiễm: `pk5@medbook.com`
    6.  Khoa Sản phụ khoa: `pk6@medbook.com`
    7.  Khoa Thận - Lọc máu: `pk7@medbook.com`
    8.  Khoa Ung bướu: `pk8@medbook.com`
    9.  Khoa Răng Hàm Mặt: `pk9@medbook.com`
    10. Khoa Tai Mũi Họng: `pk10@medbook.com`
    11. Khoa Mắt: `pk11@medbook.com`
    12. Khoa Phục hồi chức năng: `pk12@medbook.com`
    13. Khoa Da liễu: `pk13@medbook.com`
    14. Khoa Cấp cứu: `pk14@medbook.com`

*Lưu ý: Bạn cũng có thể dùng số điện thoại từ `0917500001` đến `0917500012` để đăng nhập.*

### 3. Vai trò Quản trị viên (Màu Cam)
*   **Tài khoản**: `admin@medbook.com` (hoặc `0000000000`)
*   **Mật khẩu**: `123y`

---
## 🧪 Thư mục `scratch` là gì?
Thư mục `scratch` (trong `backend/scratch`) là nơi chứa các **"kịch bản nháp"** hoặc **"kịch bản chạy một lần"**.
*   Nó không phải là code chính của ứng dụng.
*   Nó dùng để: Khởi tạo dữ liệu (Seeding), dọn dẹp database, chạy thử các đoạn code test nhỏ.
*   Ví dụ: `seed_medbook.py` dùng để tạo hàng loạt bác sĩ và lịch hẹn mẫu cho BV MedBook một cách tự động.

---
*Chúc bạn có trải nghiệm tốt với dự án MedBook!*
