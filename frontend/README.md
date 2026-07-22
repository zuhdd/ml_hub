# Frontend

A single self-contained page (no build step, no framework) that lets a business user ask a question in plain English and see the answer from the [ai](../ai) orchestrator, plus which tools were called to produce it. This is Milestone 5 (Step 7) from the [project guide](../Project_Guide/README.md).

## Setup

None. It's one HTML file with inline CSS/JS.

## Run

Make sure the [backend](../backend) (port 8000) and [ai](../ai) orchestrator (port 8001) are already running, then serve this folder:

```bash
cd frontend
python3 -m http.server 3000
```

Open http://localhost:3000. If your AI service runs somewhere other than `http://localhost:8001`, change it in the "AI service URL" field at the top of the page.

## What it does

- Text box to ask a question, plus example question chips for the demo.
- Shows the assistant's answer.
- Expandable "How this was answered" panel showing every tool call (name + input) the orchestrator made — this is the traceability/auditability the project guide calls for, made visible in the UI.
- Errors (AI service unreachable, database down, etc.) are shown inline instead of failing silently.
