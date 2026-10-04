# AI Banking System — Render Migration, RAG Architecture & Code Fixes Documentation

This document provides a complete, file-by-file technical overview of the issues encountered during the cloud migration from GCP VM to Render Cloud, their root cause analysis, and all architectural and feature upgrades implemented across the codebase.

---

## Table of Contents
1. [Problem Summary](#1-problem-summary)
2. [Root Cause Analysis](#2-root-cause-analysis)
3. [Summary of Modified & New Files](#3-summary-of-modified--new-files)
4. [File-by-File Detailed Changes](#4-file-by-file-detailed-changes)
   - [backend/app/seeder.py](#1-backendappseederpy)
   - [backend/app/main.py](#2-backendappmainpy)
   - [backend/app/services/statement_parser.py](#3-backendappservicesstatement_parserpy)
   - [backend/app/ai/financial_health.py](#4-backendappaifinancial_healthpy)
   - [backend/app/ai/advisor.py](#5-backendappaiadvisorpy)
   - [frontend/src/pages/Dashboard.jsx & Components](#6-frontendsrcpagesdashboardjsx--components)
5. [System Architecture Flow](#5-system-architecture-flow)
6. [Live Endpoints & Verification Results](#6-live-endpoints--verification-results)

---

## 1. Problem Summary

When migrating and scaling the platform on **Render Cloud**, the following issues were identified and resolved:
1. **Empty Initial Database on Render:**
   - Fresh PostgreSQL instances had empty tables (`Total Balance: $0`, `Monthly Income: $0`, `Monthly Expenses: $0`, `Savings: $0`), causing the Demo Account (`Robert Wilson`) to appear blank unless seeded automatically.
2. **Multi-User Isolation & Statement-Driven Analytics:**
   - Newly registered users needed strict data isolation so that demo account data (`Robert Wilson`) never leaked into custom accounts.
   - Uploading a bank statement (`PDF`, `CSV`, `XLSX`, `DOCX`, `TXT`) needed to immediately populate all dashboard KPIs, charts, and AI Spending Insights strictly from the uploaded document.
   - Uploading a bank statement with **$0 Balance and $0 Savings** needed to accurately classify Financial Health as **`Poor` (`20/100`)** rather than `Average`.
3. **Personalized User URLs (`/<firstname>-dashboard`):**
   - Users required dynamic, personalized routes based on their registered first name (e.g., `/aaditya-dashboard`, `/aaditya-dashboard/ai-advisor`, `/robert-dashboard`).
4. **Demo Account Hard-Refresh (`F5`) Auto-Restore:**
   - Clearing data in the demo account sets balances to `$0`, but pressing `F5` (Hard Refresh) needed to automatically restore Robert Wilson's `$20,000` balance and transaction history.
5. **Account Deletion & Demo Protection Guardrails:**
   - Users needed both a UI **Delete Account** button (with password verification) and a **3-step conversational AI Advisor deletion flow** (persuasion -> password prompt -> verified deletion & redirect to Sign Up), while protecting the Demo Account with the admin password (`robert@123`).

---

## 2. Root Cause Analysis

1. **Empty PostgreSQL Schema on Cold Start:**
   - Running `Base.metadata.create_all(bind=engine)` only creates database tables without inserting baseline demo records.
   - Moving seeding logic inside `backend/app/main.py` on `@app.on_event("startup")` guarantees that Demo User `1` (**Robert Wilson**) is always initialized while keeping all other user accounts strictly isolated.
2. **Zero-Transaction Bank Statement PDFs:**
   - Certain bank statements (such as summary statements or newly opened accounts with `Opening Balance: INR 0.00` and `Closing Balance: INR 0.00`) contain `"No transactions found"` in the ledger section.
   - Enhancing `statement_parser.py` to extract summary-level balances (`Closing Balance`, `Opening Balance`, `Total Credit Amount`, `Total Debit Amount`) ensures zero-balance PDFs are accurately recorded as `$0` uploaded statements.
3. **Zero-Income Financial Health Scoring:**
   - Previously, when `monthly_income == 0` and `monthly_expenses == 0`, the expense ratio defaulted to `0`, granting `40` points plus `10` base savings points (`50/100 = Average`).
   - Adding an explicit zero-liquidity guardrail in `financial_health.py` ensures that when `total_balance <= 0` and `monthly_income <= 0`, the health score is **`20` (`Poor`)**.
4. **Gemini API Resilience & RAG Grounding:**
   - Initializing the LLM client lazily and injecting retrieved PostgreSQL aggregates into the prompt ensures zero-hallucination financial advice with a deterministic mathematical fallback if the external API quota is reached.

---

## 3. Summary of Modified & New Files

| # | File Path | Status | Purpose |
| :--- | :--- | :---: | :--- |
| 1 | `backend/app/main.py` | **MODIFIED** | Startup schema migrations, demo seeding, `/upload-statement`, `/financial-summary`, `/spending-insights`, `/reset-demo`, and `/delete-account` endpoints |
| 2 | `backend/app/services/statement_parser.py` | **MODIFIED** | Multi-format bank statement parser (`PDF`, `CSV`, `XLSX`, `DOCX`, `TXT`) with Indian `INR`/`Cr`/`Dr` regex and summary balance extraction |
| 3 | `backend/app/ai/financial_health.py` | **MODIFIED** | Deterministic Financial Health Score (`0–100`) with `Poor` status guardrail when Balance = `$0` and Savings = `$0` |
| 4 | `backend/app/ai/advisor.py` | **MODIFIED** | Grounded Financial RAG engine with Google Gemini (`gemini-2.0-flash`) and 3-stage conversational account deletion workflow |
| 5 | `frontend/src/pages/Dashboard.jsx` | **MODIFIED** | Personalized `/<username>-dashboard` controller, `F5` hard-refresh demo auto-restore, and statement-only data binding |
| 6 | `frontend/src/components/AIRecommendation.jsx` | **MODIFIED** | Statement-driven AI Spending Insights and Category Breakdown UI |

---

## 4. File-by-File Detailed Changes

### 1. `backend/app/seeder.py`
- **Purpose:** Provides automated database seeding inside the backend container on Render.
- **Key Functions:**
  - Generates realistic baseline transactions for Demo User **Robert Wilson** (Salary, Housing, Utilities, Food, Transport, Entertainment, Shopping).
  - Resets PostgreSQL primary-key sequences (`setval`) to prevent ID collisions when new users sign up.

---

### 2. `backend/app/main.py`
- **Startup Hook & Schema Migrations:**
  - Automatically creates tables, applies safe `ALTER TABLE` migrations (`password_hash`, `statement_type`), and seeds Demo User `1` (`Robert Wilson`) on startup.
- **Statement-Driven Analytics Endpoints:**
  - `POST /users/{user_id}/upload-statement`: Parses uploaded files, updates account balances, replaces prior statement transactions, and marks the account as statement-backed.
  - `GET /users/{user_id}/financial-summary`: Computes `total_balance`, `monthly_income`, `monthly_expenses`, `savings`, and `health` strictly from the user's own account and statement records.
  - `GET /users/{user_id}/spending-insights`: Generates personalized RAG insights and category breakdowns strictly from the user's parsed transactions (including critical liquidity alerts when Balance = `$0`).
- **Demo Reset & Account Deletion Endpoints:**
  - `POST /users/1/reset-demo`: Restores Robert Wilson's demo account to `$20,000.00` balance, `$8,500.00` monthly income, `$3,350.00` expenses, and `$5,150.00` savings.
  - `POST /users/{user_id}/delete-account`: Verifies user password (or `robert@123` admin password for Demo User `1`) and permanently deletes the user's account and transactions.

---

### 3. `backend/app/services/statement_parser.py`
- **Multi-Format Ingestion:** Supports `.pdf`, `.csv`, `.xlsx`, `.docx`, and `.txt` statements.
- **Summary Balance Fallback:** Extracts `Closing Balance`, `Opening Balance`, `Total Credit Amount`, and `Total Debit Amount` from summary-only PDF statements (even when `No transactions found` appears in the table), ensuring `$0.00` statements are accurately reflected on the dashboard.

---

### 4. `backend/app/ai/financial_health.py`
- **Zero-Liquidity Check:**
  ```python
  if total_balance <= 0 and monthly_income <= 0:
      return {
          "score": 20 if monthly_expenses == 0 else 10,
          "status": "Poor",
          "savings_rate": 0.0,
          "expense_ratio": 100.0 if monthly_expenses > 0 else 0.0,
      }
  ```
  Guarantees that an account with `$0` Total Balance and `$0` Savings receives a **`Poor`** Financial Health rating instead of `Average`.

---

### 5. `backend/app/ai/advisor.py`
- **RAG Context Injection:** Injects the user's real-time balance, income, expenses, savings rate, and top spending categories into Google Gemini (`gemini-2.0-flash`).
- **Conversational Account Deletion State Machine:**
  1. First deletion request -> Persuades the user to stay by highlighting financial insights.
  2. Second confirmation -> Prompts the user to enter their account password (or `robert@123` for the demo account).
  3. Password verification -> Deletes the account and triggers automatic frontend redirection to `/login?mode=register`.

---

### 6. `frontend/src/pages/Dashboard.jsx` & Components
- **Browser Reload Detection (`isBrowserReload()`):** Detects `F5` / hard refresh on the Demo Account (`user.id === 1`) and calls `resetDemoData(1)` before fetching dashboard metrics.
- **Strict User Data Isolation:** Removed all hardcoded `Robert Wilson` fallback strings and demo KPI defaults for registered users.

---

## 5. System Architecture Flow

```text
[ User Browser / React SPA (Render Static Site) ]
          |
          v (HTTPS REST API)
[ Render Web Service (FastAPI Backend) ]
          |
          +---> On Startup: Runs Schema Migrations & Seeds Demo User 1 (Robert Wilson)
          |
          +---> Statement Upload Pipeline (statement_parser.py)
          |           |
          |           v
          |     Extracts Transactions + Summary Closing Balance (PDF/CSV/XLSX/DOCX)
          |     Categorizes Merchants & Stores in PostgreSQL
          |
          +---> Financial RAG Engine (advisor.py + financial_health.py)
                      |
                      +---> Retrieves Real User Ledger Aggregates from PostgreSQL
                      +---> Computes Health Score (0-100: Poor / Average / Good)
                      +---> Grounds Google Gemini 2.0 Flash Responses in Real User Data
```

---

## 6. Live Endpoints & Verification Results

| Endpoint | Method | Status | Description |
| :--- | :---: | :---: | :--- |
| `/auth/register` | `POST` | `200 OK` | Creates isolated user account & routes to `/<firstname>-dashboard` |
| `/auth/demo-login` | `POST` | `200 OK` | Logs into Robert Wilson Demo Account (`/robert-dashboard`) with `$20,000` balance |
| `/users/{id}/upload-statement` | `POST` | `200 OK` | Parses `PDF`/`CSV`/`XLSX`/`DOCX` statements and updates user ledger |
| `/users/{id}/financial-summary` | `GET` | `200 OK` | Returns statement-grounded Balance, Income, Expenses, Savings, and Health Status |
| `/users/{id}/spending-insights` | `GET` | `200 OK` | Returns statement-grounded AI Spending Insights & Category Breakdown |
| `/users/1/reset-demo` | `POST` | `200 OK` | Automatically restores Demo Account to `$20,000` on hard refresh (`F5`) |
| `/users/{id}/delete-account` | `POST` | `200 OK` | Verifies password (`robert@123` for demo) and deletes user account |
| `/ai/chat` | `POST` | `200 OK` | Grounded RAG Financial Advisor + 3-stage conversational account deletion |
