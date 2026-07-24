import { useState } from "react";
import { adminLogin, login } from "../lib/api";
import styles from "./Login.module.css";

export default function Login({ onLogin }) {
  const [mode, setMode] = useState("rmo"); // "rmo" | "admin"
  const [rmoCode, setRmoCode] = useState("");
  const [password, setPassword] = useState("");
  const [backendUrl, setBackendUrl] = useState("http://localhost:8000");
  const [showSettings, setShowSettings] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const isAdmin = mode === "admin";
  const canSubmit = isAdmin ? password.trim() : rmoCode.trim();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!canSubmit || loading) return;
    setLoading(true);
    setError("");
    try {
      const data = isAdmin
        ? await adminLogin(backendUrl, password.trim())
        : await login(backendUrl, rmoCode.trim());
      onLogin(data);
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  function switchMode(next) {
    setMode(next);
    setError("");
    setRmoCode("");
    setPassword("");
  }

  return (
    <div className={styles.wrap}>
      <div className={styles.card}>
        <span className={styles.mark} aria-hidden="true">ML</span>
        <h1 className={styles.title}>Sign in to ML Hub</h1>
        <p className={styles.subtitle}>
          {isAdmin
            ? "Sign in as admin to review data across every RMO's book."
            : "Enter your RMO code to see the customers assigned to you. You'll only ever see your own book — this is what keeps the assistant's answers scoped correctly."}
        </p>

        <form onSubmit={handleSubmit}>
          {isAdmin ? (
            <>
              <label htmlFor="password" className={styles.label}>Admin password</label>
              <input
                id="password"
                className={styles.input}
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoFocus
              />
            </>
          ) : (
            <>
              <label htmlFor="rmoCode" className={styles.label}>RMO code</label>
              <input
                id="rmoCode"
                className={styles.input}
                type="text"
                placeholder="e.g. RMO001"
                value={rmoCode}
                onChange={(e) => setRmoCode(e.target.value)}
                autoFocus
              />
            </>
          )}

          {error && <p className={styles.error}>{error}</p>}

          <button type="submit" className={styles.submit} disabled={loading || !canSubmit}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <button
          type="button"
          className={styles.modeToggle}
          onClick={() => switchMode(isAdmin ? "rmo" : "admin")}
        >
          {isAdmin ? "Sign in as an RMO instead" : "Sign in as admin instead"}
        </button>

        <button
          type="button"
          className={styles.settingsToggle}
          onClick={() => setShowSettings((v) => !v)}
        >
          {showSettings ? "Hide" : "Backend URL"}: <code>{backendUrl}</code>
        </button>
        {showSettings && (
          <input
            className={styles.settingsInput}
            type="text"
            value={backendUrl}
            onChange={(e) => setBackendUrl(e.target.value)}
          />
        )}

        <p className={styles.disclaimer}>
          {isAdmin
            ? "Demo login — a single shared password grants full, unscoped access to every RMO's data. Not production-grade auth."
            : "Demo login — identifies which RMO you are for row-level access, no password (the synthetic data has none). Not real authentication."}
        </p>
      </div>
    </div>
  );
}
