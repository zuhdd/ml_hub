import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import styles from "./Message.module.css";

function ThinkingDots() {
  return (
    <span className={styles.thinking}>
      <span className={styles.dot} />
      <span className={styles.dot} />
      <span className={styles.dot} />
    </span>
  );
}

export default function Message({ role, content, status, toolCalls, error }) {
  if (role === "user") {
    return (
      <div className={styles.userRow}>
        <div className={styles.userBubble}>{content}</div>
      </div>
    );
  }

  return (
    <div className={styles.assistantRow}>
      <span className={styles.avatar} aria-hidden="true">ML</span>
      <div className={styles.assistantContent}>
        {status === "loading" && <ThinkingDots />}

        {status === "error" && <p className={styles.error}>{error}</p>}

        {(status === "streaming" || status === "done") && (
          <div className={styles.prose}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
            {status === "streaming" && <span className={styles.cursor} aria-hidden="true" />}
          </div>
        )}

        {status === "done" && toolCalls?.length > 0 && (
          <details className={styles.details}>
            <summary>
              How this was answered ({toolCalls.length} tool call{toolCalls.length > 1 ? "s" : ""})
            </summary>
            <div className={styles.toolList}>
              {toolCalls.map((call, i) => (
                <div key={i} className={styles.toolCall}>
                  <span className={styles.toolName}>{call.tool}</span>
                  <pre className={styles.toolInput}>{JSON.stringify(call.input, null, 2)}</pre>
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
