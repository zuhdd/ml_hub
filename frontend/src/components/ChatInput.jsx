import { useEffect, useRef, useState } from "react";
import styles from "./ChatInput.module.css";

const MAX_QUESTION_LENGTH = 500;

export default function ChatInput({ value, onChange, onSubmit, loading, aiUrl, onAiUrlChange }) {
  const [showSettings, setShowSettings] = useState(false);
  const textareaRef = useRef(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [value]);

  return (
    <div className={styles.dock}>
      <form className={styles.bar} onSubmit={onSubmit}>
        <textarea
          ref={textareaRef}
          className={styles.input}
          placeholder="Ask about churn, CLV, RMOs, or a specific customer…"
          value={value}
          maxLength={MAX_QUESTION_LENGTH}
          onChange={(e) => onChange(e.target.value)}
          rows={1}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSubmit(e);
            }
          }}
        />
        <button type="submit" className={styles.submit} disabled={loading || !value.trim()}>
          {loading ? <span className={styles.spinner} aria-hidden="true" /> : "Ask"}
        </button>
      </form>

      <div className={styles.caption}>
        <span>Read-only · Grounded in your warehouse · Fully audited</span>
        <button type="button" className={styles.settingsToggle} onClick={() => setShowSettings((v) => !v)}>
          {showSettings ? "Hide" : "AI service"}
        </button>
      </div>

      {showSettings && (
        <div className={styles.settingsRow}>
          <label htmlFor="aiUrl" className="visually-hidden">AI service URL</label>
          <input
            id="aiUrl"
            className={styles.settingsInput}
            type="text"
            value={aiUrl}
            onChange={(e) => onAiUrlChange(e.target.value)}
          />
        </div>
      )}
    </div>
  );
}
