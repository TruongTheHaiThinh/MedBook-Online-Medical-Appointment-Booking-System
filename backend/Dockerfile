# Sử dụng hình ảnh Python chính thức
FROM python:3.12-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các công cụ cần thiết để build (nếu cần)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Sao chép file requirements và cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn
COPY . .

# Chạy server
CMD ["sh", "-c", "alembic upgrade head && python scripts/seed_data.py || true && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
