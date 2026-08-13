# Campus AI Assistant

The **Campus AI Assistant** is a production-grade, containerized AI platform built to securely and intelligently answer user queries based on authoritative campus documents. It employs a local Retrieval-Augmented Generation (RAG) pipeline utilizing open-source LLMs via Ollama, highly accurate vector search through Qdrant, and role-based access control (RBAC).

---

## 🏛 Architecture & How the System Works

The system is strictly divided into two layers: a **FastAPI Backend** and a **React Frontend**, tied together using a unified `docker-compose` network.

### The Backend
The backend serves as the brain of the application and handles:
- **Authentication**: JWT-based stateless authentication with Argon2 password hashing. Role definitions include `Guest`, `Student`, `Faculty`, and `Admin`.
- **Document Ingestion**: Fast processing of PDF, DOCX, XLSX, CSV, TXT, and MD files. The background pipeline extracts text, chunks it contextually (e.g., keeping spreadsheet rows together), and sends it to Qdrant.
- **RAG Pipeline**: 
  - Uses the **BAAI/bge-m3** (1024-dimension) embedding model for document chunk embeddings.
  - Queries are sent to **Qdrant** with strict RBAC filtering (a student only searches documents assigned to their department/club or public ones).
- **LLM Engine**: By default, it connects to a local **Ollama** service running **Qwen3.5-4B** (`qwen3.5:4b`). The LLM receives the user’s query, previous conversation context, and the retrieved context from Qdrant, generating an accurate response alongside clickable source citations.
- **Conversational Memory**: A MongoDB-backed engine tracks the last few messages in a conversation. When a conversation exceeds a specific length, it uses the LLM to generate a summary of older messages, preserving token limits while retaining context.

### The Frontend
Built with **React & Vite**, the UI provides distinct, secure portals based on the user's role:
- **Guest Portal**: Unauthenticated access restricted to public-only information. Features a session TTL to ensure data privacy.
- **Student/Faculty Portal**: Authenticated portals with access to department-specific knowledge. Users can review conversation histories, narrow search scopes, and click on citations to trace back to original source files.
- **Admin Dashboard**: A comprehensive control panel. Admins can upload documents, configure category trees, edit user permissions, and track background processing jobs in real time.

---

## 📁 Project Structure

```text
ChatBot/
├── docker-compose.yml         # Defines persistent volumes and services (MongoDB, MinIO, Qdrant, Ollama, Backend, Frontend)
├── .env.example               # Reference template for environment variables
├── scripts/                   # Database backups, restores, and Ollama initialization scripts
│
├── backend/                   # FastAPI Application
│   ├── Dockerfile             # Container definition for the backend
│   ├── requirements.txt       # Python dependencies (PyMuPDF, openpyxl, pandas, fastapi, etc.)
│   └── app/
│       ├── main.py            # API Entry Point & CORS Setup
│       ├── config.py          # Bridges .env to Python code (Validates and sets defaults)
│       ├── core/              # Security (JWT, Argon2) and Permissions (RBAC)
│       ├── db/                # MongoDB client and Pydantic models (11+ collections)
│       ├── documents/         # Strategy pattern parsers (PDF, XLSX, DOCX, CSV, TXT)
│       ├── embeddings/        # BAAI/bge-m3 SentenceTransformer integration
│       ├── llm/               # Ollama Async client
│       ├── rag/               # RAG logic (Ingestion, Retrieval, Memory, Pipeline)
│       ├── vector/            # Qdrant client configured for 1024-dim vectors
│       └── api/v1/            # Versioned API routes (auth, admin, chat, documents, health)
│
└── frontend/                  # React + Vite Application
    ├── Dockerfile             # Multi-stage build (builds static files, serves with Nginx)
    ├── package.json           # Node dependencies
    ├── nginx.conf             # Nginx reverse proxy configuration for the backend API
    └── src/
        ├── App.jsx            # React Router setup with Protected Routes
        ├── context/           # AuthContext for global session state
        ├── services/          # Axios HTTP client with JWT interceptors
        └── components/        # UI Views (Admin, Student, Guest portals)
```

---

## ⚙️ Understanding Configuration (`.env` vs `config.py`)

Configuring a secure system requires separating secret passwords from the code. This is handled using a two-step process:

1. **`.env.example` vs `.env`**:
   - `.env.example` is a safe template committed to GitHub. It shows developers what settings are required.
   - `.env` is a local text file that you create (by copying `.env.example`). It holds your actual, highly sensitive passwords. This file is ignored by Git, meaning hackers can never scrape it from your repository.
2. **`config.py`**:
   - Because `.env` is just a text file, Python doesn't naturally know how to read it safely. `config.py` acts as the security guard. It reads the `.env` file, checks the settings for typos (e.g., ensuring a port is a number, not a word), provides backup defaults if a setting is missing, and serves this data cleanly to the rest of the backend application.

---

## 🚀 Step-by-Step Deployment Guide

Follow these steps to deploy the entire stack locally or on a cloud server (VPS).

### Step 1: Environment Setup
1. Clone the repository and navigate to the project root.
2. Copy the template to create your live configuration file:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and fill in any custom passwords. By default, it is configured securely out-of-the-box. Ensure `OLLAMA_MODEL=qwen3.5:4b` is set.

### Step 2: Spin Up the Cluster
The infrastructure relies heavily on Docker. Start the cluster in detached mode:
```bash
docker compose up -d --build
```
*Docker will automatically create the required persistent volumes on your server for the databases and models.* 

### Step 3: Initialize the LLM (Qwen3.5-4B)
The Ollama container boots up empty. You must download the model weights before asking questions. Run the included initialization script:
```bash
chmod +x scripts/init_ollama.sh
./scripts/init_ollama.sh
```
*This downloads `qwen3.5:4b` directly into the `ollama_data` Docker volume. It will persist safely across server restarts.*

---

## 🌍 Exposing to the Public Internet (Cloud Hosting)

If you are hosting this on a cloud provider like **AWS, DigitalOcean, or Linode**, simply running `docker compose up -d` makes the application available via the server's **Public IP address**.

To make it production-ready and secure for users:
1. **Domain Name**: Purchase a domain name (e.g., `campus-ai.com`) and point its DNS "A Record" to your server's Public IP address.
2. **Reverse Proxy (Nginx / Traefik)**: Set up a reverse proxy in front of your Docker containers to listen on Port 80 (HTTP) and Port 443 (HTTPS).
3. **SSL Certificates**: Use Let's Encrypt / Certbot to generate a free SSL certificate to encrypt user passwords over HTTPS.
4. **Firewall Rules**: **CRITICAL SECURITY MEASURE:** Use your cloud provider's firewall to block all outside traffic to ports `27017` (MongoDB), `6333` (Qdrant), and `11434` (Ollama). The only ports that should be open to the internet are `80` (HTTP) and `443` (HTTPS).

---

## 💾 Managing Persistent Data & Server Migration

All data in this stack is strictly isolated in Docker volumes to prevent data loss. 

- **`mongodb_data`**: Stores user profiles, metadata, histories, and logs.
- **`minio_data`**: Stores the raw uploaded PDFs and spreadsheets.
- **`qdrant_data`**: Stores the 1024-dimensional document chunks.
- **`ollama_data`**: Stores the AI model weights (`qwen3.5:4b`).

### How to Migrate Databases to a New Server
Because data is locked inside Docker volumes managed by the host OS, you cannot simply copy and paste a folder. To move MongoDB to a new server:

**On the OLD Server:**
1. Run the backup script: `./scripts/backup_mongodb.sh`
2. This reaches into the volume and creates an archive file inside the `backups/` directory (e.g., `mongo_backup_20260813.archive`).
3. Download this file to your personal computer.

**On the NEW Server:**
1. Upload your code and the `.archive` file.
2. Run `docker compose up -d` to create fresh, empty volumes.
3. Run the restore script, pointing it to the archive file:
   ```bash
   ./scripts/restore_mongodb.sh backups/mongo_backup_20260813.archive
   ```
4. All of your users, chats, and metadata will instantly be populated in the new environment. (Note: You may need to re-upload raw documents or migrate MinIO/Qdrant volumes manually if you don't wish to re-ingest them).
