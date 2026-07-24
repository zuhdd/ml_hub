# Frontend

A React + Vite single-page app for asking ML Hub a question in plain English and seeing the answer from the [ai](../ai) orchestrator, plus which tools were called to produce it. This is Milestone 5 (Step 7) from the [project guide](../Project_Guide/README.md).

Design: a Mississippi.gov-style layout (a prominent "ask a question" hero, example-question chips, a plain-language trust/how-it-works section, an organized footer) in a purple-and-white colorway inspired by Wema Bank's brand.

## Setup

```bash
cd frontend
npm install
```

## Run

Make sure the [backend](../backend) (port 8000) and [ai](../ai) orchestrator (port 8001) are already running, then:

```bash
npm run dev
```

Open the URL Vite prints (defaults to http://localhost:5173). If your AI service runs somewhere other than `http://localhost:8001`, click the "AI service" line under the ask bar to change it.

## Build

```bash
npm run build
```

Outputs a static production build to `dist/`.

## Structure

- `src/App.jsx` — top-level state (question, thread of turns, AI service URL) and layout composition
- `src/components/` — `Header`, `Hero` (headline + ask form + example chips), `HowItWorks`, `AnswerThread`/`Turn` (renders each Q&A turn plus its expandable tool-call panel), `Footer`
- `src/lib/api.js` — thin fetch wrapper around the ai orchestrator's `POST /ask`

## What it does

- Ask a question via the hero's ask bar, or click an example chip.
- Each turn shows the question, a loading state, then the answer.
- An expandable "How this was answered" panel shows every tool call (name + input) the orchestrator made — the traceability/auditability the project guide calls for, made visible in the UI instead of buried in a log file.
- Errors (AI service unreachable, database down, etc.) are shown inline instead of failing silently.
