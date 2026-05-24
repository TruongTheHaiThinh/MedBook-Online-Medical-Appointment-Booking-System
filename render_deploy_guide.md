# 🚀 HƯỚNG DẪN TRIỂN KHAI LÊN CLOUD RENDER BẰNG DOCKER

Tài liệu này hướng dẫn chi tiết cách cấu hình và deploy hệ thống MedBook lên nền tảng **Render (render.com)** sử dụng cấu trúc đóng gói Docker hiện tại.

---

## 🏗️ KIẾN TRÚC TRIỂN KHAI TRÊN RENDER

Hệ thống được thiết kế tối ưu hóa chi phí và hiệu năng khi chạy trên Render:
1. **Database**: Khởi tạo dịch vụ **PostgreSQL** của Render (miễn phí).
2. **Backend**: Triển khai dạng **Web Service (Docker)** bằng cách đọc tệp [backend/Dockerfile](file:///d:/ptud/backend/Dockerfile).
3. **Frontend**: Triển khai dạng **Static Site** (Miễn phí hoàn toàn, tích hợp CDN tải trang siêu tốc) hoặc **Web Service (Docker)** bằng cách đọc tệp [frontend/Dockerfile](file:///d:/ptud/frontend/Dockerfile).

---

## 🛠️ BƯỚC 1: KHỞI TẠO DATABASE POSTGRESQL TRÊN RENDER

1. Truy cập **Render Dashboard** và click **New** -> **PostgreSQL**.
2. Thiết lập các thông số:
   * **Name**: `medbook-db`
   * **Database**: `medbook`
   * **User**: `postgres`
   * **Region**: Chọn Singapore hoặc Oregon (nên chọn cùng vùng với Backend để giảm độ trễ).
3. Click **Create Database**.
4. Sau khi tạo xong, tìm mục **Connections**:
   * Sao chép đường dẫn **Internal Database URL** (để Backend gọi nội bộ trong Render). Ví dụ: `postgres://postgres:password@dpg-xxx-a.singapore-postgres.render.com/medbook`
   * Thay thế giao thức đầu từ `postgres://` thành `postgresql+asyncpg://` (để SQLAlchemy Async tương thích).
     * *Đường dẫn cuối cùng sẽ có dạng:* `postgresql+asyncpg://postgres:password@dpg-xxx-a.singapore-postgres.render.com/medbook`

---

## 📡 BƯỚC 2: DEPLOY BACKEND WEB SERVICE (DOCKER)

1. Trên Render Dashboard, click **New** -> **Web Service**.
2. Kết nối tới tài khoản GitHub chứa mã nguồn đồ án của bạn.
3. Cấu hình dịch vụ Backend:
   * **Name**: `medbook-backend`
   * **Region**: Chọn cùng vùng với Database.
   * **Branch**: `main` (hoặc nhánh chứa code của bạn).
   * **Root Directory**: `backend` *(Rất quan trọng - Render sẽ tự động chạy trong thư mục này).*
   * **Runtime**: Chọn **Docker** *(Render sẽ tự nhận diện và build [backend/Dockerfile](file:///d:/ptud/backend/Dockerfile)).*
4. Click **Advanced** và thêm các **Environment Variables (Biến môi trường)**:
   * `DATABASE_URL` = `<Đường dẫn Internal Database URL có tiền tố postgresql+asyncpg:// đã copy ở Bước 1>`
   * `SECRET_KEY` = `<Một chuỗi ký tự ngẫu nhiên bảo mật>`
   * `FRONTEND_URL` = `<Địa chỉ trang web Frontend sau khi deploy - điền tạm thời và cập nhật sau ở Bước 3>`
5. Click **Create Web Service**. Render sẽ tiến hành build image Docker và khởi chạy server.
6. Khi hoàn tất, sao chép địa chỉ URL của Backend vừa tạo (ví dụ: `https://medbook-backend.onrender.com`).

---

## 🎨 BƯỚC 3: DEPLOY FRONTEND

Bạn có 2 lựa chọn deploy phù hợp với nhu cầu:

### LỰA CHỌN A: Deploy dạng Static Site (KHUYÊN DÙNG - MIỄN PHÍ & NHANH)
Vì Frontend của MedBook là các trang web tĩnh (HTML/CSS/JS thuần), deploy dạng Static Site trên Render sẽ được **miễn phí hoàn toàn vĩnh viễn** và tải trang cực nhanh.

1. Trên Render Dashboard, click **New** -> **Static Site**.
2. Chọn repo GitHub chứa code của bạn.
3. Thiết lập thông số:
   * **Name**: `medbook-app`
   * **Root Directory**: `frontend`
   * **Build Command**: Để trống.
   * **Publish Directory**: `.`
4. Click **Create Static Site**.
5. Sau khi thành công, bạn sẽ nhận được địa chỉ của Frontend (ví dụ: `https://medbook-app.onrender.com`).

### LỰA CHỌN B: Deploy dạng Web Service sử dụng Docker
Nếu bạn muốn sử dụng máy chủ Nginx được đóng gói trong container Docker của bạn:

1. Click **New** -> **Web Service**.
2. Chọn repo GitHub của bạn.
3. Thiết lập thông số:
   * **Name**: `medbook-frontend`
   * **Root Directory**: `frontend`
   * **Runtime**: Chọn **Docker** *(Render sẽ build [frontend/Dockerfile](file:///d:/ptud/frontend/Dockerfile)).*
4. Click **Create Web Service**.

---

## 🔄 BƯỚC 4: ĐỒNG BỘ ĐỊA CHỈ & NẠP DỮ LIỆU MẪU (FINAL SYNC)

Sau khi có cả 2 địa chỉ Public URL của Backend và Frontend:

### 1. Đồng bộ CORS phía Backend:
* Vào Dashboard của Backend Web Service trên Render -> **Environment**.
* Cập nhật lại giá trị biến `FRONTEND_URL` chính xác bằng địa chỉ URL Frontend của bạn (ví dụ: `https://medbook-app.onrender.com`).
* Render sẽ tự động restart lại Backend để nhận cấu hình CORS mới.

### 2. Đồng bộ API Gọi Đến phía Frontend:
* Trong mã nguồn của bạn ở file [config.js](file:///d:/ptud/frontend/js/config.js), hãy đảm bảo URL của Render được cập nhật chính xác ở phần fallback:
  ```javascript
  const CONFIG = {
      API_URL: (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
          ? 'http://127.0.0.1:8000'
          : 'https://medbook-backend.onrender.com', // Thay thế bằng URL Backend thực tế của bạn trên Render
  };
  ```
  *(Các file HTML tự động nhận diện tương tự để đảm bảo khi chạy offline/local hay online đều hoạt động tự động).*

### 3. Nạp dữ liệu mẫu vào database trên Render:
Để nạp dữ liệu mẫu vào PostgreSQL của Render, mở terminal trên máy của bạn và chạy lệnh sau từ thư mục `backend`:
```powershell
# Chạy script kết nối trực tiếp đến database cloud để nạp dữ liệu
$env:DATABASE_URL="<Đường dẫn External Database URL của Render PostgreSQL>"
python scripts/seed_all.py
```
*(Bạn có thể lấy đường dẫn **External Database URL** trong phần cấu hình PostgreSQL của Render để thực hiện nạp dữ liệu từ máy cá nhân lên Cloud).*

---

## 🏆 KẾT QUẢ ĐẠT ĐƯỢC
Hệ thống sẽ chạy hoàn hảo, tự động nhận diện và chuyển đổi thông minh:
* Khi chạy ở máy cục bộ của bạn hoặc của thầy giáo: Tự động kết nối tới API local (`127.0.0.1:8000`).
* Khi deploy lên Cloud: Tự động kết nối tới API Render (`https://medbook-backend.onrender.com`) mà không bị dính bất kỳ lỗi CORS hay DNS nào.
