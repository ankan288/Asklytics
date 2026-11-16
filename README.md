# Asklytics — Verifiable Conversational Analytics & BI Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![Dual LLM](https://img.shields.io/badge/Dual_LLM-Gemini_3.5_+_Groq_OSS-purple)](#-architecture--verification-pipeline)

> **Ask business questions in plain English → Get AST-guarded SQL, mathematically verified insights, and interactive charts in seconds. No SQL required. Zero hallucinated metrics.**

---

## 📌 Table of Contents
- [What is Asklytics?](#-what-is-asklytics)
- [The Problem Asklytics Solves](#-the-problem-asklytics-solves)
- [What Asklytics is Capable Of](#-what-asklytics-is-capable-of)
- [External Requirements & API Keys](#-external-requirements--api-keys)
- [Step-by-Step Installation & Setup Guide](#-step-by-step-installation--setup-guide)
- [Step-by-Step How to Use the App](#-step-by-step-how-to-use-the-app)
- [Architecture & Verification Pipeline](#-architecture--verification-pipeline)
- [Latest Updates & Fixes Changelog](#-latest-updates--fixes-changelog)
- [API Reference](#-api-reference)
- [License](#-license)

---

## 💡 What is Asklytics?

**Asklytics** is an open-source, verifiable conversational Business Intelligence (BI) engine. While standard "chat-with-data" tools simply pass your database schema to a language model and hope the model doesn't hallucinate numbers or execute destructive queries, Asklytics implements an **enterprise-grade verification barrier**:

1. **Natural Language to Verified SQL**: Converts non-technical business questions into safe, optimized SQL queries.
2. **Dual-Model Cross-Checking**: Leverages multiple LLM families (Google Gemini + Groq) to catch ambiguity before queries run.
3. **AST-Level Query Safety**: Validates all generated SQL using Abstract Syntax Tree (AST) parsing (`sqlglot`), blocking SQL injections, mutations, and runaway queries.
4. **Deterministic Claim Verification**: Automatically parses numeric claims made in natural language summaries and validates every single number against the raw database rows.
5. **Interactive Visual Dashboards**: Renders responsive Recharts visualizations (Bar, Line, Area, Pie, KPI, Heatmap, Scatter, Histogram) equipped with an interactive **"How I Got This"** transparency drawer.

---

## 🛑 The Problem Asklytics Solves

Real-world business data pipelines face severe challenges when integrated with raw generative AI:

* **The Accuracy Cliff:** While commercial LLMs score >90% on simple synthetic benchmarks (like Spider 1.0), real-world enterprise Text-to-SQL benchmark accuracy plummets to **5.7%** (Spider 2.0-Lite).
* **Invented Numbers in Prose:** Generic AI assistants routinely cite figures, growth rates, and totals in their explanations that do not exist in the actual query results.
* **Silent Wrong Interpretations:** When an executive asks *"What is our top product?"*, standard models make silent guesses (sorting by revenue? units sold? margin? customer review rating?) without alerting the user.
* **Dangerous SQL Injections & Resource Exhaustion:** Simple regex blacklists (`DROP`, `DELETE`) fail against comments, subqueries, and dialect-specific exploits.
* **Misleading Visualizations:** Raw LLMs often generate illegible charts (e.g., 40-slice pie charts or categorical line graphs).

### How Asklytics Solves Each Problem

| Real-World Challenge | How Generic Tools Break | How Asklytics Solves It |
| :--- | :--- | :--- |
| **Hallucinated Numbers** | Models write convincing text citing numbers not in the data. | **Claim-Level Verifier**: Parses every numerical statement and validates it directly against the SQL result set. |
| **Ambiguous Prompts** | Models silently guess the user's intent. | **Clarification Chips**: Detects ambiguity and surfaces one-click disambiguation options. |
| **Malicious / Heavy SQL** | Naive regex filters can be bypassed. | **AST Whitelist (`sqlglot`)**: Only strict `SELECT` trees are permitted; read-only engine driver; non-bypassable `LIMIT 1000`. |
| **Bad Visualizations** | Broken axes, overcrowded slices, incorrect encodings. | **VisEval Heuristic Guard**: Automatically transforms bad charts (e.g., pie charts with >7 items auto-convert to bar charts). |
| **Security & Privacy** | API keys or paths leak in error traces. | **AST & Secrets Sanitization**: Scrubbing engine automatically redacts keys, tokens, and system paths from all client responses. |

---

## ⚡ What Asklytics is Capable Of

* 💬 **Conversational Data Analysis**: Ask any question in plain English (e.g., *"What was our total revenue per product category in Q3?"*).
* 🛡️ **Mathematically Verified Prose**: Clear summaries with claim verification badges: `[VERIFIED]`, `[UNVERIFIED]`, or `[CONTRADICTION DETECTED]`.
* 📊 **Multi-Chart Generation**: Automatically produces Bar, Multi-Line, Area, Donut, KPI metric cards, Scatter, and Histogram views based on data semantics.
* 📁 **Instant Custom CSV Ingestion**: Drag and drop any custom CSV file (up to 25MB). Asklytics profiles columns, auto-detects types, registers an in-memory/disk SQLite table, and allows immediate queries.
* 🔍 **"How I Got This" Transparency Drawer**: Inspect the sanitized SQL query, execution latency (ms), rows scanned, stated assumptions, and model consensus scores.
* 🔐 **Local Built-in Authentication**: SQLite-backed authentication with salted SHA-256 password hashing, JWT access tokens (1 hour), and refresh tokens (7 days). No external cloud auth required!
* 👮 **Role-Based Access Control (RBAC) & Admin Dashboard**: Dedicated `/admin` route with system health telemetry, query volume analytics, user management, and security audit logs.
* 🚦 **Sliding-Window Rate Limiting**: Dynamic backend protection enforcing 20 req/min on `/query`, 10 req/min on `/upload` and `/auth`, and 120 req/min globally.
* 📱 **Mobile-First & Modern UI**: Liquid glassmorphism, above-the-fold call-to-actions, sticky mobile CTA bar, preloader animations, and dark mode interface.
* 📜 **Full Legal Compliance**: Privacy Policy, Terms of Service, Cookie Policy, interactive Cookie Consent banner, GDPR & CCPA alignment.

---

## 🔑 External Requirements & API Keys

Asklytics is engineered to be **self-contained and local-first**. You do **not** need an AWS account, Supabase project, or paid cloud database to use Asklytics.

### 1. External LLM API Keys (What You Need)

| Environment Variable | Required? | Purpose | Where to Get It (Free) |
| :--- | :---: | :--- | :--- |
| `GEMINI_API_KEY` | **Required** | Primary engine for SQL generation, natural language reasoning, and insight summaries. | [Google AI Studio](https://aistudio.google.com/app/apikey) *(Free tier available)* |
| `GROQ_API_KEY` | **Optional** *(Recommended)* | High-speed secondary engine for fallback and dual-model consensus verification. | [Groq Console](https://console.groq.com/keys) *(Free tier available)* |

> [!NOTE]
> If you only have a `GEMINI_API_KEY`, Asklytics runs seamlessly in single-model mode using Gemini. Adding `GROQ_API_KEY` unlocks dual-model cross-validation and automatic failover!

### 2. Local Built-in Services (No Cloud Setup Needed!)

- **Database**: Embedded **SQLite** (`sample.db`). Automatically seeded on first startup with a 1,000-row `amazon_sales` dataset.
- **Authentication**: **Local Built-in Auth**. User accounts, password hashes, sessions, and conversation turns are stored in SQLite. No third-party auth service is required.

---

## 🚀 Step-by-Step Installation & Setup Guide

### System Prerequisites
Ensure you have the following installed on your machine:
- **Python**: `3.10` or newer ([Download Python](https://www.python.org/downloads/))
- **Node.js**: `18.0` or newer / `v20+` ([Download Node.js](https://nodejs.org/))
- **Git**: Installed and configured

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/Asklytics.git
cd Asklytics
```

---

### Step 2: Set Up the Backend (FastAPI)

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create your `.env` configuration file**:
   Inside the `backend/` directory, create a `.env` file:
   ```env
   # LLM API Keys (Obtain for free from Google AI Studio and Groq)
   GEMINI_API_KEY=your_gemini_api_key_here
   GROQ_API_KEY=your_groq_api_key_here

   # Local SQLite Database (auto-created and seeded on startup)
   DB_PATH=./sample.db
   SAMPLE_CSV_PATH=../data/amazon_sales.csv

   # Local JWT Security
   JWT_SECRET=asklytics-dev-jwt-secret-key-32chars-min
   SUPABASE_JWT_SECRET=asklytics-dev-jwt-secret-key-32chars-min
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
   JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

   # CORS Configuration
   CORS_ORIGIN=http://localhost:3000
   PORT=8000
   ENVIRONMENT=development
   ```

5. **Start the Backend Server**:
   ```bash
   python run.py
   ```
   * The backend will automatically seed the `amazon_sales` demo data and create all authentication tables.
   * Backend API: `http://localhost:8000`
   * Interactive Swagger Docs: `http://localhost:8000/docs`
   * Health Check: `http://localhost:8000/health`

---

### Step 3: Set Up the Frontend (Next.js 14)

Open a **new terminal window** and navigate to the `frontend/` directory:

1. **Navigate to frontend**:
   ```bash
   cd Asklytics/frontend
   ```

2. **Install frontend dependencies**:
   ```bash
   npm install
   ```

3. **Verify or create `frontend/.env.local`**:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start the Frontend Development Server**:
   ```bash
   npm run dev
   ```
   * Web Application: `http://localhost:3000`

---

## 🖥️ Step-by-Step How to Use the App

```
1. Open http://localhost:3000
       │
       ▼
2. Register an Account (/register) ──► Log In (/login)
       │
       ▼
3. Enter Analytics Dashboard (/dashboard)
       │
       ├──► A. Query Pre-Loaded "Amazon Sales" Dataset
       │       - Type natural language prompt
       │       - Handle ambiguity chips if prompted
       │       - View interactive Recharts dashboard
       │       - Inspect "How I Got This" SQL & audit trail
       │
       ├──► B. Upload Custom CSV Dataset
       │       - Drag & drop any CSV file (up to 25MB)
       │       - Ask questions against newly created table
       │
       └──► C. Admin Control Center (/admin)
               - Inspect system telemetry, rate limits, and users
```

### Detailed Workflow:

#### 1. Account Creation & Secure Sign-In
- Visit [http://localhost:3000/register](http://localhost:3000/register).
- Register your email and a password (minimum 8 characters).
- Upon registration, your password is salted and hashed with SHA-256 in the local SQLite database, and an authenticated JWT session is issued.
- If you already have an account, sign in at [http://localhost:3000/login](http://localhost:3000/login).

#### 2. Querying Pre-Loaded Data
Once logged in, you will be redirected to the **Analytics Dashboard** (`/dashboard`). The default dataset (`amazon_sales`) is active. Try asking:
- *"What is the total revenue generated by each product category?"*
- *"Show me monthly sales trends across 2022."*
- *"Compare average rating and revenue by payment method."*
- *"Which customer region has the highest average order value?"*

#### 3. Resolving Ambiguities with Clarification Chips
If you ask a vague question like *"What is our best category?"*, Asklytics detects that "best" could mean revenue, units sold, or customer rating. Instead of guessing, it surfaces **Clarification Chips** (e.g. `[By Revenue]`, `[By Units Sold]`, `[By Customer Rating]`). Click one to instantly generate the precise visualization.

#### 4. Auditing Insights & SQL
Underneath each generated dashboard:
- Click the **"How I Got This"** drawer.
- View the exact AST-verified SQL statement that executed.
- Review latency in milliseconds and rows scanned.
- Review the **Claim Verification Badge**: green indicates every numeric claim matched database calculations; red alerts indicate contradictions were caught and corrected.

#### 5. Uploading Your Own Custom CSV
- Click the **Upload Dataset** icon in the dashboard navigation.
- Drag and drop your own CSV file (e.g., marketing metrics, retail inventory, SaaS churn).
- Asklytics sanitizes column names, detects data types, and creates an isolated SQLite table.
- Ask questions immediately against your new data!

#### 6. Accessing the Admin Dashboard
- Visit [http://localhost:3000/admin](http://localhost:3000/admin).
- View real-time system metrics, rate limiter statistics, active database tables, and user accounts.
- Non-admin users attempting to access admin endpoints are blocked by backend RBAC (`403 Forbidden`).

---

## 🏛️ Architecture & Verification Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ASKLYTICS PIPELINE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  User Query ─────────► [1. Ambiguity & Vague Term Detector]                 │
│                                  │                                          │
│                         Ambiguous?                                          │
│                         ├── YES ──► Emit Clarification Chips UI             │
│                         └── NO  ──► Dual LLM Query Planning                 │
│                                             │                               │
│                                    [2. Disagreement Signal]                 │
│                                     (Gemini 3.5 vs Groq Llama/OSS)          │
│                                             │                               │
│                                    [3. Structured State Manager]            │
│                                     (Metrics, Dimensions, Filters JSON)     │
│                                             │                               │
│                                    [4. AST Safe SQL Layer]                  │
│                                     (sqlglot AST parse, table/column check, │
│                                      read-only connection, row/time limits) │
│                                             │                               │
│                                    [Database Execution (SQLite / PG)]       │
│                                             │                               │
│                              ┌──────────────┴──────────────┐                │
│                              ▼                             ▼                │
│                 [5. Chart Validity Checker]   [6. Claim-Level Verifier]     │
│                  - VisEval heuristics          - Segment numeric claims     │
│                  - Auto-fix illegible charts   - Recompute against full data│
│                  - Ensure semantic fit         - Mark Verified / Rejected   │
│                              │                             │                │
│                              └──────────────┬──────────────┘                │
│                                             ▼                               │
│                         [7. 'How I Got This' Audit & Trust Panel]           │
│                          - SQL AST explanation, assumptions made            │
│                          - Rows scanned, latency, verification badge        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Latest Updates & Fixes Changelog

Here is a summary of the latest architectural improvements and bug fixes applied to the codebase:

### 1. Backend Login Check Enforcement
- **Universal API Lockdown**: All analytical endpoints (`/query`, `/sessions`, `/upload/csv`, `/conversations`, `/admin/*`, `/auth/me`) now require a valid JWT Bearer token.
- **Starlette CORS Ordering Fix**: Positioned `CORSMiddleware` outermost in the middleware stack, guaranteeing that `401 Unauthorized` and `429 Rate Limited` responses always contain valid CORS headers for browser clients.
- **Frontend `AuthGuard` Integration**: Protected `/dashboard` and `/admin` routes verify live sessions with `GET /auth/me` on mount, automatically redirecting expired or unauthenticated sessions to `/login`.

### 2. Multi-Model LLM Resilience & Updated Endpoints
- **Model Deprecation Fix**: Updated retired Gemini models to current endpoints: `gemini-3.5-flash-lite` and `gemini-flash-latest`.
- **Groq Fallback Integration**: Added high-speed fallback to `openai/gpt-oss-120b` and `qwen/qwen3.8-27b`, ensuring zero downtime if Gemini quotas are exceeded.

### 3. Enterprise Security Hardening
- **Sliding-Window Rate Limiting**: Added `RateLimitMiddleware` to prevent API flooding (`/query`: 20 req/min, `/upload`: 10 req/min, `/auth`: 10 req/min).
- **Secrets & Path Redaction**: Added `sanitize_error_message` to scrub API keys, tokens, and local file system paths from error responses.
- **Strict Input Validation**: Pydantic models validate prompt lengths (2–2000 chars) and block null bytes or malicious control characters.
- **Role-Based Access Control (RBAC)**: Added `role` enforcement (`user` vs `admin`) on `/admin/*` routes.

### 4. Frontend & Design Enhancements
- **Custom 404 Not Found Page**: Integrated animated custom 404 error page with Home redirection.
- **Above-The-Fold Redesign**: Landing page hero updated to display interactive example queries and direct CTAs without requiring scrolling.
- **Sticky Mobile CTA**: Mobile viewports feature a persistent floating CTA bar (`md:hidden`).
- **Legal Compliance Suite**: Added Privacy Policy, Terms of Service, Cookie Policy, and dynamic Cookie Consent banner.
- **SEO & Search Standards**: Generated dynamic `/sitemap.xml` and `/robots.txt` endpoints with per-page metadata templates.
- **Tailwind Module Compatibility**: Converted `tailwind.config.ts` to `tailwind.config.js` to eliminate CommonJS/ES module resolution conflicts on Next.js 14.

---

## 📡 API Reference

### Public Endpoints (No Token Required)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API status, health overview, and frontend links |
| `GET` | `/health` | Server and database health check (`{"status": "ok"}`) |
| `POST` | `/auth/register` | Register a new user account (`{email, password, display_name}`) |
| `POST` | `/auth/login` | Authenticate and obtain access + refresh tokens |
| `POST` | `/auth/refresh` | Refresh access token using refresh token |
| `GET` | `/docs` | Swagger interactive API documentation |

### Protected Endpoints (Requires `Authorization: Bearer <token>`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/auth/me` | Fetch authenticated user profile & role |
| `POST` | `/sessions` | Create a new isolated conversation session |
| `DELETE` | `/sessions/{id}` | Terminate and clean up conversation session |
| `POST` | `/query` | Natural language question → AST check → Verified Dashboard |
| `POST` | `/upload/csv` | Multipart CSV file upload (max 25MB) → In-memory SQLite table |
| `GET` | `/conversations` | Retrieve stored conversation history for user |
| `GET` | `/admin/stats` | Admin only: Query counts, system health, and registered users |

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
