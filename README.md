# 🎓 TDTU Q&A System

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React"/>
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite"/>
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
</p>

---

## 📖 Giới thiệu

**TDTU Q&A System** là hệ thống hỏi đáp thông minh dành cho sinh viên Trường Đại học Tôn Đức Thắng, được xây dựng dựa trên công nghệ **Retrieval-Augmented Generation (RAG)** kết hợp với **Large Language Model (LLM)**.

### 🔑 Điểm nổi bật
- 🤖 **AI-powered**: Sử dụng LLM (OpenAI/Gemini) để sinh câu trả lời tự nhiên
- 🔍 **RAG Pipeline**: Tìm kiếm ngữ nghĩa với Vietnamese Embedding + Cross-Encoder reranking
- 📄 **Document Processing**: Xử lý tài liệu PDF, chunking thông minh, OCR hỗ trợ
- 🏫 **Multi-tenant**: Hỗ trợ phân quyền theo khoa/phòng ban
- 📊 **Analytics**: Thống kê câu hỏi phổ biến, feedback từ người dùng
- 🔐 **SSO Integration**: Tích hợp đăng nhập qua hệ thống ELIT của TDTU

### 🛠️ Tech Stack
| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 19, Vite, Material-UI |
| **Backend** | FastAPI, Python 3.11+ |
| **Databases** | MongoDB (metadata), ChromaDB (vector store) |
| **AI/ML** | Sentence Transformers, Cross-Encoder, OpenAI/Gemini API |
| **Infrastructure** | Docker, Docker Compose |

---

## 📁 Cấu trúc thư mục

```
tdtu-qa-system/
├── 📄 docker-compose.dev.yml      # Docker Compose cho môi trường dev
├── 📄 docker-compose.prod.yml     # Docker Compose cho môi trường production
├── 📄 .env                        # Biến môi trường (Backend)
├── 📄 README.md
│
├── 📂 backend/                    # Backend API (FastAPI)
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   ├── requirements.txt
│   └── 📂 app/
│       ├── main.py               # Entry point
│       ├── 📂 controllers/       # Business logic handlers
│       ├── 📂 routes/            # API route definitions
│       ├── 📂 services/          # Core services (embedding, LLM, QA...)
│       ├── 📂 daos/              # Data Access Objects (MongoDB queries)
│       ├── 📂 schemas/           # Pydantic models
│       ├── 📂 databases/         # Database connections (MongoDB, ChromaDB)
│       └── 📂 utils/             # Utility functions
│
├── 📂 frontend/                   # Frontend (React + Vite)
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   ├── nginx.conf                # Nginx config cho production
│   ├── package.json
│   └── 📂 src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── 📂 api/               # Axios API instances
│       ├── 📂 components/        # React components
│       │   ├── ChatPage.jsx      # Trang chat chính
│       │   ├── Sidebar.jsx       # Sidebar navigation
│       │   └── 📂 admin/         # Admin dashboard components
│       ├── 📂 hooks/             # Custom React hooks
│       └── 📂 utils/             # Helper functions
│
├── 📂 hf_cache/                   # Cache HuggingFace models (mounted volume)
└── 📂 uploads/                    # Uploaded documents (mounted volume)
```

---

## ⚡ Tổng quan chức năng

### 👨‍🎓 Dành cho Sinh viên
| Chức năng | Mô tả |
|-----------|-------|
| 💬 **Hỏi đáp AI** | Đặt câu hỏi và nhận câu trả lời từ hệ thống AI |
| 📜 **Lịch sử chat** | Xem lại các cuộc hội thoại trước đó |
| 👍👎 **Feedback** | Đánh giá chất lượng câu trả lời |
| 📄 **Xem tài liệu** | Truy cập tài liệu quy chế, hướng dẫn |
| ❓ **FAQ** | Xem câu hỏi thường gặp |

### 👨‍💼 Dành cho Admin / Faculty Manager
| Chức năng | Mô tả |
|-----------|-------|
| 📤 **Quản lý tài liệu** | Upload, chỉnh sửa, xóa tài liệu PDF |
| 📊 **Dashboard** | Xem thống kê câu hỏi, feedback |
| 👥 **Quản lý người dùng** | Phân quyền, ban/unban user |
| 🔑 **Quản lý API Keys** | Thêm/sửa/xóa API keys cho LLM |
| 📝 **Quản lý Chunks** | Xem và chỉnh sửa potential questions |
| ✅ **Phản hồi thủ công** | Trả lời các câu hỏi có feedback tiêu cực |
| 📈 **Câu hỏi phổ biến** | Phân tích và hiển thị câu hỏi hay gặp |

---

## 🌐 API Endpoints

Tất cả API đều có prefix `/api`. 

### 🔐 Authentication (`/api/auth`)
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `POST` | `/verify` | Xác thực đăng nhập qua ELIT SSO |
| `GET` | `/me` | Lấy thông tin user hiện tại |
| `POST` | `/refresh` | Refresh access token |

### 👥 Users (`/api/users`)
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| `GET` | `/` | Admin | Danh sách users (phân trang) |
| `GET` | `/roles` | Admin | Lấy danh sách roles |
| `GET` | `/faculties` | Admin | Lấy danh sách khoa |
| `GET` | `/{user_id}` | Admin | Chi tiết user |
| `PATCH` | `/{user_id}` | Admin | Cập nhật user |
| `DELETE` | `/{user_id}` | Admin | Xóa user |

### 📄 Documents (`/api/documents`)
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| `POST` | `/upload` | Admin | Upload tài liệu PDF |
| `POST` | `/upload-appendix` | Admin | Upload phụ lục (bảng biểu) |
| `GET` | `/general` | User | Danh sách tài liệu chung |
| `GET` | `/faculty` | User | Tài liệu theo khoa |
| `GET` | `/{doc_id}` | User | Chi tiết tài liệu |
| `PATCH` | `/{doc_id}` | Admin | Cập nhật tài liệu |
| `DELETE` | `/{doc_id}` | Admin | Xóa tài liệu |

### 📑 Document Chunks (`/api/document-chunks`)
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| `GET` | `/{doc_id}` | Admin | Lấy chunks của document |
| `POST` | `/{doc_id}/chunks/{index}/potential-questions` | Admin | Thêm potential question |
| `DELETE` | `/{doc_id}/chunks/{index}/potential-questions/{q_index}` | Admin | Xóa potential question |

### 💬 Q&A (`/api/qa`)
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| `POST` | `/ask` | User | Đặt câu hỏi cho AI |
| `POST` | `/feedback/{record_id}` | User | Gửi feedback |
| `GET` | `/history` | User | Lịch sử câu hỏi của user |
| `GET` | `/all` | Admin | Tất cả câu hỏi |
| `GET` | `/{record_id}` | Admin | Chi tiết câu hỏi |
| `PATCH` | `/{record_id}` | Admin | Cập nhật (thêm manager answer) |

### 📊 Statistics (`/api/statistics`)
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| `GET` | `/generate-popular-questions` | Admin | Tạo thống kê câu hỏi phổ biến |
| `GET` | `/popular-questions` | Admin | Lấy danh sách câu hỏi phổ biến |
| `GET` | `/popular-questions-student` | User | Câu hỏi phổ biến cho sinh viên |
| `PATCH` | `/{record_id}` | Admin | Cập nhật hiển thị |

### 🔑 Model/API Keys (`/api/model`)
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| `POST` | `/api-keys` | Admin | Tạo API key mới |
| `GET` | `/api-keys` | Admin | Danh sách API keys |
| `GET` | `/api-keys/current` | Admin | API key đang sử dụng |
| `GET` | `/api-keys/{id}` | Admin | Chi tiết API key |
| `PATCH` | `/api-keys/{id}` | Admin | Cập nhật API key |
| `DELETE` | `/api-keys/{id}` | Admin | Xóa API key |

### 🧬 Embeddings (`/api/embeddings`)
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| `GET` | `/` | Admin | Lấy embedding vectors |
| `POST` | `/recreate` | Admin | Tạo lại embeddings |
| `DELETE` | `/reset` | Admin | Xóa toàn bộ embeddings |

---

## ⚙️ Cấu hình biến môi trường

### 📄 File `.env` (Backend - thư mục gốc)

Tạo file `.env` tại **thư mục gốc** của project:

```env
# ═══════════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════
MONGO_URL=mongodb://tdtu_qa_mongodb:27017
MONGO_DB_NAME=tdtu_qa_db

CHROMA_HOST=tdtu_qa_chromadb
CHROMA_PORT=8000

# ═══════════════════════════════════════════════════════════
# AI/ML MODELS
# ═══════════════════════════════════════════════════════════
# Vietnamese embedding model (SentenceTransformer)
EMBEDDING_MODEL=dangvantuan/vietnamese-embedding

# Translation model (Vietnamese ↔ English)
TRANSLATE_MODEL=VietAI/envit5-translation

# Cross-encoder for reranking
CROSS_ENCODER_MODEL=cross-encoder/mmarco-mMiniLMv2-L12-H384-v1

# ═══════════════════════════════════════════════════════════
# AUTHENTICATION (JWT)
# ═══════════════════════════════════════════════════════════
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_EXPIRATION_TIME_MINUTES=30
REFRESH_EXPIRATION_TIME_DAYS=7

# ═══════════════════════════════════════════════════════════
# ELIT SSO INTEGRATION (TDTU Login)
# ═══════════════════════════════════════════════════════════
ELIT_CLIENT_ID=your_elit_client_id
ELIT_CLIENT_SECRET=your_elit_client_secret
ELIT_CALLBACK_URL=http://localhost:5173/callback
ELIT_AUTH_BASE=https://sso.tdtu.edu.vn
```

### 📄 File `.env` cho Frontend (trong `docker-compose.dev.yml`)

Các biến môi trường frontend được định nghĩa trong `docker-compose.dev.yml`:

```yaml
environment:
  - VITE_API_BASE=/api
  - VITE_CLIENT_ID=${ELIT_CLIENT_ID}
  - VITE_CALLBACK_URL=${ELIT_CALLBACK_URL}
  - VITE_AUTH_URL=${ELIT_AUTH_BASE}/oauth2/v1/authorize
```

> ⚠️ **Lưu ý**: Frontend sẽ đọc biến `ELIT_*` từ file `.env` gốc thông qua Docker Compose.

---

## 🐳 Hướng dẫn sử dụng Docker

### 📋 Yêu cầu
- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **RAM** >= 8GB (khuyến nghị 16GB cho ML models)

### 🚀 Khởi chạy môi trường Development

```powershell
# 1. Clone repository
git clone https://github.com/your-username/tdtu-qa-system.git
cd tdtu-qa-system

# 2. Tạo file .env (copy từ template và chỉnh sửa)
cp .env.example .env

# 3. Khởi động tất cả services
docker-compose -f docker-compose.dev.yml up -d --build

# 4. Xem logs (optional)
docker-compose -f docker-compose.dev.yml logs -f
```

### 🌐 Truy cập các services

| Service | URL | Mô tả |
|---------|-----|-------|
| **Frontend** | http://localhost:5173 | React app (Vite dev server) |
| **Backend API** | http://localhost:8000 | FastAPI với Swagger UI tại `/docs` |
| **MongoDB** | mongodb://localhost:27020 | Kết nối qua Compass |
| **ChromaDB** | http://localhost:8001 | Vector database HTTP API |

### 📝 Các lệnh Docker thường dùng

```powershell
# Xem logs của từng service
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend

# Restart một service
docker-compose -f docker-compose.dev.yml restart backend

# Dừng tất cả services
docker-compose -f docker-compose.dev.yml down

# Dừng và xóa volumes (⚠️ MẤT DỮ LIỆU)
docker-compose -f docker-compose.dev.yml down -v

# Rebuild một service cụ thể
docker-compose -f docker-compose.dev.yml up -d --build backend

# Vào shell của container
docker exec -it tdtu_qa_backend bash
docker exec -it tdtu_qa_frontend sh
```

### 🏭 Chạy môi trường Production

```powershell
# Build và chạy production
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 📝 Ghi chú thêm

### Cài đặt dependencies mới cho Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate

# Cài package mới
pip install <package-name>

# Export ra requirements.txt
pip freeze > requirements.txt
```

### Lần đầu chạy
1. Hệ thống sẽ tự động download các model HuggingFace (có thể mất 5-10 phút)
2. Models được cache tại `./hf_cache/` để tái sử dụng
3. Cần thêm ít nhất 1 API key (OpenAI/Gemini) qua Admin dashboard để sử dụng tính năng Q&A

---