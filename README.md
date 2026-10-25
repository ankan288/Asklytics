# Asklytics — Verifiable Conversational Analytics & BI Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org/)
[![Dual LLM](https://img.shields.io/badge/Dual_LLM-Gemini_2.0_+_Groq_Llama_3.3-purple)](#architecture--hallucination-prevention-pipeline)

> **Ask business questions in plain English → Get AST-guarded SQL, mathematically verified insights, and interactive charts in seconds. No SQL. No hallucinated metrics.**

---

## 💡 What is Asklytics?

**Asklytics** is an open, verifiable conversational business intelligence engine. While existing "chat with CSV" tools simply pass data to an LLM and pray that the model doesn't invent numbers or execute malicious SQL, Asklytics combines **dual-model query generation**, **Abstract Syntax Tree (AST) query parsing**, **claim-level deterministic verification**, and **automated chart validity guards**.

Users can upload any CSV or query existing databases using natural language, receive instant visual dashboards, inspect how every metric was derived, and trust that every figure cited in prose is mathematically verified against raw database rows.

---

## 🛑 The Problem: Why Standard Text-to-SQL Fails on Real Data

Recent research shows a stark contrast between synthetic benchmarks and real-world enterprise deployments:

* **The Accuracy Cliff:** While commercial LLMs score >90% on simple synthetic benchmarks like Spider 1.0, benchmark accuracy drops to **5.7%** on real-world enterprise tasks (Spider 2.0-Lite).
* **Benchmark Noise:** A CIDR 2026 study (*"Text-to-SQL Benchmarks are Broken"*) discovered annotation error rates of 52.8% in BIRD Mini-Dev and 66.1% in Spider 2.0-Snow, demonstrating that naive single-prompt pipelines cannot be trusted in production.

Typical AI analytics applications suffer from five fatal flaws:

| Flaw | How It Breaks in Other Tools | Impact on Business |
| :--- | :--- | :--- |
| **1. Invented Numbers in Prose** *(ConDABench / InsightLens)* | The LLM writes convincing commentary citing numbers or percentages not actually present in query results. | Executives make critical decisions based on fabricated figures. |
| **2. Silent Wrong Interpretations** *(AmbiSQL / ABISS)* | Vague questions like *"What is our best product?"* cause the model to make silent guesses (revenue? units sold? margin? rating?). | Misaligned metrics across teams without anyone realizing. |
| **3. Vulnerable SQL Guards** *(P2SQL / ICSE 2025)* | Naive regex blacklists (`DROP`, `DELETE`) fail against SQL comments, subqueries, and dialect-specific exploits. | Potential data leaks or Denial of Service (DoS) from expensive un-indexed queries. |
| **4. Misleading Visualizations** *(VisEval / Rethinking NL2VIS)* | Models routinely produce 40-slice pie charts, unordered categorical line charts, or unreadable scatter plots. | Visual misinterpretation and poor decision-making. |
| **5. Context Loss in Follow-Ups** *(BIRD-INTERACT)* | Passing raw chat text into prompts causes the LLM to drop active filters and aggregations between turns. | Broken drill-downs and frustrating user experience. |

---

## 🛡️ How Asklytics Solves These Problems

Asklytics introduces a multi-layered verification and execution architecture designed around trust, safety, and auditability:

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
│                                     (Gemini 2.0 vs Groq Llama 3.3)          │
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

### 1. AST-Level Safe SQL Execution
Rather than relying on vulnerable regex matching, Asklytics parses all queries using `sqlglot` Abstract Syntax Trees:
- **Strict AST Whitelist:** Validates that the root node is strictly an `exp.Select` statement.
- **Schema Attribution:** Verifies all accessed tables and columns against introspected database metadata.
- **Read-Only Database Connection:** Enforced at the engine driver level (`file:...mode=ro`).
- **Enforced Safety Bounds:** Injects non-bypassable `LIMIT 1000` bounds and query timeouts (5.0s max).

### 2. Claim-Level Insight Verification
Instead of treating LLM summaries as authoritative truth, Asklytics passes Stage 2 prose through a deterministic verification engine:
- **Claim Extraction:** Breaks generated text into individual numeric and comparative claims.
- **Ground-Truth Recomputation:** Re-calculates each referenced quantity directly from the complete result set in code.
- **Verification Badging:** Every claim is labeled `[VERIFIED]`, `[UNVERIFIED]`, or `[REJECTED]`. Contradictory statements are excised or auto-corrected before reaching the UI.

### 3. Cross-Model Disagreement as an Ambiguity Signal
Ambiguity is detected through dual-model consensus:
- Query prompts run concurrently through **Google Gemini 2.0 Flash** and **Groq (Llama 3.3 70B)**.
- If the normalized SQL ASTs diverge (e.g. Gemini aggregates by `SUM(revenue)` while Groq groups by `COUNT(order_id)`), Asklytics surfaces **Clarification Chips** in the chat UI, letting the user select their intended meaning instead of guessing.

### 4. VisEval Chart Validity Guard
Automatically evaluates generated chart types against perceptual visualization rules:
- **Pie Charts:** Automatically converted to horizontal bar charts if categories exceed 7.
- **Line Charts:** Enforces sequential or temporal keys (dates, timestamps) to prevent misleading trends across categorical variables.
- **KPI Cards:** Enforces scalar single-value contracts.

### 5. Structured Conversation State
Maintains structured conversational memory:
- Rather than passing lossy chat transcripts, conversation history is preserved as an evolving JSON state (active metrics, filter predicates, dimensions, and sort orders).
- Follow-ups (e.g. *"Now show only 2023 and split by region"*) update the state delta deterministically.

### 6. "How I Got This" Transparency Panel
Every generated dashboard widget includes an audit drawer:
- **Executable SQL:** Formatted and copyable.
- **Stated Assumptions:** Plain-English explanations of choices made (e.g., *"Assumed 'sales' refers to total revenue after discount"*).
- **Execution Telemetry:** Execution latency (ms), rows scanned, and memory footprint.
- **Verification Badges:** Visual assurance verifying that cited numbers match the raw dataset.

---

## 🏆 Why Asklytics is Better: Market Comparison

| Feature | Enterprise BI + Chat<br>*(Power BI Copilot, Tableau Pulse)* | Single-File Chat Tools<br>*(Julius AI, CSV Chatbots)* | Standard Text-to-SQL Toy Projects | **Asklytics** |
| :--- | :--- | :--- | :--- | :--- |
| **Pricing / Lock-In** | High ($6,400/mo Fabric F64 capacity + per-seat costs) | ~$20/user/mo, limited to one-off file sessions | Open source | **Open source & lightweight** |
| **Data Scope** | Only queries pre-modeled semantic cubes in vendor ecosystem | Single uploaded file | Single database | **Instant CSV upload + relational DBs** |
| **Hallucination Defense** | Model-dependent prose | None (LLM hallucinates figures) | None (Single prompt) | **Deterministic Claim Verification** |
| **SQL Security** | Controlled by enterprise data gateway | Serverless code sandbox | Simple regex blacklist | **AST Parser (`sqlglot`) + Read-Only Connection** |
| **Ambiguity Handling** | Silent best guess | Silent best guess | Silent error or guess | **Cross-Model Disagreement + Clarification Chips** |
| **Chart Quality** | High (Pre-templated) | Inconsistent | Frequently broken | **VisEval Heuristic Guard & Auto-Fixer** |
| **Auditability** | Limited | Minimal | Raw SQL text | **"How I Got This" Audit Drawer** |

---

## 🏗️ Architecture & Technology Stack

| Layer | Technologies Used | Purpose |
| :--- | :--- | :--- |
| **Frontend** | **Next.js 14**, React 18, TypeScript | High-performance dashboard rendering and state management |
| **Styling & Motion** | **Tailwind CSS**, Framer Motion, GSAP | Fluid glassmorphic UI, responsive layouts, micro-animations |
| **Visualizations** | **Recharts**, Lucide Icons | Bar, Line, Area, Pie, KPI, Heatmap, Scatter, Histogram |
| **Backend API** | **FastAPI**, Uvicorn, Python 3.10+ | Asynchronous REST endpoints, CORS, lifespan database seeding |
| **Primary LLM** | **Google Gemini 2.0 Flash Lite** | Fast, cost-efficient SQL generation & insight reasoning |
| **Fallback & Consensus LLM** | **Groq (Llama 3.3 70B Versatile)** | High-speed ambiguity detection and zero-downtime fallback |
| **SQL Security** | **sqlglot** | AST parsing, schema whitelisting, injection prevention |
| **Database Engine** | **SQLite** (file-based + in-memory registry) | High-speed local querying; PostgreSQL-compatible roadmap |
| **Data Processing** | **Pandas** | CSV schema profiling, data typing, statistical column introspection |

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- **Python:** 3.10 or higher
- **Node.js:** 18.0 or higher (`npm` 9+)
- **Gemini API Key:** Free tier from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Groq API Key (Optional):** Free tier from [Groq Console](https://console.groq.com/)

---

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Windows: copy .env.example .env
```

**Configure `backend/.env`:**
```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
CORS_ORIGIN=http://localhost:3000
DB_PATH=./sample.db
SAMPLE_CSV_PATH=../data/amazon_sales.csv
```

**Launch Backend:**
```bash
python run.py
```
* Backend API: `http://localhost:8000`
* Interactive API Documentation (Swagger): `http://localhost:8000/docs`
* Health Check: `http://localhost:8000/health`

---

### 3. Frontend Setup

Open a new terminal window:

```bash
# Navigate to frontend
cd frontend

# Install packages
npm install

# Start development server
npm run dev
```

* Web Application: `http://localhost:3000`
* Direct Dashboard: `http://localhost:3000/dashboard`

---

## 📊 Example Queries to Try

Test the end-to-end intelligence and chart rendering with these business queries:

1. **Category Comparison (Bar Chart):**
   > *"What is the total revenue generated by each product category?"*
2. **Time-Series Analysis (Multi-Line Chart):**
   > *"Show me the monthly revenue trend for each category throughout 2022."*
3. **Compound Aggregation + Executive KPI (Multi-Widget):**
   > *"Compare the average customer rating and total revenue for each payment method. Also show the overall total revenue as a KPI card."*
4. **Contextual Drill-Down (Follow-Up):**
   > *"Now filter this down to only show the Asia and Europe regions."*
5. **Custom CSV Analysis:**
   - Click the **Upload Dataset** button in the header.
   - Upload any custom CSV (sales, inventory, churn, marketing).
   - Ask: *"Break down customer acquisition cost by campaign type."*

---

## 📡 API Reference

### Sessions
| Method | Endpoint | Description | Response |
| :--- | :--- | :--- | :--- |
| `POST` | `/sessions` | Create a new isolated conversation session | `{ "session_id": "uuid" }` |
| `DELETE` | `/sessions/{id}` | Terminate and clean up session | `{ "status": "deleted" }` |
| `GET` | `/health` | Server and database health check | `{ "status": "ok" }` |

### Natural Language Query
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/query` | Natural language question → AST validation → Execution → Verified Dashboard |

**Request Body:**
```json
{
  "session_id": "a9b8c7d6-...",
  "prompt": "What is the total revenue by category?",
  "datasource_id": "default"
}
```

**Response Payload:**
```json
{
  "sql": "SELECT product_category, SUM(total_revenue) AS revenue FROM amazon_sales GROUP BY product_category ORDER BY revenue DESC LIMIT 1000",
  "dashboard_title": "Total Revenue by Category",
  "charts": [
    {
      "id": "chart-1",
      "type": "bar",
      "title": "Revenue by Category",
      "data": [
        { "product_category": "Electronics", "revenue": 145200 },
        { "product_category": "Fashion", "revenue": 98700 }
      ],
      "x_key": "product_category",
      "y_keys": ["revenue"],
      "color_palette": ["#6366f1"]
    }
  ],
  "insight_summary": "Electronics generated the highest revenue at $145.2k, outperforming Fashion by 47%.",
  "data_limitations": null,
  "follow_up_suggestions": [
    "Break down Electronics revenue by region",
    "Show monthly growth for top categories"
  ],
  "verification": {
    "status": "verified",
    "claims_verified": 2,
    "claims_rejected": 0
  },
  "error": null
}
```

### Dataset Upload
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/upload/csv` | Upload multipart CSV → Register in-memory SQLite table |

---

## 🔒 Branch & Contribution Policy

To ensure production stability, Asklytics follows a strict sub-branch release process:
- Direct pushes to `main` are disabled.
- All new features, security updates, and enhancements are developed and tested on `feature/*` sub-branches.
- Only after passing the full test matrix (AST security checks, claim verification tests, and frontend build) are changes merged into `main`.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
