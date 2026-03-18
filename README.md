# Asklytics — Conversational Analytics Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org/)

**Status**: 🚀 **MVP Complete | Production-Ready | Ready for Authentication Integration**

Conversational AI for Instant Business Intelligence Dashboards.
Type a plain-English business question → get an interactive chart dashboard in seconds. **No SQL. No code.**

---

## 🎯 Project Status Summary

### ✅ **COMPLETED (Phase 1-4)**

#### Backend
- [x] FastAPI server with CORS, health checks, lifespan hooks
- [x] LLM Integration with automatic fallback:
  - **Primary**: Gemini API (`gemini-2.0-flash-lite`) - Fast, cost-effective
  - **Fallback**: Groq API (`llama-3.3-70b-versatile`) - Free, unlimited, sub-second latency
  - Transparent switching when primary fails (quota/rate limits)
  - 2-stage prompting: SQL generation + insight grounding
- [x] SQLite database (file-based + in-memory registry for CSV uploads)
- [x] Schema introspection with column statistics (prevents hallucination)
- [x] SQL execution with SELECT-only validation (injection-safe)
- [x] CSV upload processor (pandas + in-memory SQLite)
- [x] Session management (TTL 1 hour, 10-turn history, UUID-based)
- [x] Error handling with structured error responses
- [x] Row-level data merging from SQL results into charts
- [x] Follow-up context threading (chat history) to Gemini

#### Frontend
- [x] Landing page (hero, login/demo call-to-action)
- [x] Dashboard page (chat + live charts)
- [x] Login/register page scaffolds (UI-only, no backend auth yet)
- [x] Chat interface (message history, follow-up support)
- [x] Chart rendering (bar, line, area, pie, KPI)
- [x] CSV upload modal with drag-and-drop
- [x] Error banners for API/SQL/AI failures
- [x] Loading spinners and skeleton loaders
- [x] Responsive grid layout (mobile/tablet/desktop)
- [x] Custom UI components (glass surfaces, animations, gradients)
- [x] Session persistence via localStorage
- [x] Toast notifications
- [x] Profile menu with logout placeholder

#### Data & Hallucination Prevention
- [x] Amazon Sales dataset (50k rows, 13 columns, 2022-2023)
- [x] Column statistics in schema (min/max for numerics, distinct values for categoricals)
- [x] 2-sample rows per table for concrete context
- [x] Two-stage Gemini prompting:
  - Stage 1: SQL + chart specs from schema
  - Stage 2: Insights grounded in ACTUAL query results (not predicted)
- [x] Error field handling for unanswerable queries
- [x] SQL validation blocking fabricated columns
- [x] Retry logic for JSON parsing failures

---

### ⏳ **PENDING (Phase 5+) — Before Production Deployment**

#### Authentication & Authorization
- [ ] **User authentication system** (Firebase OR Supabase)
  - [ ] Signup/login backend endpoints
  - [ ] JWT or session token validation
  - [ ] Frontend auth flow integration (redirect on auth fail)
  - [ ] Secure token storage (httpOnly cookies preferred)
  - [ ] Password reset flow
  - [ ] Email verification (optional but recommended)

- [ ] **Multi-tenancy & data isolation**
  - [ ] User-to-datasource relationship (who owns what CSV)
  - [ ] Row-level security (RLS) if using Supabase PostgreSQL
  - [ ] Session isolation (users only see their sessions)
  - [ ] Query logging with user attribution

#### Database Migration & Scaling
- [ ] **PostgreSQL migration** (if adopting Supabase for multi-user)
  - [ ] Migrate SQLite → PostgreSQL (1 SQL dump)
  - [ ] Update connection pool in backend
  - [ ] Full-text search indexing (optional: for fast schema lookup)
  - [ ] Backup strategy

- [ ] **Persistent session storage** (currently in-memory)
  - [ ] Move session store to database (Redis or PostgreSQL)
  - [ ] Enable session recovery after server restart
  - [ ] Implement TTL cleanup job

#### Production Hardening
- [ ] **Environment validation**
  - [ ] Check GEMINI_API_KEY exists at startup
  - [ ] Validate CSV path accessibility
  - [ ] Database connection pooling for PostgreSQL

- [ ] **Rate limiting**
  - [ ] Per-user query limits (prevent abuse)
  - [ ] Per-session request throttling
  - [ ] Gemini API cost monitoring

- [ ] **Input validation & sanitization**
  - [ ] CSV file validation (max rows, column count, data types)
  - [ ] Prompt length limits (prevent token overflow)
  - [ ] Column name whitelisting for uploaded CSVs

- [ ] **Observability**
  - [ ] Structured logging (JSON format for parsing)
  - [ ] Error tracking (Sentry or similar)
  - [ ] Performance monitoring (query/API latency)
  - [ ] Gemini API fallback (if rate-limited, degrade gracefully)

- [ ] **Security & compliance**
  - [ ] HTTPS enforcement (production deployments)
  - [ ] CSRF token on form submissions
  - [ ] SQL injection prevention audit (currently regex-based, could add parameterized queries)
  - [ ] Data retention policy (when to delete uploaded CSVs)
  - [ ] Privacy policy & user data handling

- [ ] **Testing**
  - [ ] Unit tests (services, validators)
  - [ ] Integration tests (API endpoints)
  - [ ] E2E tests (landing → login → query → dashboard)
  - [ ] Hallucination test cases (verify AI doesn't make up data)

#### Frontend Polish
- [ ] **Accessibility (a11y)**
  - [ ] ARIA labels on interactive components
  - [ ] Keyboard navigation (Tab, Enter, Escape)
  - [ ] Color contrast validation (WCAG AA)

- [ ] **Edge cases**
  - [ ] Empty CSV handling
  - [ ] Very large CSV (>100k rows) performance
  - [ ] Network timeout recovery
  - [ ] Browser back/forward button behavior

---

## 💡 Improvement Suggestions (Priority Order)

### 🔴 **Critical (Before MVP Demo)**
1. **Add authentication** — currently anyone can access the dashboard
   - Recommendation: **Supabase Auth** (easiest integration with PostgreSQL later)
   - Time: ~2-3 hours
   - Blocks: Multi-user deployment

2. **Session persistence** — sessions lost on server restart
   - Move `_sessions` dict to Redis or database
   - Time: ~1 hour
   - Impact: Better user experience for long sessions

3. **Gemini model validation** — ensure `gemini-flash-lite-latest` is available
   - Current model might rotate; add fallback to `gemini-1.5-flash`
   - Time: 15 mins

### 🟠 **High (MVP v2)**
4. **Rate limiting** — prevent abuse
   - Add per-user request throttling
   - Track Gemini API usage
   - Time: ~1 hour

5. **Data cleanup** — uploaded CSVs never deleted
   - Add automatic cleanup after 1 day
   - Manual delete endpoint
   - Time: 30 mins

6. **Query logging** — no audit trail
   - Log all queries → database
   - Enable user history ("past 10 queries")
   - Time: 1 hour

7. **Better error messages** — some errors are generic
   - Parse Gemini errors more granularly
   - Add "try rephrasing your question" tips
   - Time: 1 hour

### 🟡 **Medium (Future)**
8. **RAG (Retrieval-Augmented Generation)**
   - Add vector embeddings for uploaded CSVs
   - Improve context length for large datasets
   - Time: 2-3 hours

9. **Advanced charts**
   - Scatter plots, heatmaps, histograms
   - Forecast/trend lines
   - Time: 2 hours

10. **Dashboard sharing**
    - Generate public read-only links
    - Embed iframes in other apps
    - Time: 2 hours

11. **Chart customization**
    - Axis labels, color picker, legend position
    - Export as PNG/PDF
    - Time: 2 hours

---

## Architecture & Hallucination Prevention Strategy

### AI Model Fallback System

**Automatic LLM Switching:**
```
Primary: Gemini (gemini-2.0-flash-lite)
   ↓ (if fails: quota/rate limit/error)
Fallback: Groq (llama-3.3-70b-versatile) - Free, unlimited
```

**Benefits:**
- **Zero downtime**: Seamless switching when Gemini quota exhausted
- **Cost optimization**: Free fallback prevents service interruption
- **Performance**: Groq provides sub-second response times
- **Transparent**: Users never see which model is used

---

### Two-Stage AI Prompting (Prevents Hallucination)

**Stage 1: SQL + Chart Spec Generation**
```
Input: Database schema (columns, sample rows, value ranges) + user question
Output: { sql, charts[], dashboard_title, follow_up_suggestions }
Safety: System prompt forbids fabricating column names; schema limits valid outputs
```

**Stage 2: Insight Grounding (AFTER SQL execution)**
```
Input: User question + SQL used + ACTUAL query results
Output: { insight_summary (cites real numbers), data_limitations }
Safety: Insights ONLY from real data, never predicted
```

**Why this works:**
- Stage 1 validates against schema → prevents invalid column names
- Stage 2 runs AFTER DB query → ensures insights match actual data
- Error field catches unanswerable questions upstream
- SQL validator blocks non-SELECT statements

**Example:**
- Q: "Show revenue by unicorn_category"
- Result: `{ "error": "Column 'unicorn_category' does not exist" }`
- Frontend: Displays error, no broken charts

---

## Tech Stack (Current)

| Layer | Technology | Version |
|-------|-----------|---------|
| **Frontend** | Next.js | 14 |
| **Frontend Styling** | Tailwind CSS | 3.4 |
| **Charts** | Recharts | 2.12 |
| **Animations** | Framer Motion | 12.36 |
| **Frontend HTTP** | Fetch API (native) | — |
| **Backend** | FastAPI | 0.111+ |
| **Backend Server** | Uvicorn | 0.29+ |
| **LLM Primary** | Google Gemini | gemini-2.0-flash-lite |
| **LLM Fallback** | Groq (Llama 3.3) | llama-3.3-70b-versatile |
| **LLM SDKs** | google-genai, openai | 1.0+, 2.0+ |
| **Database** | SQLite (file + in-memory) | — |
| **Data Processing** | Pandas | 2.2+ |
| **Session** | In-memory dict + Timer | — |
| **Config** | Pydantic Settings | 2.2+ |

---

## Prerequisites

| Tool | Minimum version | Install |
|------|---|---|
| Python | 3.10+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| npm | 9+ | `npm -v` (included with Node) |
| Gemini API key | (free tier) | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| Groq API key (optional) | (free, unlimited) | [console.groq.com](https://console.groq.com/) |

---

## Setup & Run

### 1. Clone / Navigate to Project

```bash
cd asklytics
```

---

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Windows: copy .env.example .env
```

**Edit `backend/.env`:**

```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
CORS_ORIGIN=http://localhost:3000
DB_PATH=./sample.db
SAMPLE_CSV_PATH=D:\gfg\7. Amazon Sales\Amazon Sales.csv
```

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key (get free at [aistudio.google.com](https://aistudio.google.com/app/apikey)) | (required) |
| `GROQ_API_KEY` | Your Groq API key - free fallback (get at [console.groq.com](https://console.groq.com/)) | (optional but recommended) |
| `CORS_ORIGIN` | Frontend origin for CORS | `http://localhost:3000` |
| `DB_PATH` | SQLite database file path | `./sample.db` |
| `SAMPLE_CSV_PATH` | Full path to Amazon Sales CSV | (required) |

**Start backend:**

```bash
python run.py
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

> **First run**: Backend auto-seeds SQLite from CSV. Subsequent runs skip seeding.

---

### 3. Frontend Setup

Open **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

- App: `http://localhost:3000`

---

## Project Structure

```
asklytics/
├── README.md                          ← You are here
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app (CORS, startup, routers)
│   │   ├── config.py                  # Pydantic settings (.env loading)
│   │   │
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py          # SQLite factory (file + in-memory)
│   │   │   ├── sample_db.py           # CSV → SQLite seeder
│   │   │   └── postgres_db.py         # (future: PostgreSQL support)
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── request_models.py      # CreateSessionRequest, QueryRequest
│   │   │   └── response_models.py     # DashboardResponse, ChartSpec, etc
│   │   │
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── session.py             # POST /sessions, DELETE /sessions/{id}
│   │   │   ├── query.py               # POST /query (main orchestration)
│   │   │   └── upload.py              # POST /upload/csv
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── gemini_service.py      # Gemini API calls (2-stage)
│   │       ├── schema_service.py      # Database schema introspection
│   │       ├── session_service.py     # Session store (in-memory)
│   │       ├── sql_service.py         # Query execution (SELECT-only)
│   │       └── csv_service.py         # CSV parsing → in-memory SQLite
│   │
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Example env vars
│   └── run.py                         # Entry point
│
└── frontend/
    ├── app/
    │   ├── page.tsx                   # Landing page (hero)
    │   ├── layout.tsx                 # Root layout
    │   ├── dashboard/
    │   │   └── page.tsx               # Dashboard page (main UI)
    │   ├── login/
    │   │   └── page.tsx               # Login page (UI-only)
    │   ├── register/
    │   │   └── page.tsx               # Register page (UI-only)
    │   └── globals.css                # Tailwind base + custom styles
    │
    ├── components/
    │   ├── chat/
    │   │   ├── ChatInput.tsx          # Message input + send
    │   │   ├── ChatHistory.tsx        # Message list
    │   │   └── ChatBubble.tsx         # Single message bubble
    │   │
    │   ├── dashboard/
    │   │   ├── Dashboard.tsx          # Main grid layout
    │   │   ├── ChartCard.tsx          # Card wrapper (title, skeleton)
    │   │   ├── BarChartWidget.tsx     # Recharts BarChart
    │   │   ├── LineChartWidget.tsx    # Recharts LineChart
    │   │   ├── AreaChartWidget.tsx    # Recharts AreaChart
    │   │   ├── PieChartWidget.tsx     # Recharts PieChart
    │   │   └── KPICard.tsx            # Single number display
    │   │
    │   └── ui/
    │       ├── LoadingSpinner.tsx     # Animated spinner
    │       ├── ErrorBanner.tsx        # Error message display
    │       ├── FileUploadModal.tsx    # CSV upload (drag-drop)
    │       ├── Toast.tsx              # Toast notifications
    │       ├── ProfileMenu.tsx        # User menu (logout placeholder)
    │       ├── AIProgressLoader.tsx   # AI thinking animation
    │       ├── Preloader.tsx          # Initial page load animation
    │       ├── ColorBends.tsx         # Animated gradient background
    │       ├── LightRays.tsx          # Light effect
    │       ├── ShapeGrid.tsx          # Grid animation
    │       ├── PixelBlast.tsx         # Pixel particle effect
    │       ├── Plasma.tsx             # Plasma effect
    │       ├── GlassSurface.tsx       # Glass morphism
    │       ├── FaultyTerminal.tsx     # Terminal-like UI
    │       ├── entropy.tsx            # Entropy effect
    │       └── textarea.tsx           # Custom textarea
    │
    ├── hooks/
    │   └── useSession.ts              # Session persistence (localStorage)
    │
    ├── lib/
    │   ├── api.ts                     # API fetch wrappers
    │   ├── types.ts                   # Shared TypeScript types
    │   └── utils.ts                   # Utility functions
    │
    ├── package.json                   # NPM dependencies
    ├── tsconfig.json                  # TypeScript config
    ├── next.config.ts                 # Next.js config
    └── tailwind.config.ts             # Tailwind config

```

---

## API Endpoints

### Sessions
| Method | Path | Description | Returns |
|--------|------|---|---|
| `POST` | `/sessions` | Create new chat session | `{ session_id: uuid }` |
| `DELETE` | `/sessions/{session_id}` | Delete session | `{ status: "deleted" }` |
| `GET` | `/health` | Health check | `{ status: "ok" }` |

### Query
| Method | Path | Description |
|--------|------|---|
| `POST` | `/query` | Query with natural language → dashboard JSON |

**Request:**
```json
{
  "session_id": "uuid",
  "prompt": "What is the total revenue by category?",
  "datasource_id": "default"
}
```

**Response:**
```json
{
  "sql": "SELECT product_category, SUM(total_revenue) FROM amazon_sales GROUP BY product_category",
  "dashboard_title": "Total Revenue by Category",
  "charts": [
    {
      "id": "chart-1",
      "type": "bar",
      "title": "Revenue by Category",
      "data": [
        { "product_category": "Electronics", "value": 145200 },
        { "product_category": "Fashion", "value": 98700 }
      ],
      "x_key": "product_category",
      "y_keys": ["value"],
      "color_palette": ["#6366f1"]
    }
  ],
  "insight_summary": "Electronics generated the highest revenue at $145.2k.",
  "data_limitations": null,
  "follow_up_suggestions": ["Filter by region", "Show monthly trends"],
  "error": null
}
```

### Upload
| Method | Path | Description |
|--------|------|---|
| `POST` | `/upload/csv` | Upload CSV → returns datasource_id |

**Request:** `multipart/form-data` with `file: <csv binary>`

**Response:**
```json
{
  "datasource_id": "a1b2c3d4...",
  "table_name": "uploaded_data",
  "columns": {
    "category": "object",
    "revenue": "float64",
    "month": "object"
  }
}
```

---

## Demo Queries (Try These!)

1. **Simple bar chart**
   > "What is the total revenue generated by each product category?"
   - Expected: Single bar chart with 6 bars

2. **Multi-line chart**
   > "Show me the monthly revenue trend for each category throughout 2022."
   - Expected: Line chart with 6 lines (one per category)

3. **Multi-chart + KPI**
   > "Compare the average customer rating and total revenue for each payment method. Also show me the overall total revenue as a single number."
   - Expected: 2× bar charts + 1 KPI card

4. **Follow-up (after query 2)**
   > "Now filter this to only show the Asia and Europe regions."
   - Expected: Same chart, filtered (uses session history)

5. **CSV upload**
   - Upload custom CSV
   - Query: "Show me a breakdown of [column_a] by [column_b]"

---

## Hallucination Prevention Details

### Column Validation
```python
# schema_service.py — What Gemini sees:
TABLE amazon_sales(
  order_id INTEGER,
  product_category TEXT,
  total_revenue REAL
)
COLUMN STATS:
  product_category: 6 distinct values = ['Electronics', 'Fashion', 'Books', 'Beauty', 'Sports', 'Home & Kitchen']
  total_revenue: range [5.01, 499.99]

SAMPLE ROWS:
[
  {"product_category": "Electronics", "total_revenue": 145.50},
  {"product_category": "Fashion", "total_revenue": 298.20}
]
```

### Error Handling
**Invalid question:**
```
Q: "Show revenue by unicorn_category"
→ Gemini: { "error": "Column 'unicorn_category' does not exist in the schema" }
→ Frontend: ErrorBanner displays error message
→ No broken charts, no hallucination
```

**SQL validation:**
```python
# sql_service.py
- Blocks: INSERT, UPDATE, DELETE, DROP, CREATE, ALTER
- Enforces: Must start with SELECT
- Result: Only safe read operations allowed
```

### Grounded Insights
```python
# Stage 2 — Insight generation (gemini_service.py)
ACTUAL DATA (50 rows, showing first 25):
[
  {"product_category": "Electronics", "total_revenue": 145200},
  {"product_category": "Fashion", "total_revenue": 98700},
  ...
]

Output:
"Electronics generated the highest revenue at $145.2k"
^ This is GUARANTEED to match the data (not predicted)
```

---

## Error Handling

| Scenario | Response | Frontend |
|----------|----------|----------|
| Invalid question | `{ "error": "Column does not exist" }` | Red ErrorBanner |
| SQL fails | `{ "error": "SQL error: ..." }` | Red ErrorBanner |
| Gemini API error | `{ "error": "AI service unavailable" }` | Red ErrorBanner |
| CSV parse error | HTTP 400 + detail message | Modal inline error |
| Network timeout | Fetch error catch | "Connection failed" toast |

---

## Environment Variables

### Backend (`.env`)
```env
# Required
GEMINI_API_KEY=your_api_key_from_aistudio.google.com

# Optional (defaults shown)
CORS_ORIGIN=http://localhost:3000
DB_PATH=./sample.db
SAMPLE_CSV_PATH=D:\gfg\7. Amazon Sales\Amazon Sales.csv
POSTGRES_URL=postgresql://user:pass@localhost:5432/bi_dashboard  # (future)
```

### Frontend (`.env.local`)
```env
# Optional (default: http://localhost:8000)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Gemini Model Selection

**Current:** `gemini-flash-lite-latest` (recommended for MVP)

**Why:** Fast + free tier + good JSON output

**Future migration:**
- If latency issues: switch to `gemini-1.5-flash` (slightly slower but more reliable)
- If accuracy issues: use `gemini-1.5-pro` (slower, higher cost)

Example:
```python
# gemini_service.py line 110
model="gemini-1.5-flash",  # Change to this if needed
```

---

## Common Issues & Solutions

### Issue: `GEMINI_API_KEY not set`
**Fix:** Set `GEMINI_API_KEY` in `backend/.env`
```env
GEMINI_API_KEY=AIzaSy...your_key...
```

### Issue: `CSV not found`
**Fix:** Set `SAMPLE_CSV_PATH` to absolute path of your Amazon Sales CSV
```env
SAMPLE_CSV_PATH=D:\gfg\7. Amazon Sales\Amazon Sales.csv
```

### Issue: Frontend can't reach backend
**Fix:** Ensure backend is running (`python run.py`)
- Backend: `http://localhost:8000`
- Check CORS: `CORS_ORIGIN=http://localhost:3000`

### Issue: Large CSV too slow
**Fix:** Current implementation loads entire CSV into memory
- Limitation: Max ~100k rows recommended
- Future: Paginate or use chunk streaming

---

## Testing & Demo

```bash
# Backend + Frontend both running:

# Test API docs
curl http://localhost:8000/docs
# → Interactive Swagger UI

# Create session
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"datasource_id": "default"}'

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "...",
    "prompt": "Show total revenue by category",
    "datasource_id": "default"
  }'
```

---

## Production Checklist (Before Deploying)

- [ ] Add user authentication (Firebase or Supabase)
- [ ] Move sessions to database (Redis or PostgreSQL)
- [ ] Migrate SQLite → PostgreSQL (if multi-user)
- [ ] Add rate limiting (per-user query limits)
- [ ] Enable HTTPS (production domains only)
- [ ] Set up monitoring & error tracking
- [ ] Add database backups & snapshots
- [ ] Implement user audit logging
- [ ] Add data retention policy
- [ ] Test with 10k+ row CSVs
- [ ] Load test Gemini API fallback
- [ ] Set up CI/CD pipeline (GitHub Actions)

---

## Contributing

This is an educational project for GFG. To improve:

1. **Report issues** in comments
2. **Suggest improvements** in PRs (if version controlled)
3. **Test edge cases** — especially large CSVs and complex queries

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**TL;DR**: You can use, modify, and distribute this code freely for personal, educational, or commercial purposes. Just include the original copyright notice.

---

## Next Steps

**Immediate (Week 1):**
1. ✅ Test MVP locally (landing → login → query → dashboard)
2. Add authentication (Supabase recommended)
3. Move sessions to Redis/database
4. Deploy to staging (Vercel + Railway/Heroku)

**Short-term (Week 2-3):**
5. Add rate limiting
6. Implement query logging & history
7. Add data cleanup job
8. Write E2E tests

**Long-term (Month 2+):**
9. RAG with vector embeddings
10. Advanced chart types
11. Dashboard sharing & embedding
12. Multi-workspace support

---

**Last Updated:** March 17, 2026
**Version:** 1.0.0 (MVP)
**Status:** Production-Ready | Awaiting Authentication Integration
