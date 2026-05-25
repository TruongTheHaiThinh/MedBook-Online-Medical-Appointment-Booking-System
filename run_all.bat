@echo off
chcp 65001 > nul
echo =================================================================
echo             🏥 MedBook - BỘ CÀI ĐẶT & KHỞI CHẠY TỰ ĐỘNG
echo =================================================================
echo.

:: 1. Kiểm tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Không tìm thấy Python trên hệ thống của bạn!
    echo Vui lòng cài đặt Python (từ 3.9 trở lên) và chọn "Add Python to PATH".
    pause
    exit /b 1
)

:: Kiểm tra và tạo môi trường ảo .venv nếu chưa tồn tại
if not exist ".venv\" (
    echo [INFO] Đang tạo môi trường ảo Python (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Không thể tạo môi trường ảo!
        pause
        exit /b 1
    )
    echo [SUCCESS] Tạo môi trường ảo thành công.
)

echo [1/4] Đang cài đặt các thư viện cần thiết vào .venv...
.venv\Scripts\python -m pip install --upgrade pip >nul 2>&1
.venv\Scripts\pip install -r backend/requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Lỗi khi cài đặt thư viện! Vui lòng kiểm tra lại kết nối mạng.
    pause
    exit /b 1
)
echo.

:: 2. Khởi tạo & Seed Database
echo [2/4] Khởi tạo Database và nạp dữ liệu mẫu...
cd backend
..\.venv\Scripts\python scripts/seed_all.py
if %errorlevel% neq 0 (
    echo [WARNING] Có lỗi khi chạy seed_all.py!
    echo Đảm bảo rằng bạn đã cấu hình .env hoặc PostgreSQL chính xác.
    echo Vẫn tiếp tục khởi chạy các server...
)
cd ..
echo.

:: 3. Chạy Backend trong cửa sổ mới
echo [3/4] Đang khởi động Backend Server (Cổng 8000) bằng .venv...
start "MedBook - Backend Server" cmd /k "cd backend && set PYTHONPATH=.&& ..\.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: 4. Chạy Frontend trong cửa sổ mới
echo [4/4] Đang khởi động Frontend Server (Cổng 5500) bằng .venv...
start "MedBook - Frontend Server" cmd /k ".venv\Scripts\python -m http.server 5500"

echo.
echo =================================================================
echo 🎉 MEDBOOK ĐÃ ĐƯỢC KHỞI CHẠY THÀNH CÔNG!
echo.
echo [!] Địa chỉ ứng dụng: http://localhost:5500/frontend/index.html
echo.
echo 🔑 THÔNG TIN TÀI KHOẢN DÙNG THỬ (TEST):
echo -----------------------------------------------------------------
echo 1. Quản lý Nhân sự (HR Admin):
echo    - Email:    admin@medbook.vn
echo    - Mật khẩu: 123y  (hoặc  Admin@123  tùy database)
echo.
echo 2. Thu ngân (Cashier Admin):
echo    - Email:    cashier@medbook.vn
echo    - Mật khẩu: Cashier@123
echo.
echo 3. Bác sĩ (Doctor):
echo    - Email:    pk1@medbook.com (Bác sĩ Tim mạch A - Khoa Tim mạch)
echo    - Email:    vietnam.175@medbook.vn (Nguyễn Việt Nam - Chấn thương Chỉnh hình)
echo    - Mật khẩu: Doctor@123
echo.
echo 4. Bệnh nhân (Patient):
echo    - Email:    patient1@medbook.vn
echo    - Mật khẩu: Patient@123
echo =================================================================
echo.
echo Hệ thống sẽ tự động mở trình duyệt sau 3 giây...
timeout /t 3 >nul
start http://localhost:5500/frontend/index.html
