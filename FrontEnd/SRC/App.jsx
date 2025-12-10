import { useAuth } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";
import PrincipalDashboard from "./pages/PrincipalDashboard";
import TeacherDashboard from "./pages/TeacherDashboard";

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

  const role = user?.role || "unknown";

  const isPrincipal = role === "principal";
  const isTeacher = role === "teacher";

  return (
    <div className="app-container">
      <header className="app-header">
        <div>
          <h1>Schoolify UI</h1>
          <p className="subtitle">
            Logged in as <strong>{role}</strong>
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
            <strong>Role:</strong> {role}
          </p>
          <p className="hint">
            This is decoded from the JWT issued by the backend. Role is used in
            the UI and also enforced by backend RBAC.
          </p>
        </section>

        {isPrincipal && <PrincipalDashboard />}

        {role === "teacher" && <TeacherDashboard />}

        {!isPrincipal && !isTeacher && (
          <section className="card">
            <h2>Limited view</h2>
            <p>
              You are logged in but do not have principal or teacher
              permissions. Principal-only actions are hidden and will return
              HTTP 403 from the backend if attempted.
            </p>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;