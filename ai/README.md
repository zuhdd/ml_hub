# AI Orchestrator

Connects an LLM (Claude) to the [backend](../backend) so business users can ask questions in plain English instead of calling fixed endpoints. This is Milestone 3 (Step 5) from the [project guide](../Project_Guide/README.md).

Rather than having the model generate free-form SQL, it is given **tool-use access to the backend's 4 existing endpoints** — churn risk, CLV, RMO customer counts, and single-customer lookup. It picks the right tool(s) for a question, and answers only from what the tools return (grounding). Every question, the tools called, and the final answer are logged to `../logs/audit.log`.

## Setup

Make sure the [backend](../backend) is already running on port 8000 (`curl localhost:8000/health` should return `{"status":"ok",...}`).

```bash
cd ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your own Anthropic API key (`ANTHROPIC_API_KEY=sk-ant-...`). Get one at https://console.anthropic.com/.

## Run

```bash
uvicorn main:app --reload --port 8001
```

(Port 8001, since the backend already uses 8000.)

## Try it

```bash
curl -X POST localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Which customers are most likely to churn?"}'

curl -X POST localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Tell me about customer R000000001"}'

curl -X POST localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Which RMO manages the most customers?"}'
```

Each response includes the answer plus which tool(s) were called. Check `../logs/audit.log` afterward to see the audit trail.
