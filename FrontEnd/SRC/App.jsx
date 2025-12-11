import { useAuth } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";
import PrincipalDashboard from "./pages/PrincipalDashboard";
import TeacherDashboard from "./pages/TeacherDashboard";
import ParentDashboard from "./pages/ParentDashboard";
import ChangePasswordForm from "./components/ChangePasswordForm";
import {useState} from "react";

function App() {
  const { isAuthenticated, user, logout, initializing } = useAuth();
    const [showChangePassword, setShowChangePassword] = useState(false);

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
        <div style={{ display: "flex", gap: "8px" }}>
          <button
            className="logout-btn"
            type="button"
            onClick={() => setShowChangePassword((v) => !v)}
          >
            {showChangePassword ? "Close password panel" : "Change password"}
          </button>
          <button className="logout-btn" type="button" onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      {showChangePassword && (
        <section className="card">
          <h2>Change password</h2>
          <ChangePasswordForm />
        </section>
      )}

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

        {role === "parent" && <ParentDashboard />}

        {role !== "principal" && role !== "teacher" && role !== "parent" && (
          <section className="card">
            <h2>Limited access</h2>
            <p>
              Your role (<code>{role}</code>) has limited UI features. You can
              still use APIs directly via curl/Postman.
            </p>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;