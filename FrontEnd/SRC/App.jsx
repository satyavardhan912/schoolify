import { useAuth } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";

function App() {
  const { isAuthenticated, user, logout, initializing } = useAuth();

  if (initializing) {
    return (
      <div className="app-container">
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div>
          <h1>Schoolify UI</h1>
          <p className="subtitle">
            You are logged in as <strong>{user?.role || "unknown-role"}</strong>
          </p>
        </div>
        <button className="logout-btn" onClick={logout}>
          Logout
        </button>
      </header>

      <main>
        <section className="card">
          <h2>Current User</h2>
          <p>
            <strong>ID:</strong> {user?.id || "N/A"}
          </p>
          <p>
            <strong>Role:</strong> {user?.role || "N/A"}
          </p>
          <p className="hint">
            This data is decoded from the JWT issued by the backend.
          </p>
        </section>

        <section className="card">
          <h2>Next steps</h2>
          <ul>
            <li>Principal dashboard to create teachers (principal-only).</li>
            <li>
              Teacher dashboard to add students, upload exams and compare
              performance.
            </li>
            <li>Security info page explaining hashing, JWT and encryption.</li>
          </ul>
        </section>
      </main>
    </div>
  );
}

export default App;