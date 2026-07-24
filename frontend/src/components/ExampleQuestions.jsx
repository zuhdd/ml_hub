import styles from "./ExampleQuestions.module.css";

const EXAMPLES = [
  "Which customers are most likely to churn?",
  "Which retail customers should get a product offer?",
  "Which SME customers are eligible for lending?",
  "Tell me about customer R000000001",
];

export default function ExampleQuestions({ onPick }) {
  return (
    <div className={styles.wrap}>
      <span className={styles.label}>Try asking</span>
      <div className={styles.chips}>
        {EXAMPLES.map((question) => (
          <button
            key={question}
            type="button"
            className={styles.chip}
            onClick={() => onPick(question)}
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
