# TDTU Q&A System
Hệ thống hỏi đáp thông minh cho sinh viên Đại học Tôn Đức Thắng sử dụng FastAPI, MongoDB, ChromaDB và React.

#   1. Setup Backend (Python + FastAPI)
##  1.1 Tạo Virtual Environment
```bash
# Di chuyển vào thư mục backend
cd backend
# Tạo virtual environment
python -m venv venv
# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
# Cài đặt dependencies
pip install -r requirements.txt
# Đặt môi trường ảo cho project
Ctrl+Shift+P chọn "Python:Selected Interpreter" và chọn đường dẫn đến file venv vừa tạo xuất hiện trong project.
```

##  1.2. Kiểm tra môi trường
```bash
# Kiểm tra Python version (>= 3.11)
python --version
# Kiểm tra pip packages đã cài
pip list
```

#   2. Setup Docker Environment
##  2.1. Kiểm tra Docker
```bash
# Kiểm tra Docker và Docker Compose đã cài chưa
docker --version
docker-compose --version
```

##  2.2. Tạo file .env (nếu chưa có)
```bash
# Tạo file .env trong thư mục root
# MongoDB
MONGO_URL=mongodb://mongodb:27017
MONGO_DB_NAME=tdtu_qa_db
# ChromaDB
CHROMA_HOST=tdtu_qa_chromadb
CHROMA_PORT=8000
# Models
# EMBEDDING_MODEL=BAAI/bge-m3
# LLM_MODEL=meta-llama/Llama-3.1-8B
```

#   3. Chạy ứng dụng
##  3.1. Chạy với Docker Compose (Khuyến nghị)
```bash
# Về thư mục root của project
cd ..
# BUILD
# 1. Build và chạy tất cả services cho dev
docker-compose -f docker-compose.dev.yml up --build
# 2. Build và chạy tất cả services cho production
docker-compose -f docker-compose.prod.yml up --build

# Hoặc chạy ở background
docker-compose up -d

# STOP
# 1. Dev
docker-compose -f docker-compose.dev.yml down
# 2. Production
docker-compose -f docker-compose.prod.yml down

# Dừng và xóa volumes (reset database)
# 1. Dev
docker-compose -f docker-compose.dev.yml down -v
# 2. Production
docker-compose -f docker-compose.prod.yml down -v
```

##  3.2. Chạy Development Mode (Backend riêng lẻ)
```bash
# Chạy MongoDB và ChromaDB bằng Docker
docker-compose up mongodb chromadb
# Chạy backend ở local (terminal khác)
cd backend
venv\Scripts\activate  # Windows
uvicorn app.main:app --reload
```

#   4. Development Workflow
##  4.1. Thêm dependencies mới
```bash
# Kích hoạt venv
cd backend
venv\Scripts\activate
# Cài package mới
pip install package-name
# Cập nhật requirements.txt
pip freeze > requirements.txt
```

##  4.2. Database Operations
```bash
# Reset database
docker-compose down -v
docker-compose up mongodb
# Backup database (nếu cần)
docker exec tdtu_qa_mongodb mongodump --out /data/backup
# Connect vào MongoDB shell
docker exec -it tdtu_qa_mongodb mongosh
# Connect bằng MongoDB Compass
mongodb://localhost:27018
```

# 5. Ẩn bớt các file không cần thiết hiện lên folder project
```bash
Ctrl + ,
Tìm files:exclude
Chọn Add Pattern và thêm 2 pattern sau:
**/__init__.py
**/__pycache__
```

# 6. Triển khai GPU cho LLM self host
```bash
Tải và cài đặt Cuda toolkit cho máy tùy theo phiên bản tương thích
Trong venv, sử dụng lệnh cài đặt PyTorch tùy theo version cuda tương thích:
pip3 install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cu130 (Version 13)
```