# 🏥 MedBook - Hướng dẫn khởi chạy nhanh

Tài liệu này hướng dẫn cách chạy ứng dụng MedBook hàng ngày.

---

## ⚡ BƯỚC 1: KHỞI CHẠY HÀNG NGÀY (THÔNG THƯỜNG)
Bạn chỉ cần thực hiện các bước này để bắt đầu làm việc. Mọi dữ liệu bạn đã sửa sẽ được **LƯU VĨNH VIỄN**.

### 1. Khởi chạy Backend (API)
Mở Terminal 1 và nhập:
```powershell
cd backend
$env:PYTHONPATH="."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Khởi chạy Frontend (Giao diện)
Mở Terminal 2 (đứng ở thư mục gốc của dự án) và nhập:
```powershell
python -m http.server 5500
```

### 3. Truy cập ứng dụng
*   **Trang chủ:** [http://localhost:5500/frontend/index.html](http://localhost:5500/frontend/index.html)
*   **Tài khoản Bệnh nhân:** `patient1@medbook.vn` / `Patient@123`
*   **Tài khoản Bác sĩ:** `pk1@medbook.com` / `Doctor@123`

---

## 🛠️ CÀI ĐẶT LẦN ĐẦU (CHỈ CHẠY 1 LẦN)
> [!CAUTION]
> **CẢNH BÁO QUAN TRỌNG:** Lệnh `python -m app.seed` sẽ thực hiện **XÓA TOÀN BỘ DỮ LIỆU HIỆN CÓ** (TRUNCATE) trong Database trước khi nạp dữ liệu mẫu. **CHỈ CHẠY KHI BẠN MUỐN RESET LẠI HỆ THỐNG.**

1.  **Cài đặt thư viện:** `pip install -r backend/requirements.txt`
2.  **Khởi tạo Database & Dữ liệu mẫu (Cho người mới clone):** 
    ```powershell
    cd backend
    python seed_all.py
    ```

---

## 💎 Tính năng Cao cấp mới cập nhật
*   **Hồ sơ Bệnh nhân Chi tiết**: Lưu trữ Ngày sinh, Giới tính, Nhóm máu.
*   **Dashboard Bác sĩ Thông minh**: Tự động hiển thị tóm tắt lâm sàng.
*   **Đồng bộ thời gian thực**: Cập nhật thông tin mượt mà.
