import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch } from "../lib/apiClient";

export default function ParentDashboard() {
  const { token, user } = useAuth();
  const [children, setChildren] = useState([]);
  const [childrenError, setChildrenError] = useState("");
  const [childrenLoading, setChildrenLoading] = useState(false);

  const [selectedChildId, setSelectedChildId] = useState("");
  const [exams, setExams] = useState([]);
  const [examsError, setExamsError] = useState("");
  const [examsLoading, setExamsLoading] = useState(false);

  useEffect(() => {
    async function loadChildren() {
      setChildrenError("");
      setChildrenLoading(true);
      try {
        const list = await apiFetch("/students/me/children", {
          method: "GET",
          token,
        });
        setChildren(Array.isArray(list) ? list : []);
      } catch (err) {
        console.error(err);
        const msg =
          err?.body?.detail ||
          (Array.isArray(err?.body) && err.body[0]?.msg) ||
          `Failed to load children (status ${err.status || "unknown"})`;
        setChildrenError(msg);
      } finally {
        setChildrenLoading(false);
      }
    }

    if (token && user?.role === "parent") {
      loadChildren();
    }
  }, [token, user]);

  async function loadExams(studentId) {
    if (!studentId) return;
    setExamsError("");
    setExams([]);
    setExamsLoading(true);
    try {
      const list = await apiFetch(`/exams/students/${studentId}`, {
        method: "GET",
        token,
      });
      setExams(Array.isArray(list) ? list : []);
    } catch (err) {
      console.error(err);
      const msg =
        err?.body?.detail ||
        (Array.isArray(err?.body) && err.body[0]?.msg) ||
        `Failed to load exams (status ${err.status || "unknown"})`;
      setExamsError(msg);
    } finally {
      setExamsLoading(false);
    }
  }

  function handleSelectChild(e) {
    const id = e.target.value;
    setSelectedChildId(id);
    if (id) {
      loadExams(id);
    } else {
      setExams([]);
    }
  }

  return (
    <section className="card">
      <h2>Parent Dashboard</h2>
      <p className="hint">
        You can only see students linked to your parent account and their exam
        results. Backend enforces this via role-based access control.
      </p>

      <div className="teacher-section">
        <h3>Your children</h3>
        {childrenLoading && <p>Loading children...</p>}
        {childrenError && <div className="error">{childrenError}</div>}
        {!childrenLoading && children.length === 0 && !childrenError && (
          <p className="hint">No linked students yet.</p>
        )}

        {children.length > 0 && (
          <>
            <label>
              <span>Select child</span>
              <select value={selectedChildId} onChange={handleSelectChild}>
                <option value="">Choose a student</option>
                {children.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.class_name || "N/A"})
                  </option>
                ))}
              </select>
            </label>
          </>
        )}
      </div>

      <div className="teacher-section">
        <h3>Exam results</h3>
        {examsLoading && <p>Loading exams...</p>}
        {examsError && <div className="error">{examsError}</div>}
        {!examsLoading && exams.length === 0 && selectedChildId && !examsError && (
          <p className="hint">No exam records found for this student.</p>
        )}

        {exams.length > 0 && (
          <div className="created-box">
            <h4>Exam data (raw)</h4>
            <pre>{JSON.stringify(exams, null, 2)}</pre>
          </div>
        )}
      </div>
    </section>
  );
}