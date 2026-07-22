import json
import os
from datetime import datetime, timezone

import anthropic
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
- Keep answers concise and business-friendly, not a raw data dump."""


def _run_tool(name: str, tool_input: dict):
    func = TOOL_FUNCTIONS.get(name)
    if func is None:
        return {"error": f"Unknown tool '{name}'"}
    return func(**tool_input)


def _log(question: str, tool_calls: list, answer: str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "tool_calls": tool_calls,
        "answer": answer,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def ask(question: str) -> dict:
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": question}]
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
                result = _run_tool(block.name, block.input)
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

    _log(question, tool_calls_made, answer)

    return {"answer": answer, "tool_calls": tool_calls_made}
