export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

export async function login(backendUrl, rmoCode) {
  const base = backendUrl.trim().replace(/\/$/, "");
  const response = await fetch(`${base}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rmo_code: rmoCode }),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(body.detail || `Login failed (${response.status})`, response.status);
  }

  return { ...(await response.json()), backendUrl: base };
}

export async function adminLogin(backendUrl, password) {
  const base = backendUrl.trim().replace(/\/$/, "");
  const response = await fetch(`${base}/api/auth/admin-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(body.detail || `Login failed (${response.status})`, response.status);
  }

  const data = await response.json();
  return { token: data.token, role: "admin", backendUrl: base };
}

export async function getRmoDirectory(backendUrl, token) {
  const base = backendUrl.trim().replace(/\/$/, "");
  const response = await fetch(`${base}/api/admin/rmos`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(body.detail || `Request failed (${response.status})`, response.status);
  }

  return response.json();
}

// Consumes the ai orchestrator's SSE stream (POST /ask/stream). Events:
//   delta    - a chunk of the answer text to append
//   tool_call - a tool the model called, shown in the "how this was answered" panel
//   retract  - discard any delta text appended since the last tool_call/start
//              (the model narrated before calling a tool; that text wasn't the real answer)
//   done     - the final list of tool calls; stream is complete
//   error    - something went wrong server-side
export async function streamQuestion(aiUrl, question, token, viewRmoCode, history, { onDelta, onToolCall, onRetract, onDone, onError }) {
  const base = aiUrl.trim().replace(/\/$/, "");
  const response = await fetch(`${base}/ask/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ question, view_rmo_code: viewRmoCode || undefined, history }),
  });

  if (response.status === 401) {
    throw new ApiError("Session expired", 401);
  }
  if (!response.ok || !response.body) {
    throw new ApiError(`AI service returned ${response.status}`, response.status);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let boundary;
    while ((boundary = buffer.indexOf("\n\n")) !== -1) {
      const rawEvent = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);

      const eventLine = rawEvent.split("\n").find((l) => l.startsWith("event: "));
      const dataLine = rawEvent.split("\n").find((l) => l.startsWith("data: "));
      if (!eventLine || !dataLine) continue;

      const eventType = eventLine.slice("event: ".length);
      const data = JSON.parse(dataLine.slice("data: ".length));

      if (eventType === "delta") onDelta?.(data);
      else if (eventType === "tool_call") onToolCall?.(data);
      else if (eventType === "retract") onRetract?.();
      else if (eventType === "done") onDone?.(data.tool_calls);
      else if (eventType === "error") onError?.(data.message);
    }
  }
}
