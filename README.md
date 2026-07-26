# ML Hub

An AI assistant that lets a bank's relationship managers ask questions about their customers in plain English ; churn risk, lifetime value, fraud signals, lending eligibility and default risk, product recommendations and get answers that are grounded in a real warehouse, scoped to exactly who's allowed to see what, and fully auditable.

This is an MVP demo, not a production banking system. The synthetic data and the deliberately simplified login are called out explicitly below so nothing here is dressed up to look more real than it is.

## The one architectural decision that matters most

**The AI never writes SQL and never touches the database directly** It can only call a small, fixed set of pre-approved functions; get churn risk, get CLV, get lending eligibility, look up one customer, list RMOs. That trade-off (less flexible than free-form query generation) makes an entire category of risk structurally impossible instead of merely discouraged by a prompt.

## What's actually here

| Layer | Folder | What it does |
|---|---|---|
| Data | `Project_Guide/sql/` | SQL Server warehouse — 200,000 customers (100,000 original + 100,000 added by the ML pipeline), dimension tables (customers, branches, RMOs, products), and fact tables for every model output |
| Backend | [`backend/`](backend) | FastAPI service exposing fixed, read-only, parameterized queries — every one scoped server-side by the logged-in RMO (or admin's chosen scope) |
| AI orchestrator | [`ai/`](ai) | Claude, restricted to tool-calling against the backend, with streaming responses, conversation memory, and a full audit log |
| Frontend | [`frontend/`](frontend) | A React chat interface — login, streaming answers, markdown rendering, an expandable "how this was answered" panel per message |
| ML | [`ml/`](ml) | Jupyter notebooks that train real models (not formulas) on the original 100,000 customers and score a second cohort of 100,000 new ones |

## Quickstart

**1. Start SQL Server and load the warehouse**

```bash
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=<your-password>" \
  -p 1433:1433 --name sqlserver -d mcr.microsoft.com/mssql/server:2022-latest

# then run Project_Guide/sql/ml_hub_warehouse.sql against it, e.g.:
docker cp Project_Guide/sql/ml_hub_warehouse.sql sqlserver:/tmp/
docker exec sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P '<your-password>' -C -i /tmp/ml_hub_warehouse.sql
```

**2. Backend** (port 8000)

```bash
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your SQL Server details, a JWT_SECRET, and an ADMIN_PASSWORD
uvicorn main:app --reload --port 8000
```

**3. AI orchestrator** (port 8001)

```bash
cd ai && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8001
```

**4. Frontend** (port 5173)

```bash
cd frontend && npm install && npm run dev
```

Open http://localhost:5173. Log in as any RMO (`RMO001` through `RMO200`, no password — see [Login](#login--access-control) below), or as admin with the password you set in `backend/.env`.

## Login & access control

- **RMO login** — enter an RMO code (`RMO001`–`RMO200`). No password: this is a demo identifier for row-level access, not real authentication. You'll only ever see the ~500–1,065 customers assigned to that RMO.
- **Admin login** — a shared password (set as `ADMIN_PASSWORD` in `backend/.env`). Grants bank-wide access, plus a "Browse RMOs" directory to scope the chat to any specific RMO's book.
- Every query is scoped **server-side**, not by the AI's judgment — an RMO can't see past their own book no matter what they ask, and an admin's chosen scope is injected into every tool call automatically.

## Project structure

```
ml_hub/
├── Project_Guide/     # original planning docs, SQL warehouse script, data dictionary
├── backend/           # FastAPI - auth, RLS-scoped queries
├── ai/                # Claude orchestrator - tool-use, streaming, conversation memory, audit log
├── frontend/          # React chat UI
├── ml/                # Jupyter notebooks - trained models, second-customer-cohort pipeline
└── logs/              # audit.log - every question, tool call, and answer, by who asked
```

## What each layer actually guarantees

- **Grounding** — every answer comes from a tool result just fetched, never from the model's own memory.
- **Row-level security** — enforced by the backend's SQL, not by asking the AI nicely.
- **Audit trail** — `logs/audit.log` records every question, every tool call (with parameters), the answer, and who asked, for every request through the AI layer.
- **Conversation memory** — follow-up questions ("is *that* customer eligible for lending?") resolve against prior turns, with fresh tool calls each time rather than trusting stale answers.

## The ML layer

Five notebooks in [`ml/`](ml) train real scikit-learn models (not the warehouse's original hand-written formulas) on the first 100,000 customers as ground truth, then score a second, newly-generated cohort of 100,000 customers and write the predictions straight into the live warehouse — churn, CLV, fraud, lending eligibility + default risk, and product recommendations. See `ml/README.md` for the full pipeline, run order, and an honest table of which models actually found learnable signal and which didn't.

## Tech stack

Python (FastAPI, pymssql, scikit-learn, pandas, Jupyter), React + Vite, Microsoft SQL Server, Claude (Anthropic API).

## Known limitations — said out loud, not discovered later

- The customer data and every model score are **synthetic** — generated by formulas (or, for the second cohort, models trained on those formulas). None of it reflects real customer behavior.
- RMO login has no password by design; admin login uses a single shared password. Neither is production-grade authentication.
- No rate limiting, no production auth infrastructure, no real historical outcomes feeding the ML models yet.

This is an MVP that proves the pattern — safe, grounded, auditable AI over a real warehouse — not a finished banking product.
