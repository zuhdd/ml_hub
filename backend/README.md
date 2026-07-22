# Backend

A minimal FastAPI service that connects to the `ML_HUB_DEMO` SQL Server warehouse and answers a fixed set of business questions over HTTP. This is Milestone 2 (Basic Query Layer) from the [project guide](../Project_Guide/README.md) — no natural language handling yet, just a few named, parameterized, read-only queries.

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your SQL Server connection details (the values from the Docker container setup work as-is: server `localhost`, port `1433`, database `ML_HUB_DEMO`, user `sa`, and the SA password you set when creating the container).

## Run

```bash
uvicorn main:app --reload --port 8000
```

Interactive API docs: http://localhost:8000/docs

## Endpoints

| Endpoint | Description |
|---|---|
| `GET /health` | Confirms the service is up and can reach the database |
| `GET /api/high-churn-risk?limit=20` | Top customers by predicted churn score |
| `GET /api/high-clv?limit=20` | Top customers by CLV score |
| `GET /api/rmo-customer-counts` | Customer count per relationship manager |
| `GET /api/customers/{cif}` | A single customer's profile plus churn, CLV, fraud, and lending scores |
