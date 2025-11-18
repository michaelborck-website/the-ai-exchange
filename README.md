# The AI Exchange

**The AI Exchange** is an internal platform designed for the **School of Marketing and Management (SoMM)** to facilitate the discovery, sharing, and discussion of Artificial Intelligence use cases and applications.

The goal is to connect SoMM staff who are experimenting with AI ("The Spark") with those looking for guidance, while offering a safe ("Verified Anonymity") space to share failures, successes, and best practices in marketing and management contexts.

## 🚀 Project Overview

This is a full-stack web application built to run on a self-hosted VPS. It features a unified feed where staff can post three distinct types of resources:
1. **Use Cases:** Full stories/case studies of AI in teaching or research.
2. **Prompts:** Quick copy-paste blocks of text/code for specific tools.
3. **Policies:** Official or classroom-level governance documents.

### Key Features
* **Unified Feed:** Filters content by type, topic (Digital Marketing, Brand Strategy, Customer Analytics, etc.), or AI tool.
* **Verified Anonymity:** SoMM staff can post anonymously to reduce anxiety. Admins see the real identity, but the public frontend hides it.
* **Smart Connections:** Non-anonymous posts display the author's profile and deep links (Email/Teams) to encourage offline collaboration.
* **Auto-Tagging (NLP):** Uses `YAKE` (lightweight NLP) to automatically extract keywords from descriptions, keeping the server load low.
* **Domain Locking:** Authentication is restricted strictly to `@curtin.edu.au` email addresses.

## 🛠 Tech Stack

### Backend
* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
* **Database:** SQLite (MVP) / PostgreSQL (Production)
* **ORM:** SQLModel (Pydantic + SQLAlchemy)
* **NLP:** YAKE (Yet Another Keyword Extractor - CPU-only, zero external API calls)
* **Authentication:** Email/Password (bcrypt hashing) with Domain Whitelisting
* **Environment Management:** uv (Python package manager)
* **Code Quality:** ruff (linting/formatting), mypy (type checking), pytest (testing)

### Frontend
* **Framework:** React 18+ (via Vite)
* **Language:** TypeScript (strict mode)
* **UI Library:** Chakra UI
* **State Management:** React Query (TanStack Query)
* **Testing:** Vitest
* **Code Quality:** ESLint, Prettier

---

## ⚡️ Quick Start (Local Development)

### 1. Backend Setup
Navigate to the backend directory and set up the Python environment using `uv`.

```bash
cd backend

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Run the server with hot-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.
API Docs (Swagger) are at `http://localhost:8000/docs`.

### 2. Frontend Setup

Navigate to the frontend directory.

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The UI will be available at `http://localhost:5173`.

-----

## 🔐 Configuration (.env)

Create a `.env` file in the `backend/` directory. See `.env.example` for all available options:

```bash
cp backend/.env.example backend/.env
```

Key configuration variables:

```ini
# General
PROJECT_NAME="The AI Exchange - SoMM"
API_V1_STR="/api/v1"
SECRET_KEY="generate-a-secure-random-string-minimum-32-chars"

# Database
DATABASE_URL="sqlite:///./ai_exchange.db"  # For MVP/development

# Authentication
ALLOWED_DOMAINS="curtin.edu.au"

# Email (Mocked for MVP)
MAIL_FROM="noreply@curtin.edu.au"

# CORS
ALLOWED_ORIGINS="http://localhost:5173,http://localhost:3000"
```

See `backend/.env.example` for production settings including PostgreSQL and email configuration.

## 🏗 Architecture Decisions

### The "Resource" Model

To keep the database simple for the MVP, we use **Single Table Inheritance**. Prompts, Stories, and Policies are all stored in the `resources` table, distinguished by a `type` enum.

### Verified Anonymity Logic

The database *always* records the `user_id`. The API response serializer handles the privacy logic:

  * If `is_anonymous=True` → Return "Faculty Member" & `null` avatar.
  * If `is_anonymous=False` → Return `user.full_name` & `user.avatar`.

## 📚 Development Documentation

- **[CLAUDE.md](CLAUDE.md)** - Development guidelines, tooling setup, code standards
- **[docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)** - 10-phase implementation roadmap
- **[docs/srs.md](docs/srs.md)** - Complete software requirements specification

## 🚢 Deployment (VPS)

This project includes a `docker-compose.yml` for easy deployment on a Linux VPS (DigitalOcean/Linode/Internal/AWS).

```bash
# Build and run containers
docker-compose up -d --build

# View logs
docker-compose logs -f
```

See [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) Phase 10 for complete deployment instructions.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Copyright © 2025 Michael Borck

