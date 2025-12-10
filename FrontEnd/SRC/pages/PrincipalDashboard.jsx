import {useEffect, useState} from "react";
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

  const [teachers, setTeachers] = useState([]);
  const [teachersLoading, setTeachersLoading] = useState(false);
  const [teachersError, setTeachersError] = useState("");


  async function loadTeachers() {
    setTeachersError("");
    setTeachersLoading(true);
    try {
      const list = await apiFetch("/users/teachers", {
        method: "GET",
        token,
      });
      setTeachers(Array.isArray(list) ? list : []);
    } catch (err) {
      console.error(err);
      const msg =
        err?.body?.detail ||
        (Array.isArray(err?.body) && err.body[0]?.msg) ||
        `Failed to load teachers (status ${err.status || "unknown"})`;
      setTeachersError(msg);
    } finally {
      setTeachersLoading(false);
    }
  }

  useEffect(() => {
    if (token) {
      loadTeachers();
    }
  }, [token]);


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

  async function handleDeleteTeacher(id) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this teacher?"
    );
    if (!confirmed) return;

    try {
      await apiFetch(`/auth/principal/teachers/${id}`, {
        method: "DELETE",
        token,
      });
      // optimistic update
      setTeachers((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      console.error(err);
      const msg =
        err?.body?.detail ||
        (Array.isArray(err?.body) && err.body[0]?.msg) ||
        `Failed to delete teacher (status ${err.status || "unknown"})`;
      alert(msg);
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
       <div className="teacher-list">
        <h3>Existing teachers</h3>

        {teachersLoading && <p>Loading teachers...</p>}
        {teachersError && <div className="error">{teachersError}</div>}

        {!teachersLoading && teachers.length === 0 && !teachersError && (
          <p className="hint">No teachers found yet.</p>
        )}

        {teachers.length > 0 && (
          <table className="teacher-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Full name</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {teachers.map((t) => (
                <tr key={t.id}>
                  <td>{t.email}</td>
                  <td>{t.full_name || "-"}</td>
                  <td>
                    <button
                      type="button"
                      className="danger-btn"
                      onClick={() => handleDeleteTeacher(t.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}