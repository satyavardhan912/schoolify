import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch } from "../lib/apiClient";

export default function PrincipalDashboard() {
  const { token } = useAuth();

  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("changeme");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastCreated, setLastCreated] = useState(null);

  async function handleCreateTeacher(e) {
    e.preventDefault();
    setError("");
    setLastCreated(null);
    setLoading(true);
    try {
      const res = await apiFetch("/auth/principal/add-teacher", {
        method: "POST",
        token,
        body: {
          email,
          password,
          full_name: fullName || null,
          role: "teacher",
        },
      });
      setLastCreated(res);
      setEmail("");
      setFullName("");
      setPassword("changeme");
    } catch (err) {
      console.error(err);
      const msg =
        err?.body?.detail ||
        (Array.isArray(err?.body) && err.body[0]?.msg) ||
        `Failed to create teacher (status ${err.status || "unknown"})`;
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <h2>Principal: Manage Teachers</h2>
      <p className="hint">
        This form calls <code>POST /auth/principal/add-teacher</code> with your
        JWT. Backend enforces that only principals can access it.
      </p>

      <form onSubmit={handleCreateTeacher} className="teacher-form">
        <label>
          <span>Email</span>
          <input
            type="email"
            required
            value={email}
            placeholder="teacher2@schoolify"
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>

        <label>
          <span>Full name</span>
          <input
            type="text"
            value={fullName}
            placeholder="Teacher Two"
            onChange={(e) => setFullName(e.target.value)}
          />
        </label>

        <label>
          <span>Initial password</span>
          <input
            type="text"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        {error && <div className="error">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? "Creating..." : "Create Teacher"}
        </button>
      </form>

      {lastCreated && (
        <div className="created-box">
          <h3>Teacher created</h3>
          <pre>{JSON.stringify(lastCreated, null, 2)}</pre>
        </div>
      )}
    </section>
  );
}