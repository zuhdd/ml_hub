import { useEffect, useState } from "react";
import Header from "./components/Header";
import ChatPanel from "./components/ChatPanel";
import ChatInput from "./components/ChatInput";
import Login from "./components/Login";
import RmoDirectory from "./components/RmoDirectory";
import { streamQuestion } from "./lib/api";

const SESSION_KEY = "mlhub.session";
const THREAD_KEY = "mlhub.thread";
const MAX_STORED_MESSAGES = 100;

function loadSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY));
  } catch {
    return null;
  }
}

function loadStoredMessages() {
  try {
    const parsed = JSON.parse(localStorage.getItem(THREAD_KEY) ?? "[]");
    if (!Array.isArray(parsed)) return [];
    // A message still "loading"/"streaming" means the page closed mid-request -
    // that request is gone now, so surface it as interrupted rather than
    // showing a spinner that will never resolve.
    return parsed.map((m) =>
      m.status === "loading" || m.status === "streaming"
        ? { ...m, status: "error", error: "Interrupted — the page was closed or reloaded before this finished." }
        : m
    );
  } catch {
    return [];
  }
}

const initialMessages = loadStoredMessages();
let nextId = initialMessages.reduce((max, m) => Math.max(max, m.id), 0) + 1;

const MAX_HISTORY_TURNS = 20;

function buildHistory(messages) {
  return messages
    .filter((m) => m.role === "user" || m.status === "done")
    .map((m) => ({ role: m.role, content: m.content }))
    .slice(-MAX_HISTORY_TURNS);
}

function App() {
  const [session, setSession] = useState(loadSession());
  const [question, setQuestion] = useState("");
  const [aiUrl, setAiUrl] = useState("http://localhost:8001");
  const [messages, setMessages] = useState(initialMessages);
  const [loading, setLoading] = useState(false);
  const [viewScope, setViewScope] = useState(null);
  const [showDirectory, setShowDirectory] = useState(false);

  useEffect(() => {
    try {
      localStorage.setItem(THREAD_KEY, JSON.stringify(messages.slice(-MAX_STORED_MESSAGES)));
    } catch {
      // storage full or unavailable - not critical, just skip persisting
    }
  }, [messages]);

  function handleLogin(data) {
    localStorage.setItem(SESSION_KEY, JSON.stringify(data));
    setSession(data);
  }

  function handleLogout() {
    localStorage.removeItem(SESSION_KEY);
    localStorage.removeItem(THREAD_KEY);
    setSession(null);
    setMessages([]);
    setViewScope(null);
  }

  function updateMessage(id, patch) {
    setMessages((prev) =>
      prev.map((m) => (m.id === id ? { ...m, ...(typeof patch === "function" ? patch(m) : patch) } : m))
    );
  }

  async function runQuestion(q) {
    const trimmed = q.trim();
    if (!trimmed || loading || !session) return;

    const history = buildHistory(messages);

    const userId = nextId++;
    const assistantId = nextId++;
    setMessages((prev) => [
      ...prev,
      { id: userId, role: "user", content: trimmed },
      { id: assistantId, role: "assistant", status: "loading", content: "", toolCalls: [] },
    ]);
    setQuestion("");
    setLoading(true);

    try {
      await streamQuestion(aiUrl, trimmed, session.token, viewScope?.RmoCode, history, {
        onDelta: (text) =>
          updateMessage(assistantId, (m) => ({ status: "streaming", content: m.content + text })),
        onToolCall: (call) => updateMessage(assistantId, (m) => ({ toolCalls: [...m.toolCalls, call] })),
        onRetract: () => updateMessage(assistantId, { content: "" }),
        onDone: (toolCalls) => updateMessage(assistantId, { status: "done", toolCalls }),
        onError: (message) => updateMessage(assistantId, { status: "error", error: message }),
      });
    } catch (err) {
      if (err.status === 401) {
        updateMessage(assistantId, { status: "error", error: "Your session expired. Please log in again." });
        handleLogout();
      } else {
        updateMessage(assistantId, {
          status: "error",
          error: `Could not reach the AI service at ${aiUrl}. Is it running? (${err.message})`,
        });
      }
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    runQuestion(question);
  }

  if (!session) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <>
      <Header
        onNewChat={() => setMessages([])}
        session={session}
        onLogout={handleLogout}
        viewScope={viewScope ? { rmo_code: viewScope.RmoCode, rmo_name: viewScope.RmoName } : null}
        onBrowseRmos={() => setShowDirectory(true)}
        onClearScope={() => setViewScope(null)}
      />
      <ChatPanel messages={messages} onPickExample={(q) => runQuestion(q)} />
      <ChatInput
        value={question}
        onChange={setQuestion}
        onSubmit={handleSubmit}
        loading={loading}
        aiUrl={aiUrl}
        onAiUrlChange={setAiUrl}
      />
      {showDirectory && (
        <RmoDirectory
          backendUrl={session.backendUrl}
          token={session.token}
          onClose={() => setShowDirectory(false)}
          onSelect={(rmo) => {
            setViewScope(rmo);
            setShowDirectory(false);
          }}
        />
      )}
    </>
  );
}

export default App;
