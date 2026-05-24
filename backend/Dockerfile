# Sử dụng Python image chính thức, dung lượng nhẹ
FROM python:3.11-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết (để cài đặt psycopg2/asyncpg mượt mà)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements và cài đặt python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn backend vào container
COPY . .

# Xóa .env nếu bị copy vào — biến môi trường Render Dashboard sẽ được dùng thay thế
RUN rm -f .env


# Mở cổng 8000 của container
EXPOSE 8000

# Khởi chạy server FastAPI sử dụng uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
