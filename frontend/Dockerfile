# Sử dụng Nginx Alpine image siêu nhẹ
FROM nginx:alpine

# Xóa trang mặc định của Nginx
RUN rm -rf /usr/share/nginx/html/*

# Tạo thư mục /frontend để giữ nguyên cấu trúc đường dẫn tĩnh giống localhost:5500/frontend
WORKDIR /usr/share/nginx/html/frontend

# Copy toàn bộ nội dung thư mục frontend hiện tại vào container
COPY . .

# Mở cổng 80 của Nginx
EXPOSE 80
