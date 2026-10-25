# Asklytics Upgrade Architecture & Implementation Plan
**Branch:** `feature/asklytics-upgrade` (Sub-branch)  
**Base:** `main`  
**Author:** AI Pair Programmer & @Ankan  

---

## 1. Executive Summary & Core Objective

Asklytics currently provides natural-language to SQL execution and interactive dashboard generation using a two-stage LLM pipeline (Gemini with Groq fallback), SQLite, and Next.js 14 / Recharts. 

While the MVP demonstrates functional text-to-SQL, real-world data and benchmark research (Spider 2.0, BIRD, AmbiSQL, P2SQL, ConDABench, VisEval) identify critical failure modes:
1. **Ungrounded Insights:** LLM prose can hallucinate numbers not supported by raw query results.
2. **Insecure SQL Validation:** Simple regex blacklists are vulnerable to prompt-to-SQL injection.
3. **Ambiguity Gaps:** Vague queries ("best product", "recent sales") receive silent guesses rather than explicit clarification.
4. **Follow-Up Context Decay:** Flat chat history loses structured filtering, metric, and dimensional state across turns.
5. **Misleading Visualizations:** Inappropriate chart choices (e.g., 40-slice pie charts, unordered line charts).
6. **Absence of Evaluation:** No automated metric to measure execution accuracy and hallucination rates.

This plan details the end-to-end upgrade roadmap to elevate Asklytics into an enterprise-grade, verifiable conversational analytics engine, along with a **strict sub-branch git strategy** to ensure stability before merging to `main`.

---

## 2. Strict Git Branching & Merge Protocol

To prevent destabilization of the production code on `main`, all work follows this protocol:

### Git Rules:
1. **Main Branch Protection:** NEVER push directly to `origin/main`.
2. **Sub-Branch Development:** All development is committed to `feature/asklytics-upgrade` (already created and checked out).
3. **Push Destination:** Only push to `origin feature/asklytics-upgrade`.
4. **Local Verification Gate:** Run full automated test suites (backend `pytest`, frontend `pnpm run build` / `npm test`) on the feature branch.
5. **Manual Merge:** The user verifies the live app in staging/local mode, then manually merges `feature/asklytics-upgrade` into `main` using:
   ```bash
   git checkout main
   git merge --no-ff feature/asklytics-upgrade
   git push origin main
   ```

---

## 3. Architecture & Upgrade Breakdown (10 Upgrades)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ASKLYTICS 2.0 PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  User Query ─────────► [2. Ambiguity & Vague Term Detector]                 │
│                                  │                                          │
│                         Ambiguous?                                          │
│                         ├── YES ──► Emit Clarification Chips UI             │
│                         └── NO  ──► Dual LLM Query Generation               │
│                                             │                               │
│                                    [3. Disagreement Signal]                 │
│                                     (Gemini vs Groq SQL)                    │
│                                             │                               │
│                                    [5. Structured State Manager]            │
│                                     (Metrics, Dimensions, Filters)          │
│                                             │                               │
│                                    [4. AST Safe SQL Layer]                  │
│                                     (sqlglot parse, column/table whitelist, │
│                                      read-only connection, row/time limits) │
│                                             │                               │
│                                    [Database Execution (SQLite/PG)]         │
│                                             │                               │
│                              ┌──────────────┴──────────────┐                │
│                              ▼                             ▼                │
│                 [6. Chart Validity Checker]   [1. Claim-Level Verifier]     │
│                  - VisEval heuristics          - Extract numeric claims     │
│                  - Auto-fix bad chart types    - Recompute against full data│
│                  - Fallback recommendations    - Mark Verified / Rejected   │
│                              │                             │                │
│                              └──────────────┬──────────────┘                │
│                                             ▼                               │
│                         [7. 'How I Got This' Audit & Trust Panel]           │
│                          - SQL & AST explanation, assumptions made          │
│                          - Rows scanned, latency, verification badge        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Upgrade 1: Claim-Level Insight Verification (InsightLens & ConDABench)
* **Problem:** Stage 2 prompts the LLM to write prose about query rows. LLMs frequently hallucinate exact figures, percentages, or trends.
* **Solution:**
  * Implement `claim_verifier.py`.
  * Parse generated `insight_summary` into individual factual claims using a claim segmentation parser.
  * Extract numerical quantities, comparisons ("increased by 15%", "highest is $45,200", "accounted for 32%").
  * Execute deterministic Python code against the complete query result set (`rows`) to independently compute each claim.
  * Tag claims: `[VERIFIED]`, `[UNVERIFIED]`, or `[CONTRADICTION]`.
  * If a contradiction is detected, either replace the faulty clause with calculated ground truth or drop the unverified claim with a warning.
  * Return verification metadata in the API response: `{ verified: true, claims: [{ text, status, computed_value }] }`.

---

### Upgrade 2: Ambiguity Detection & Clarification Chips (AmbiSQL & Sphinteract)
* **Problem:** Ambiguous business questions ("What is the best category?", "Show recent sales", "Who are the top customers?") cause the LLM to make arbitrary assumptions that lead to inaccurate conclusions.
* **Solution:**
  * Implement `ambiguity_service.py` to identify polysemic metrics, vague temporal intervals, and under-specified sorting criteria.
  * When detected, return a `ClarificationRequest` before running expensive queries:
    * E.g. *"By 'best category', do you mean by total revenue, order count, or average rating?"*
  * Frontend renders interactive **Clarification Chips** inside the chat UI.
  * Clicking a chip instantly resolves the query without requiring manual retyping.

---

### Upgrade 3: Cross-Model Disagreement as an Ambiguity Signal (VLDB 2026)
* **Problem:** Single models frequently display overconfidence on ambiguous prompts without detecting their own uncertainty.
* **Solution:**
  * Leverage existing Gemini 2.0 Flash and Groq (Llama 3.3 70B) configurations concurrently.
  * In Stage 1, run the planning prompt on both models in parallel via `asyncio.gather()`.
  * Compare normalized SQL ASTs using `sqlglot`.
  * If the two models generate structurally divergent logic (e.g., Gemini aggregates by `SUM(amount)` while Groq uses `COUNT(order_id)`), this triggers an ambiguity signal.
  * Present both interpretations to the user as options: *"Gemini interpreted this by Revenue, while Groq interpreted by Order Volume. Which would you like to view?"*

---

### Upgrade 4: Safe SQL AST & Execution Sandbox (Pedro et al. P2SQL)
* **Problem:** Regex filters (`_FORBIDDEN = re.compile(...)`) are easily bypassed by query obfuscation, subqueries, comments, or dialect-specific injection.
* **Solution:**
  * Integrate `sqlglot` for robust AST parsing.
  * Enforce strict AST validation:
    * Disallow everything that is not an `exp.Select`.
    * Whitelist table names against known database schemas.
    * Whitelist column names against verified table schema metadata.
    * Disallow system functions, attachments, and schema modifications.
  * Enforce database-level read-only connections:
    * SQLite URI: `file:{db_path}?mode=ro`
  * Add automatic query safety wrappers:
    * Hard `LIMIT 1000` injected into AST if no limit or higher limit is present.
    * Query execution timeout (e.g. 5.0 seconds max) to prevent denial of service.
    * Input sanitization for CSV-derived table definitions and string parameters.

---

### Upgrade 5: Structured Multi-Turn Conversation State (Memory Architectures)
* **Problem:** Current follow-ups pass raw chat strings into the prompt. The model frequently drops previous filters, changes aggregation levels unintentionally, or forgets previous context.
* **Solution:**
  * Implement `ConversationState` schema:
    ```json
    {
      "active_metric": "SUM(revenue)",
      "dimensions": ["category"],
      "filters": [{"column": "order_date", "op": ">=", "value": "2023-01-01"}],
      "group_by": ["category"],
      "order_by": [{"column": "revenue", "direction": "DESC"}],
      "limit": 10
    }
    ```
  * On follow-up questions (e.g., *"Now filter to just North America and break down by month"*), the LLM outputs a delta modification to the state rather than re-inventing the query from scratch.
  * The query is synthesized from the structured state, guaranteeing continuity.

---

### Upgrade 6: Chart Validity Checker (VisEval & Rethinking NL2VIS)
* **Problem:** LLMs often select illegible or invalid charts (e.g. pie charts with 35 categories, line charts on unordered nominal categories, scatter plots with 1 variable).
* **Solution:**
  * Implement `chart_validator.py` with VisEval heuristics:
    * **Pie Chart Rule:** If slices > 7, automatically convert to horizontal Bar Chart.
    * **Line Chart Rule:** Must have a continuous, temporal, or sequentially ordered x-axis (dates, timestamps, intervals); otherwise convert to Bar Chart.
    * **KPI Rule:** Dataset must contain exactly 1 row or aggregated scalar.
    * **Scatter Rule:** Must have 2 continuous numerical variables.
    * **Heatmap Rule:** Must have 2 discrete categorical axes and 1 continuous intensity metric.
  * Validate that `x_key`, `y_keys`, and `z_key` match returned SQL column names and have valid data types.
  * If invalid, automatically auto-repair the chart spec or suggest alternative visual encodings.

---

### Upgrade 7: "How I Got This" Audit & Trust Panel (InsightLens)
* **Problem:** Users are reluctant to trust black-box AI SQL and insights without visibility into execution and logic.
* **Solution:**
  * Add an expandable **"How I Got This"** drawer/panel on each dashboard widget.
  * Shows:
    1. **Exact SQL Query:** Syntax-highlighted, copyable, with formatting.
    2. **Assumptions Made:** Human-readable explanations (e.g., *"Filtered for completed orders only; assumed 'sales' refers to total price after discount"*).
    3. **Performance Metrics:** Rows scanned, execution time in milliseconds, memory impact.
    4. **Claim Verification Badges:** Visual indicator (e.g., *✓ All 3 figures verified against raw database rows*).
    5. **Confidence Rating:** High / Medium / Low based on schema match and model agreement.

---

### Upgrade 8: Enterprise Semantic Layer & Metric Glossary
* **Problem:** "Revenue", "Gross Margin", "AOV", and "Active User" mean different things to different stakeholders. Uncontrolled LLM generation leads to conflicting metrics.
* **Solution:**
  * Implement a lightweight, customizable semantic configuration (`semantic_layer.json` / UI dictionary).
  * Example definition:
    * `AOV`: `SUM(total_amount) / COUNT(DISTINCT order_id)`
    * `Gross Margin`: `(SUM(revenue) - SUM(cogs)) / SUM(revenue) * 100`
    * `Active Customer`: `Customers with at least 1 order in the last 90 days`
  * Provide standard metrics definitions to the Stage 1 system prompt, requiring the LLM to use the canonical formula whenever the business term appears.

---

### Upgrade 9: Automated Evaluation & Benchmark Harness (CIDR 2026)
* **Problem:** Changes to prompts or models can cause silent regressions. No quantitative benchmark exists to verify accuracy.
* **Solution:**
  * Build `backend/evaluation/`:
    * 100+ annotated gold-standard queries (Amazon dataset + curated Spider/BIRD subsets).
    * Evaluates:
      1. **Execution Accuracy (EX):** Does the generated SQL return the exact same result set as the gold SQL?
      2. **Insight Faithfulness Score:** Automated verification pass rate of generated insight text.
      3. **Clarification Trigger Rate:** Does the ambiguity detector correctly flag ambiguous test queries and pass unambiguous ones?
      4. **Latency & Token Efficiency:** Milliseconds per query and token usage.
    * Runnable via CLI: `python -m app.evaluation.run_benchmark` producing a clear accuracy report.

---

### Upgrade 10: Production Readiness & Platform Hardening
* **Problem:** Sessions live in memory; no persistent conversation storage; no rate limiting or tenant data isolation.
* **Solution:**
  * Complete Supabase/PostgreSQL conversation and user data persistence.
  * Enforce strict tenant isolation outside the LLM: data scopes injected at query boundary so tenant A cannot query tenant B's SQLite/Postgres tables.
  * Rate limiting with sliding window (FastAPI limiter).
  * Comprehensive automated test suite:
    * Backend unit & integration tests (`pytest`).
    * Frontend typecheck and build validation (`tsc --noEmit`, `next build`).

---

## 4. Four-Wave Implementation Roadmap

```
┌────────────────────────────────────────────────────────────────────────┐
│                        IMPLEMENTATION PHASES                           │
├────────────────────┬───────────────────────────────────────────────────┤
│ Wave 1: Trust &    │ • Safe SQL AST Layer (sqlglot + read-only DB)     │
│ Safety Core        │ • Claim-Level Insight Verifier (code ground-truth)│
│ (Week 1 / Phase 1) │ • 'How I Got This' UI Audit Panel                 │
├────────────────────┼───────────────────────────────────────────────────┤
│ Wave 2: Ambiguity  │ • Ambiguity Detection Service & Prompt Parser     │
│ & Visual Quality   │ • Cross-Model Disagreement Signal (Gemini + Groq) │
│ (Week 2 / Phase 2) │ • Chart Validity Checker (VisEval rules)          │
│                    │ • Clarification Chips UI Component                │
├────────────────────┼───────────────────────────────────────────────────┤
│ Wave 3: Memory     │ • Structured Conversation State (JSON state)      │
│ & Benchmarking     │ • 100+ Query Automated Evaluation Harness         │
│ (Week 3 / Phase 3) │ • Spider / BIRD / Amazon Benchmark Runner         │
├────────────────────┼───────────────────────────────────────────────────┤
│ Wave 4: Production │ • Semantic Layer & Metric Dictionary              │
│ & SaaS Platform    │ • Auth & Multi-tenant data isolation              │
│ (Week 4 / Phase 4) │ • PostgreSQL persistent sessions & Rate limits    │
│                    │ • Full Pytest & E2E Testing Suite                 │
└────────────────────┴───────────────────────────────────────────────────┘
```

---

## 5. Verification & Testing Checklist Before Merging to Main

Before initiating the final merge into `main`, the following test matrix must pass on `feature/asklytics-upgrade`:

- [ ] **SQL Security Tests:** All 15 injection payloads (comment injection, chained DROP, subquery exploits) blocked by `sqlglot`.
- [ ] **Read-Only SQLite URI:** Confirm write queries (`INSERT`, `UPDATE`) fail at the database level even if AST parsing was bypassed.
- [ ] **Claim Verification Tests:** Injected false numbers in test insights are caught and flagged with 100% accuracy.
- [ ] **Chart Validity Tests:** 40-slice pie chart auto-converts to horizontal bar chart; categorical line chart auto-converts to bar chart.
- [ ] **Cross-Model Disagreement:** Vague query triggers clarification chips in frontend UI.
- [ ] **Evaluation Harness:** Benchmark suite runs cleanly and generates `benchmark_report.json` with >80% EX on Amazon dataset.
- [ ] **Typecheck & Build:** `frontend/` builds with 0 errors (`pnpm run build` / `npm run build`).
- [ ] **Sub-Branch Push:** Changes pushed to `origin feature/asklytics-upgrade`.
- [ ] **Manual User Review:** User tests the running application locally and gives sign-off before manual merge to `main`.
