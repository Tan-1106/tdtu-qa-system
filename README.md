# TDTU Q&A System
Hệ thống hỏi đáp cho sinh viên Trường ĐH Tôn Đức Thắng, xây dựng trên FastAPI (backend), React + Vite (frontend), MongoDB và ChromaDB.

---

## Cấu trúc dự án

```
tdtu-qa-system/
├─ docker-compose.dev.yml
├─ docker-compose.prod.yml
├─ README.md
├─ backend/
│  ├─ Dockerfile.dev
│  ├─ Dockerfile.prod
│  ├─ requirements.txt
│  └─ app/
│     ├─ main.py
│     ├─ controllers/
│     ├─ routes/
│     ├─ services/
│     ├─ daos/
│     ├─ schemas/
│     ├─ databases/
│     └─ utils/
├─ frontend/
│  ├─ Dockerfile.dev
│  ├─ Dockerfile.prod
│  ├─ nginx.conf
│  └─ src/ public/
├─ hf_cache/          # cache mô hình HuggingFace (được mount vào backend)
└─ uploads/           # nơi lưu file upload (được mount vào backend)
```

---

## Biến môi trường (.env)
Tạo file `.env` ở thư mục gốc repo. Backend sẽ đọc các biến sau:

```
# OpenAI / LLM
GPT_KEY=your_openai_key
GPT_5_NANO=gpt-…      # model dùng để sinh câu hỏi (create_questions)
GPT_5_MINI=gpt-…      # model dùng để sinh câu trả lời (generate_answer)

# Embedding + Dịch máy
EMBEDDING_MODEL=dangvantuan/vietnamese-embedding   # SentenceTransformer
TRANSLATE_MODEL=VietAI/envit5-translation          # HuggingFace seq2seq

# MongoDB
MONGO_URL=mongodb://mongodb:27017                   # mặc định theo docker-compose.dev.yml
MONGO_DB_NAME=tdtu_qa_db

# ChromaDB (vector store)
CHROMA_HOST=tdtu_qa_chromadb                        # trùng container_name dịch vụ chromadb
CHROMA_PORT=8000

# JWT/Auth
SECRET_KEY=your_secret
ALGORITHM=HS256
ACCESS_EXPIRATION_TIME_MINUTES=5
REFRESH_EXPIRATION_TIME_DAYS=7
```

---

## Docker môi trường Dev
Chạy hot-reload cho cả frontend và backend.

```powershell
# Khởi động (từ repo root)
docker-compose -f docker-compose.dev.yml up -d --build

# Xem log
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend

# Dừng dịch vụ
docker-compose -f docker-compose.dev.yml down

# Dọn dẹp cả volumes (MẤT DỮ LIỆU DB/CHROMA/UPLOADS)
docker-compose -f docker-compose.dev.yml down -v
```

Service/Ports (dev):
- Frontend (Vite): http://localhost:5173/
- Backend API (FastAPI): http://localhost:8000/
- MongoDB (Compass): mongodb://localhost:27020
- ChromaDB HTTP: http://localhost:8001/ (proxy đến container port 8000)

---

## Về file requirements (backend)
File: `backend/requirements.txt`. Để bổ sung/chốt phiên bản dependencies:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate

# Cài thêm gói mới
pip install <package>

# Cập nhật requirements.txt từ môi trường hiện tại
python -m pip freeze | Out-File -Encoding UTF8 requirements.txt
```

Trong Docker dev, backend sẽ cài đặt dependencies theo `requirements.txt` khi build image.

---

## API Routes (Backend)
Tất cả routes đều được mount dưới prefix `/api`.

### Authentication (`auth_route`)
- `POST /api/auth/register`: Đăng ký tài khoản mới.
- `POST /api/auth/login`: Đăng nhập, trả `access_token` và `refresh_token`.
- `GET /api/auth/me`: Lấy thông tin người dùng hiện tại.
- `POST /api/auth/refresh`: Cấp lại cặp access/refresh token.

### Users (`user_route`)
- `(Admin) GET /api/users/`: Lấy danh sách người dùng.
- `(Admin) POST /api/users/search`: Tìm người dùng theo email (body: EmailLookup).
- `(Admin) GET /api/users/{user_id}`: Lấy chi tiết người dùng theo ID.
- `(Admin) PATCH /api/users/{user_id}`: Cập nhật thông tin người dùng.
- `(Admin) DELETE /api/users/{user_id}`: Xóa người dùng.
- `(User) PATCH /api/users/me`: Cập nhật thông tin của chính mình.

### Documents (`document_route`)
- `(Admin) GET /api/documents/{doc_id}/chunks/{chunk_index}`: Lấy nội dung một chunk theo doc_id và index.
- `(Admin) PATCH /api/documents/{doc_id}`: Cập nhật tài liệu.
- `(Admin) DELETE /api/documents/{doc_id}`: Xóa tài liệu.
- `(Admin) POST /api/documents/upload`: Upload tài liệu PDF chính, chunking, tạo embeddings, clustering.
- `(Admin) POST /api/documents/upload-appendix`: Upload tài liệu phụ lục (bảng), chunking đặc thù, embeddings.
- `(User) GET /api/documents/`: Danh sách tài liệu (phân trang, lọc `type`, `department`).
- `(User) GET /api/documents/view/{doc_id}`: Xem file PDF inline.
- `(User) GET /api/documents/{doc_id}`: Lấy chi tiết tài liệu.

### Potential Questions (`potential_question_route`) — Admin
- `GET /api/potential-questions/`: Lấy tất cả potential questions.
- `GET /api/potential-questions/{doc_id}/chunks/{chunk_index}`: Lấy potential questions theo chunk.
- `POST /api/potential-questions/{doc_id}/chunks/{chunk_index}`: Thêm potential question cho chunk.
- `PUT /api/potential-questions/{doc_id}/chunks/{chunk_index}/questions/{question_index}`: Cập nhật một potential question.
- `DELETE /api/potential-questions/{doc_id}/chunks/{chunk_index}/questions/{question_index}`: Xóa một potential question.

### Questions (`question_route`)
- `(Admin) GET /api/questions/`: Lấy danh sách câu hỏi.
- `(Admin) GET /api/questions/{question_id}`: Lấy chi tiết câu hỏi.
- `(User) POST /api/questions/query`: Đặt câu hỏi (RAG + LLM trả lời).
- `(User) POST /api/questions/{question_id}/feedback`: Gửi feedback cho câu trả lời.

### Question Embeddings (`question_embedding_route`) — Admin
- `GET /api/question-embeddings/`: Lấy danh sách embeddings.
- `GET /api/question-embeddings/export`: Xuất embeddings (JSON) để tải về.
- `POST /api/question-embeddings/import`: Import embeddings từ file JSON.
- `GET /api/question-embeddings/{embedding_id}`: Lấy chi tiết một embedding.
- `POST /api/question-embeddings/`: Tạo embedding (mục đích test).
- `DELETE /api/question-embeddings/{embedding_id}`: Xóa một embedding.
- `DELETE /api/question-embeddings/`: Xóa toàn bộ embeddings (reset collection).

### Prototypes (`prototype_route`) — Admin
- `GET /api/prototypes/`: Lấy danh sách prototypes (cụm/centroid).
- `GET /api/prototypes/{prototype_id}`: Lấy chi tiết một prototype.
- `POST /api/prototypes/`: Tạo prototype (mục đích test).
- `POST /api/prototypes/cluster`: Gom cụm embeddings thành prototypes (HDBSCAN).
- `DELETE /api/prototypes/`: Xóa/reset toàn bộ prototypes.  