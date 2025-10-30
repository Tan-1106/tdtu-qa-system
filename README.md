# TDTU Q&A System
Hệ thống hỏi đáp cho sinh viên Trường ĐH Tôn Đức Thắng, xây dựng trên FastAPI (backend), React + Vite + Nginx (frontend), MongoDB và ChromaDB.

## Mục lục
- Giới thiệu & cấu trúc dự án
- Yêu cầu hệ thống
- Biến môi trường (.env)
- Chạy môi trường Dev (Docker Compose)
- Chạy môi trường Prod (Docker Compose)
- Dừng/dọn dẹp dịch vụ
- Chạy backend local (tùy chọn)
- Quản lý dependencies

---

## Giới thiệu & cấu trúc dự án

```
tdtu-qa-system/
├─ docker-compose.dev.yml
├─ docker-compose.prod.yml
├─ README.md
├─ .dockerignore                  # dùng cho build prod (context = repo root)
├─ backend/
│  ├─ Dockerfile.dev             # dev: uvicorn --reload, không COPY code
│  ├─ Dockerfile.prod            # prod: COPY code vào image, uvicorn workers
│  ├─ Dockerfile                 # (dev-compatible; không bắt buộc dùng)
│  ├─ .dockerignore              # dev: loại trừ app/ để build nhanh (dùng volumes)
│  ├─ requirements.txt
│  └─ app/
│     ├─ main.py
│     ├─ controllers/ routes/ services/ daos/ schemas/ databases/ utils/
├─ frontend/
│  ├─ Dockerfile.dev             # dev: Vite dev server (port 5173)
│  ├─ Dockerfile.prod            # prod: build dist + Nginx serve (port 80)
│  ├─ .dockerignore
│  ├─ nginx.conf                 # proxy /api → backend:8000 trong prod
│  └─ src/ public/ ...
├─ hf_cache/                     # cache models (được mount volume)
└─ uploads/                      # lưu file upload (được mount volume)
```

## Yêu cầu hệ thống
- Docker Desktop + Docker Compose
- Python 3.11 (nếu chạy backend local)

Kiểm tra cài đặt:
```powershell
docker --version
docker-compose --version
```

## Biến môi trường (.env)
Tạo file `.env` ở repo root (đã được load bởi backend):
```
GPT_KEY=...
GPT_MODEL=...
EMBEDDING_MODEL=...
# Tuỳ chọn khác nếu bạn có:
# MONGODB_URI=mongodb://mongodb:27017
# CHROMA_HOST=chromadb
# CHROMA_PORT=8000
```

---

## Chạy môi trường Dev (Docker Compose)
Mặc định dùng hot-reload cho cả FE/BE.

```powershell
# Từ thư mục repo root
docker-compose -f docker-compose.dev.yml up -d --build
```

URL dev:
- Frontend (Vite): http://localhost:5173/
- Backend API (FastAPI): http://localhost:8000/
- MongoDB: localhost:27018 (Compass URI: mongodb://localhost:27018)
- ChromaDB HTTP: http://localhost:8001/

Ghi chú dev:
- Backend dev mount code: `./backend/app:/app/app` (không COPY code khi build)
- Frontend dev chạy Vite server, mount `./frontend:/app`
- Windows đã bật polling để hot-reload ổn định

---

## Chạy môi trường Prod (Docker Compose)
Prod sẽ “đóng gói” mã nguồn vào image, không mount code.

```powershell
docker-compose -f docker-compose.prod.yml up -d --build
```

URL prod:
- Frontend (Nginx): http://localhost/
- Backend API (Uvicorn): http://localhost:8000/

Ghi chú prod:
- Frontend Dockerfile.prod: build dist và serve qua Nginx; proxy `/api` → `backend:8000`
- Backend Dockerfile.prod: COPY `backend/app` vào image, chạy uvicorn nhiều workers
- Volumes dữ liệu được giữ lại: `uploads`, `mongo_data`, `chroma_data`, `hf_cache`

---

## Dừng/dọn dẹp dịch vụ
```powershell
# Dev
docker-compose -f docker-compose.dev.yml down
# Dev (xóa cả volumes: MẤT DỮ LIỆU)
docker-compose -f docker-compose.dev.yml down -v

# Prod
docker-compose -f docker-compose.prod.yml down
# Prod (xóa cả volumes: MẤT DỮ LIỆU)
docker-compose -f docker-compose.prod.yml down -v
```

Xem log live:
```powershell
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend
```

---

## Chạy backend local (tuỳ chọn, không Docker)
```powershell
# Chạy MongoDB & ChromaDB bằng Docker (terminal 1)
docker-compose -f docker-compose.dev.yml up mongodb chromadb

# Chạy backend local (terminal 2)
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Quản lý dependencies (backend)
Thêm package mới và cập nhật requirements:
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install <package>
python -m pip freeze | Out-File -Encoding UTF8 requirements.txt
```

---
