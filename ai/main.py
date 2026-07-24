import json
from typing import List, Literal, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from orchestrator import ask, ask_stream

app = FastAPI(title="ML Hub AI Orchestrator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_HISTORY_TURNS = 20


class HistoryTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class Question(BaseModel):
    question: str
    view_rmo_code: Optional[str] = None
    history: List[HistoryTurn] = []

    def history_dicts(self) -> list:
        # Cap server-side too, regardless of what the client sends, to bound
        # cost/latency on every request.
        return [h.model_dump() for h in self.history[-MAX_HISTORY_TURNS:]]


def _require_auth(authorization: Optional[str]) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return authorization


@app.post("/ask")
def post_ask(body: Question, authorization: Optional[str] = Header(None)):
    auth_header = _require_auth(authorization)
    return ask(body.question, auth_header, body.view_rmo_code, body.history_dicts())


def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.post("/ask/stream")
def post_ask_stream(body: Question, authorization: Optional[str] = Header(None)):
    auth_header = _require_auth(authorization)

    def generate():
        try:
            for event, payload in ask_stream(body.question, auth_header, body.view_rmo_code, body.history_dicts()):
                yield _sse(event, payload)
        except Exception as exc:
            yield _sse("error", {"message": str(exc)})

    return StreamingResponse(generate(), media_type="text/event-stream")
