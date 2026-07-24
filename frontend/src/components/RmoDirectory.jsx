import { useEffect, useState } from "react";
import { getRmoDirectory } from "../lib/api";
import styles from "./RmoDirectory.module.css";

export default function RmoDirectory({ backendUrl, token, onSelect, onClose }) {
  const [rmos, setRmos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("");

  useEffect(() => {
    getRmoDirectory(backendUrl, token)
      .then(setRmos)
      .catch((err) => setError(err.message || "Failed to load RMO directory"))
      .finally(() => setLoading(false));
  }, [backendUrl, token]);

  const filtered = rmos.filter((r) => {
    const q = filter.trim().toLowerCase();
    if (!q) return true;
    return (
      r.RmoCode.toLowerCase().includes(q) ||
      r.RmoName.toLowerCase().includes(q) ||
      r.Team.toLowerCase().includes(q) ||
      r.Region.toLowerCase().includes(q)
    );
  });

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.panel} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2 className={styles.title}>RMO directory</h2>
          <button type="button" className={styles.close} onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <input
          className={styles.search}
          type="text"
          placeholder="Filter by code, name, team, or region…"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          autoFocus
        />

        <div className={styles.tableWrap}>
          {loading && <p className={styles.status}>Loading…</p>}
          {error && <p className={styles.error}>{error}</p>}
          {!loading && !error && (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Name</th>
                  <th>Team</th>
                  <th>Region</th>
                  <th>Customers</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((r) => (
                  <tr key={r.RmoId}>
                    <td className={styles.code}>{r.RmoCode}</td>
                    <td>{r.RmoName}</td>
                    <td>{r.Team}</td>
                    <td>{r.Region}</td>
                    <td>{r.CustomerCount}</td>
                    <td>
                      <button
                        type="button"
                        className={styles.viewButton}
                        onClick={() => onSelect(r)}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {!loading && !error && filtered.length === 0 && (
            <p className={styles.status}>No RMOs match "{filter}".</p>
          )}
        </div>
      </div>
    </div>
  );
}
