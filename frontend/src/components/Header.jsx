import styles from "./Header.module.css";

export default function Header({ onNewChat, session, onLogout, viewScope, onBrowseRmos, onClearScope }) {
  const isAdmin = session?.role === "admin";

  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <div className={styles.identity}>
          {session && !isAdmin && (
            <span className={styles.rmoBadge}>
              {session.rmo.rmo_name} <span className={styles.rmoCode}>({session.rmo.rmo_code})</span>
            </span>
          )}
          {isAdmin && (
            <>
              <span className={styles.adminBadge}>Admin</span>
              <span className={styles.scopeBadge}>
                {viewScope ? `Viewing: ${viewScope.rmo_name} (${viewScope.rmo_code})` : "Viewing: all RMOs"}
              </span>
              <button type="button" className={styles.linkButton} onClick={onBrowseRmos}>
                Browse RMOs
              </button>
              {viewScope && (
                <button type="button" className={styles.linkButton} onClick={onClearScope}>
                  Clear scope
                </button>
              )}
            </>
          )}
        </div>

        <div className={styles.actions}>
          <button type="button" className={styles.newChat} onClick={onNewChat}>
            New chat
          </button>
          {session && (
            <button type="button" className={styles.logout} onClick={onLogout}>
              Log out
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
