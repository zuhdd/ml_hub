import { useEffect, useRef } from "react";
import Message from "./Message";
import ExampleQuestions from "./ExampleQuestions";
import styles from "./ChatPanel.module.css";

export default function ChatPanel({ messages, onPickExample }) {
  const listRef = useRef(null);

  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className={styles.empty}>
        <span className={styles.kicker}>AI Customer Intelligence</span>
        <h1 className={styles.headline}>
          Ask ML Hub anything about your <span className={styles.accent}>customers</span>.
        </h1>
        <p className={styles.subtext}>
          Churn risk, lifetime value, RMO coverage, product recommendations, and lending
          eligibility — grounded in the warehouse, every source traceable.
        </p>
        <ExampleQuestions onPick={onPickExample} />
      </div>
    );
  }

  return (
    <div className={styles.list} ref={listRef}>
      <div className={styles.inner}>
        {messages.map((m) => (
          <Message key={m.id} {...m} />
        ))}
      </div>
    </div>
  );
}
