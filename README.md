# CampusAI — KPRIET Campus Assistant

A full-stack RAG (Retrieval-Augmented Generation) chatbot for campus information,
with separate **Student** and **Admin** portals, JWT-based authentication,
role-based access control, and a Docker-first deployment pipeline.

---

## 📑 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Authentication System](#authentication-system)
3. [How to Add the First Admin](#how-to-add-the-first-admin)
4. [How Students Get Access](#how-students-get-access)
5. [Running Locally (Dev)](#running-locally-dev)
6. [Running with Docker Compose](#running-with-docker-compose)
7. [Environment Variables](#environment-variables)
8. [API Reference](#api-reference)
9. [Password Reset Flow](#password-reset-flow)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Docker Network                       │
│                                                          │
│  frontend-user (:5173) ──┐                              │
│                           ├──→  backend (:8000)          │
│  frontend-admin (:5174) ──┘       │    │                │
│                                  MongoDB  Qdrant         │
│                                   │    │                │
│                               MinIO   Ollama            │
└─────────────────────────────────────────────────────────┘
```

| Port | Service | Description |
|------|---------|-------------|
| 5173 | frontend-user | Student / Guest chat portal |
| 5174 | frontend-admin | Admin-only management portal |
| 8000 | backend | FastAPI REST API |
| 27017 | MongoDB | User data, conversations, sessions |
| 6333 | Qdrant | Vector store for document retrieval |
| 9000 | MinIO | Object storage for uploaded documents |
| 11434 | Ollama | Local LLM server (qwen2.5:7b) |

---

## Authentication System

### Token Storage

| Key | Where | Stores |
|-----|-------|--------|
| `campus_ai_token` | localStorage | JWT for authenticated students/faculty/admin |
| `campus_ai_role` | localStorage | `student` / `faculty` / `admin` |
| `campus_ai_name` | localStorage | Display name |
| `campus_guest_session` | localStorage | Guest session ID (no login) |
| `campus_admin_token` | localStorage | JWT for the admin portal specifically |

### User Portal (`http://localhost:5173`)

On first visit, the user sees a **choice screen**:

- **Continue as Guest** → Creates a temporary guest session (public info only, no history saved after reload)
- **Student / Staff Login** → Login with Student ID (e.g. `22CSEA001`) or email + password

### Admin Portal (`http://localhost:5174`)

- Completely separate application from the student portal
- Only users with `role: "admin"` can log in
- Trying to log in without admin role shows "Access denied"

### Role-Based Access Control

| Role | Permissions |
|------|------------|
| `guest` | Public documents only, no history |
| `student` | Public + student-level docs, conversation history |
| `faculty` | Public + student + faculty docs |
| `admin` | Everything + user management |

Backend enforces role checks on every API call — frontend route protection is secondary.

---

## How to Add the First Admin

### Method 1 — Automatic (Recommended) ✅

The **principal admin is seeded automatically** when the backend starts for the first time.

```
Email    : principal@kpriet.ac.in
Password : 123456
Role     : admin
```

No manual action required. Just start the backend:

```bash
# Local dev
cd backend
uvicorn app.main:app --reload

# Or with Docker
docker compose up -d
```

Check the logs:
```bash
docker logs campus_assistant_backend | grep Seed
# [Seed] Admin account created: principal@kpriet.ac.in
```

> ⚠️ **Change the default password immediately after first login!**
> Go to Admin Portal → change password via the profile/settings, or use the API.

---

### Method 2 — Manual via MongoDB Shell

If you need to add an admin directly to the database:

```bash
# Connect to MongoDB container
docker exec -it campus_assistant_mongodb mongosh

# Switch to your DB
use college_chatbot_db

# Insert admin (password hash for "123456" using argon2)
# Run this Python snippet first to get the hash:
```

```python
# Run locally to get the hash
from passlib.context import CryptContext
ctx = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
print(ctx.hash("YourNewPassword"))
```

```js
// Then in mongosh:
db.users.insertOne({
  email: "principal@kpriet.ac.in",
  password_hash: "<paste hash here>",
  name: "Principal",
  role: "admin",
  student_id: null,
  active: true,
  created_at: new Date(),
  updated_at: new Date(),
  club_ids: []
})
```

---

### Method 3 — Admin API (when already logged in as admin)

```bash
curl -X POST http://localhost:8000/api/v1/admin/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin_token>" \
  -d '{
    "email": "newadmin@kpriet.ac.in",
    "password": "SecurePass123",
    "name": "Vice Principal",
    "role": "admin"
  }'
```

---

## How Students Get Access

**No self-registration is allowed.** Only admins can create accounts.

### Admin Workflow to Add a Student

1. Log in to the **Admin Portal** → `http://localhost:5174`
2. Navigate to **Users** → click **Add User**
3. Fill in:
   - **Full Name** — student full name
   - **Email** — institutional email (e.g. `name@kpriet.ac.in`)
   - **Student ID** — e.g. `22CSEA001` (used for login)
   - **Password** — initial password (share securely with student)
   - **Role** — `student`
   - **Department ID**, **Year**, **Section** — optional but recommended
4. Click **Create User**

The student can then log in at `http://localhost:5173` using either their **Student ID** or **email** plus the initial password.

### Giving Faculty/Admin Access

Same process — just select **Role: faculty** or **Role: admin**.

---

## Running Locally (Dev)

### Prerequisites

- Python 3.11+
- Node.js 20+
- MongoDB running (or Docker)
- Qdrant running (or Docker)
- Ollama running with the model pulled: `ollama pull qwen2.5:7b`

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### User Frontend

```bash
cd frontend/apps/user
npm install
npm run dev        # → http://localhost:5173
```

### Admin Frontend

```bash
cd frontend/apps/admin
npm install
npm run dev        # → http://localhost:5174
```

Both Vite dev servers proxy `/api/*` requests to `http://localhost:8000` automatically.

---

## Running with Docker Compose

```bash
# From project root
cp .env.example .env    # Edit .env with your real values
docker compose up -d --build

# View logs
docker compose logs -f backend

# Stop everything
docker compose down
```

Services started:
1. `mongodb` — MongoDB 7.0
2. `minio` + `createbuckets` — Object storage
3. `qdrant` — Vector database
4. `ollama` — LLM server (pull model manually if GPU not available)
5. `backend` — FastAPI (auto-seeds principal admin on first run)
6. `frontend-user` — Nginx serving student app on port 5173
7. `frontend-admin` — Nginx serving admin app on port 5174

> 💡 The admin account is created automatically on first `backend` startup.

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# MongoDB
MONGO_URI=mongodb://mongodb:27017
MONGO_DB_NAME=college_chatbot_db

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=college-documents

# Qdrant (cloud or local)
QDRANT_URL=http://qdrant:6333
COLLECTION_NAME=college_knowledge
QDRANT_API_KEY=         # leave blank for local

# Ollama / LLM
OPENAI_BASE_URL=http://ollama:11434/v1
OPENAI_API_KEY=ollama
LLM_MODEL_NAME=qwen2.5:7b

# Embedding
EMBEDDING_MODEL_NAME=BAAI/bge-base-en-v1.5

# Security
SECRET_KEY=change-this-to-a-long-random-string
JWT_SECRET_KEY=change-this-too
```

---

## API Reference

### Auth Endpoints (`/api/v1/auth/`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/login` | Login with `identifier` (email or student_id) + `password` |
| POST | `/logout` | Revoke current session (requires Bearer token) |
| GET | `/me` | Get current user profile |
| POST | `/change-password` | Change own password (requires current password) |
| POST | `/forgot-password` | Request password reset token |
| POST | `/reset-password` | Reset password with token |

### Admin Endpoints (`/api/v1/admin/`) — Requires admin JWT

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users` | List all users (filter by `?role=` or `?active=`) |
| POST | `/users` | Create a new user |
| PATCH | `/users/{id}` | Update user fields |
| DELETE | `/users/{id}` | Deactivate user (soft delete) |
| POST | `/users/{id}/reset-password` | Admin resets a user password |
| POST | `/users/{id}/generate-reset-link` | Generate a reset token to share |

### Chat Endpoints (`/api/v1/chat/`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/` | Send a message (authenticated or guest) |
| POST | `/guest/session` | Create a new guest session |

---

## Password Reset Flow

### Student-initiated

1. Student clicks **Forgot password?** on login page
2. Enters Student ID or email
3. Admin is notified (in dev, the token is returned in the response)
4. Admin shares the reset token with the student
5. Student uses the token to set a new password at `/api/v1/auth/reset-password`

### Admin-initiated

1. Admin goes to **Users** page → finds the student
2. Clicks the **🔑 Reset Password** icon
3. Enters and sets a new password directly
4. Student uses the new password to log in

> 🔒 In production, wire `/api/v1/auth/forgot-password` to an SMTP email service.
> The `reset_token` field in the response is for development only — remove it in prod.

---

## Directory Structure

```
ChatBot/
├── backend/
│   ├── app/
│   │   ├── api/v1/         # auth.py, admin.py, chat.py, documents.py, health.py
│   │   ├── core/           # security.py, permissions.py
│   │   ├── db/             # mongodb.py, models.py
│   │   ├── llm/            # ollama_client.py
│   │   ├── rag/            # pipeline.py, retrieval.py, memory.py, chunking.py
│   │   ├── vector/         # qdrant_client.py
│   │   ├── embeddings/     # embedding_service.py
│   │   ├── config.py       # Settings (pydantic-settings, reads .env)
│   │   └── main.py         # FastAPI app + admin seed
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── apps/
│   │   ├── user/           # Student portal (port 5173)
│   │   │   ├── src/
│   │   │   │   ├── pages/Login.tsx      # Guest/Login choice screen
│   │   │   │   ├── pages/Chat.tsx       # Main chat (real API)
│   │   │   │   ├── layouts/UserLayout.tsx
│   │   │   │   └── App.tsx             # Route guard
│   │   │   ├── nginx.conf              # /api proxy for Docker
│   │   │   └── vite.config.ts          # /api proxy for dev
│   │   └── admin/          # Admin portal (port 5174)
│   │       ├── src/
│   │       │   ├── pages/Login.tsx      # Admin-only login
│   │       │   ├── pages/Users.tsx      # User management CRUD
│   │       │   ├── layouts/AdminLayout.tsx
│   │       │   └── App.tsx             # Admin route guard
│   │       ├── nginx.conf              # /api proxy for Docker
│   │       └── vite.config.ts          # /api proxy for dev
└── docker-compose.yml
```
