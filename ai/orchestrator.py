import json
import os
from datetime import datetime, timezone

import anthropic
import jwt
from dotenv import load_dotenv

from tools import TOOLS, TOOL_FUNCTIONS

load_dotenv()

MODEL = "claude-opus-4-8"
MAX_ITERATIONS = 4

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "audit.log")

SYSTEM_PROMPT = """You are ML Hub, a business intelligence assistant for a bank's relationship management teams.

You help users answer questions about retail, corporate, and SME customers using the tools provided. Rules:
- Only answer using data returned by the tools. Never invent customer names, scores, or figures from your own knowledge.
- Use the fewest tool calls needed to answer the question.
- If the question cannot be answered with the available tools, say so plainly instead of guessing.
- When you present customer data, refer to customers by their CIF, since that is how the bank identifies them.
- Keep answers concise and business-friendly, not a raw data dump.
- When you need to call a tool, call it directly with no preceding text. Save all narrative text for your final answer, after tool results come back.
- The person asking may be a relationship manager (always scoped to their own customers) or an admin (who may be viewing one specific RMO's book, or the whole bank at once). The scope is applied automatically to every tool call - phrase your answers naturally for whichever is in effect, without assuming it's always "your" customers.
- The conversation may include earlier turns. Use them to resolve follow-up questions (e.g. "is that customer eligible for lending?", "what about just the SME ones?") - but always call a tool again to get current data rather than trusting your own earlier answer, since the underlying data can change between turns."""


def _run_tool(name: str, tool_input: dict, auth_header: str, rmo_code: str | None):
    func = TOOL_FUNCTIONS.get(name)
    if func is None:
        return {"error": f"Unknown tool '{name}'"}
    return func(auth_header, rmo_code, **tool_input)


def _principal_label(auth_header: str, rmo_code: str | None) -> str:
    """Best-effort label of who asked, for the audit log. Not a security
    check - the backend independently verifies the token on every call."""
    try:
        token = auth_header.removeprefix("Bearer ")
        payload = jwt.decode(token, options={"verify_signature": False})
        if payload.get("role") == "admin":
            return f"admin (viewing {rmo_code})" if rmo_code else "admin (viewing all RMOs)"
        return f"{payload.get('rmo_code')} ({payload.get('rmo_name')})"
    except Exception:
        return "unknown"


def _log(question: str, tool_calls: list, answer: str, principal_label: str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "principal": principal_label,
        "question": question,
        "tool_calls": tool_calls,
        "answer": answer,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def ask(question: str, auth_header: str, rmo_code: str | None = None, history: list | None = None) -> dict:
    client = anthropic.Anthropic()
    messages = [*(history or []), {"role": "user", "content": question}]
    tool_calls_made = []

    for _ in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            break

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = _run_tool(block.name, block.input, auth_header, rmo_code)
                tool_calls_made.append({"tool": block.name, "input": block.input})
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )
        messages.append({"role": "user", "content": tool_results})

    answer = next(
        (block.text for block in response.content if block.type == "text"), ""
    )

    _log(question, tool_calls_made, answer, _principal_label(auth_header, rmo_code))

    return {"answer": answer, "tool_calls": tool_calls_made}


def ask_stream(question: str, auth_header: str, rmo_code: str | None = None, history: list | None = None):
    """Same tool-use loop as ask(), but yields ("delta", text) as the final
    answer is generated so the frontend can render it token-by-token. Yields
    ("tool_call", {...}) as each tool is called, and ("done", {...}) at the end.

    `history` is the prior turns of this conversation (plain {"role", "content"}
    text pairs, not the tool_use scaffolding) so follow-up questions like "is
    that customer eligible for lending?" can resolve what "that customer" means."""
    client = anthropic.Anthropic()
    messages = [*(history or []), {"role": "user", "content": question}]
    tool_calls_made = []
    answer_parts = []

    for _ in range(MAX_ITERATIONS):
        parts_before = len(answer_parts)
        with client.messages.stream(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        ) as stream:
            for event in stream:
                if event.type == "content_block_delta" and event.delta.type == "text_delta":
                    answer_parts.append(event.delta.text)
                    yield ("delta", event.delta.text)
            final_message = stream.get_final_message()

        if final_message.stop_reason != "tool_use":
            break

        # Any text streamed this iteration was preamble before a tool call
        # (e.g. "let me check that"), not the real answer - discard it.
        if len(answer_parts) > parts_before:
            del answer_parts[parts_before:]
            yield ("retract", None)

        messages.append({"role": "assistant", "content": final_message.content})

        tool_results = []
        for block in final_message.content:
            if block.type == "tool_use":
                result = _run_tool(block.name, block.input, auth_header, rmo_code)
                tool_calls_made.append({"tool": block.name, "input": block.input})
                yield ("tool_call", {"tool": block.name, "input": block.input})
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )
        messages.append({"role": "user", "content": tool_results})

    answer = "".join(answer_parts)
    _log(question, tool_calls_made, answer, _principal_label(auth_header, rmo_code))
    yield ("done", {"tool_calls": tool_calls_made})
