# CampusAI — KPRIET Campus Assistant

A full-stack RAG (Retrieval-Augmented Generation) chatbot system for campus information, featuring separate **Student/Guest** and **Admin** portals, JWT-based authentication, role-based access control (RBAC), and a **100% automated, zero-touch Docker deployment pipeline** with persistent local LLM and embedding model management.

---

## 📑 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Key Features & Model Management](#key-features--model-management)
3. [Quick Start (Docker Compose)](#quick-start-docker-compose)
4. [Service Ports & Endpoints](#service-ports--endpoints)
5. [Authentication & RBAC](#authentication--rbac)
6. [How to Add the First Admin](#how-to-add-the-first-admin)
7. [How Students Get Access](#how-students-get-access)
8. [Running Locally for Development](#running-locally-for-development)
9. [Environment Variables](#environment-variables)
10. [API Reference](#api-reference)
11. [Troubleshooting & FAQ](#troubleshooting--faq)

---

## Architecture Overview

```
                                  ┌──────────────────────────┐
                                  │      Host (Browser)      │
                                  └─────────────┬────────────┘
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼ (Port 5173)                                                 ▼ (Port 5174)
   ┌───────────────────────────┐                                 ┌───────────────────────────┐
   │   frontend-user (Nginx)   │                                 │   frontend-admin (Nginx)  │
   └─────────────┬─────────────┘                                 └─────────────┬─────────────┘
                 │                                                             │
                 └──────────────────────────────┬──────────────────────────────┘
                                                │ proxy_pass /api/ (Dynamic DNS)
                                                ▼ (Port 8000)
                                 ┌─────────────────────────────┐
                                 │       FastAPI Backend       │
                                 └──────────────┬──────────────┘
                                                │
         ┌───────────────────────┬──────────────┼───────────────────────┬───────────────────────┐
         ▼                       ▼              ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐ ┌─────────┐    ┌───────────────────┐    ┌─────────────────┐
│     MongoDB     │    │      MinIO      │ │ Qdrant  │    │      Ollama       │    │  Hugging Face   │
│  (Port 27017)   │    │  (Port 9000)    │ │(Pt 6333)│    │   (Port 11434)    │    │  (Cache Volume) │
│ [mongodb_data]  │    │  [minio_data]   │ │[qdrant] │    │   [ollama_data]   │    │   [hf_cache]    │
└─────────────────┘    └────────┬────────┘ └─────────┘    └─────────┬─────────┘    └─────────────────┘
                                │                                   │
                                ▼                                   ▼
                       ┌─────────────────┐                 ┌─────────────────┐
                       │   createbucket  │                 │   ollama-init   │
                       │  (MinIO Init)   │                 │ (Model Puller)  │
                       └─────────────────┘                 └─────────────────┘
```

---

## Key Features & Model Management

### 1. Automated Model Containerization & Persistence
- **Ollama LLM Server**: Runs locally inside Docker with GPU acceleration fallback. Configured with model **`qwen3.5:4b`** (or configurable via `OLLAMA_MODEL` in `.env`).
- **`ollama-init` Service**: Automatically polls the Ollama container on boot, checks if `qwen3.5:4b` exists in the persistent `ollama_data` volume, and **only downloads it if missing**. Subsequent restarts and rebuilds skip downloading.
- **Hugging Face Embedding Cache (`hf_cache`)**: The multilingual embedding model (`BAAI/bge-m3`) is stored in a persistent Docker volume (`hf_cache`), loaded offline-first (`local_files_only=True`), eliminating repeated gigabyte downloads.

### 2. Resilient Startup Synchronization
- **Nginx Dynamic DNS**: Both user and admin Nginx configs utilize Docker's internal DNS resolver (`127.0.0.11`) to prevent container crashes if the backend is initializing or restarting.
- **MinIO Health & Bucket Setup**: The `createbuckets` init container retries with exponential backoff until MinIO is ready and creates the bucket with `--ignore-existing`.

---

## Quick Start (Docker Compose)

### 1. Clone & Enter Directory
```bash
cd ChatBot
```

### 2. Configure Environment (Optional)
```bash
# A default .env is already included, or copy from example:
cp .env.example .env
```

### 3. Start the Complete Stack
```bash
docker compose up -d --build
```

### 4. Monitor Initialization
```bash
# Follow logs across all containers
docker compose logs -f

# Or monitor model download specifically
docker compose logs -f ollama-init backend
```

---

## Service Ports & Endpoints

| Port | Service | Container Name | Description |
|---|---|---|---|
| **5173** | Frontend User | `campus_assistant_frontend_user` | Student & Guest chat application |
| **5174** | Frontend Admin | `campus_assistant_frontend_admin` | Administrative portal for document & user management |
| **8000** | Backend API | `campus_assistant_backend` | FastAPI REST API & Swagger UI (`/docs`) |
| **11434** | Ollama LLM | `campus_assistant_ollama` | Local LLM server running `qwen3.5:4b` |
| **6333** | Qdrant | `campus_assistant_qdrant` | Vector database for RAG document retrieval |
| **9000** | MinIO API | `campus_assistant_minio` | S3-compatible object storage for uploaded files |
| **9001** | MinIO Console | `campus_assistant_minio` | Object storage web console |
| **27017** | MongoDB | `campus_assistant_mongodb` | Database for users, sessions, chats, and jobs |

---

## Authentication & RBAC

### Token Management
- Authenticated users store JWT tokens in `localStorage` under `campus_ai_token`.
- Admin sessions use `campus_admin_token`.
- Guests receive a transient `campus_guest_session` without requiring credentials.

### Access Levels

| Role | Access Permissions |
|---|---|
| **`guest`** | Public documents only; temporary session (no persistent history across sessions). |
| **`student`** | Public + student-tier documents; full conversation history and summaries. |
| **`faculty`** | Public + student + faculty/department documents. |
| **`admin`** | Full access to all documents, vector search, user management, and system logs. |

---

## How to Add the First Admin

The **Principal Admin account is automatically seeded** on first startup of the backend:

```text
Email    : principal@kpriet.ac.in
Password : 123456
Role     : admin
```

1. Navigate to the Admin Portal: [http://localhost:5174](http://localhost:5174)
2. Log in using `principal@kpriet.ac.in` and `123456`.
3. *(Recommended)* Change the password immediately under account settings or create dedicated admin accounts.

---

## How Students Get Access

**No public self-registration is permitted.** Accounts are managed centrally by administrators:

1. Log in to [http://localhost:5174](http://localhost:5174).
2. Go to **Users** → **Add User**.
3. Fill in:
   - **Full Name**
   - **Email** (e.g. `student@kpriet.ac.in`)
   - **Student ID** (e.g. `22CSEA001`)
   - **Password**
   - **Role** (`student` or `faculty`)
   - **Department**, **Year**, **Section**
4. Click **Create User**.
5. Students can now log in at [http://localhost:5173](http://localhost:5173) using either their **Student ID** or **Email**.

---

## Running Locally for Development

If you prefer to run services individually outside Docker:

### Prerequisites
- Python 3.11+
- Node.js 20+
- MongoDB, Qdrant, MinIO, and Ollama running locally.

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### User Frontend
```bash
cd frontend/apps/user
npm install
npm run dev # http://localhost:5173
```

### Admin Frontend
```bash
cd frontend/apps/admin
npm install
npm run dev # http://localhost:5174
```

---

## Environment Variables

Configured in `.env`:

```env
# ========================================
# DATABASE CONFIGURATION
# ========================================
MONGO_URI=mongodb://mongodb:27017
MONGO_DB_NAME=campus_assistant_db

# ========================================
# STORAGE CONFIGURATION (MINIO)
# ========================================
MINIO_ENDPOINT=minio:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=campus-documents
MINIO_SECURE=false

# ========================================
# VECTOR DATABASE CONFIGURATION (QDRANT)
# ========================================
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=campus_documents

# ========================================
# LLM & EMBEDDING CONFIGURATION
# ========================================
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=qwen3.5:4b
EMBEDDING_MODEL_NAME=BAAI/bge-m3

# ========================================
# SECURITY & AUTHENTICATION
# ========================================
JWT_SECRET_KEY=generate_a_secure_random_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
GUEST_SESSION_TTL_HOURS=2

# ========================================
# APP CONFIGURATION
# ========================================
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:3000
MAX_UPLOAD_SIZE_MB=50
ENVIRONMENT=development
```

---

## API Reference

Interactive OpenAPI documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Core Endpoints

- **`POST /api/v1/auth/login`**: Authenticate with student ID / email and password.
- **`GET /api/v1/auth/me`**: Get current user profile and role permissions.
- **`POST /api/v1/chat/`**: Submit a question for RAG processing with role-based document scoping.
- **`POST /api/v1/chat/guest/session`**: Create an anonymous guest session.
- **`POST /api/v1/documents/upload`**: Upload and trigger async chunking & vector indexing for PDF, DOCX, XLSX, CSV, and TXT files.
- **`GET /api/v1/admin/users`**: List and filter all registered users (Admin only).
- **`POST /api/v1/admin/users`**: Provision a new student, faculty, or admin account.
- **`GET /api/v1/health/`**: System health check endpoint.

---

## Troubleshooting & FAQ

### Q1: Does the model redownload every time I restart Docker?
**No.** Both the Ollama LLM model (`qwen3.5:4b`) and Hugging Face embeddings (`BAAI/bge-m3`) are saved into persistent named Docker volumes (`ollama_data` and `hf_cache`). The init script checks if the model exists and skips download if present.

### Q2: How do I verify all services are running properly?
```bash
docker compose ps
```
You should see all services in `Up` or `healthy` state, with `campus_assistant_ollama_init` and `campus_assistant_minio_init` having exited with code `0`.

### Q3: How do I completely reset all data?
```bash
# Stop containers and wipe volumes (caution: removes databases and cached models)
docker compose down -v
```
