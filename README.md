# College RAG Chatbot - Full Stack Docker & Local Deployment Guide

An enterprise RAG web application built with **FastAPI**, **React 18**, **MinIO Object Storage**, **MongoDB Database**, **Qdrant Vector Store**, **HuggingFace Embeddings (`BAAI/bge-base-en-v1.5`)**, and **Local Ollama Model (`qwen2.5:7b`)**.

---

## 🚀 Quick Start with Docker Compose

The entire stack (MongoDB, MinIO, Auto Bucket Creation, FastAPI Backend, Nginx-served React Frontend) is fully containerized and orchestrated via `docker-compose.yml`.

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed & running.
- [Ollama](https://ollama.com/) running on your host machine (`ollama serve`).

### Launch All Containers
Run the following command in the root directory:

```bash
docker compose up --build -d
```

### Services Available After Launch

| Service | Endpoint | Description |
| :--- | :--- | :--- |
| **React Web App** | `http://localhost:3000` | Full UI (Admin, Student, Guest views) |
| **FastAPI Backend** | `http://localhost:8000` | REST API endpoints |
| **FastAPI Swagger Docs** | `http://localhost:8000/docs` | Interactive API documentation |
| **MinIO Console UI** | `http://localhost:9001` | Object storage management (`minioadmin` / `minioadmin`) |
| **MongoDB** | `localhost:27017` | Database for users, metadata & chat histories |

---

## 📂 Project Structure

```
ChatBot/
├── docker-compose.yml         # Container orchestration (MongoDB, MinIO, Backend, Frontend)
├── backend/                   # FastAPI Backend
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py            # FastAPI entry point
│       ├── config.py          # Centralized configuration
│       ├── database/          # Mongo & MinIO storage handlers
│       ├── services/          # RAG, VectorStore, Auth, Document Loader
│       └── routes/            # Auth, Admin, and Chat REST endpoints
└── frontend/                  # React Vite Frontend
    ├── Dockerfile
    ├── nginx.conf             # Nginx reverse proxy to backend:8000
    ├── README.md              # Parameter reference guide
    └── src/
        ├── App.jsx            # Tab & Auth router (Admin, Student, Guest)
        ├── components/        # AdminDashboard, StudentPortal, GuestPortal
        └── services/api.js    # HTTP API client
```

---

## 🛠️ Local Development (Without Docker)

### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🔒 User Roles & Access

1. **Admin Control Center**:
   - Access tab: **Admin Control**
   - Features: PDF drag & drop upload, document category tagging (`Academic`, `Placement`, etc.), live search & filters, file deletion (with dynamic vector DB removal), and vector re-indexing.

2. **Student Portal**:
   - Access tab: **Student Portal**
   - Features: Login with Student ID or credentials, sidebar listing past chat history sessions with timestamps, RAG Q&A interface with source citations.

3. **Guest Mode**:
   - Access tab: **Guest Mode**
   - Features: Quick fast-query interface for temporary questions.
