import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch } from "../lib/apiClient";

export default function TeacherDashboard() {
  const { token, user } = useAuth();
  const teacherId = user?.id;

  // students created in this session
  const [students, setStudents] = useState([]);

  // create student
  const [sName, setSName] = useState("");
  const [sRoll, setSRoll] = useState("");
  const [sClass, setSClass] = useState("");
  const [sParentEmail, setSParentEmail] = useState("");
  const [studentError, setStudentError] = useState("");
  const [studentLoading, setStudentLoading] = useState(false);

  // exam upload
  const [selectedStudentId, setSelectedStudentId] = useState("");
  const [term, setTerm] = useState("");
  const [marks, setMarks] = useState({
    maths: "",
    physics: "",
    chemistry: "",
    biology: "",
    social: "",
    english: "",
  });
  const [examError, setExamError] = useState("");
  const [examLoading, setExamLoading] = useState(false);
  const [lastExamResult, setLastExamResult] = useState(null);

  // comparison
  const [studentA, setStudentA] = useState("");
  const [studentB, setStudentB] = useState("");
  const [compareTerm, setCompareTerm] = useState("");
  const [compareError, setCompareError] = useState("");
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareResult, setCompareResult] = useState(null);

  if (!teacherId) {
    return (
      <section className="card">
        <h2>Teacher Dashboard</h2>
        <p>Could not determine teacher id from token.</p>
      </section>
    );
  }

  async function handleCreateStudent(e) {
    e.preventDefault();
    setStudentError("");
    setStudentLoading(true);
    try {
      const body = {
        name: sName,
        roll_no: sRoll || null,
        class_name: sClass || null,
        parent_email: sParentEmail || null,
      };
      const res = await apiFetch(`/auth/teachers/${teacherId}/students`, {
        method: "POST",
        token,
        body,
      });
      setStudents((prev) => [...prev, res]);
      setSName("");
      setSRoll("");
      setSClass("");
      setSParentEmail("");
    } catch (err) {
      console.error(err);
      const msg =
        err?.body?.detail ||
        (Array.isArray(err?.body) && err.body[0]?.msg) ||
        `Failed to create student (status ${err.status || "unknown"})`;
      setStudentError(msg);
    } finally {
      setStudentLoading(false);
    }
  }

  function handleMarksChange(subject, value) {
    setMarks((prev) => ({
      ...prev,
      [subject]: value,
    }));
  }

  async function handleUploadExam(e) {
    e.preventDefault();
    setExamError("");
    setLastExamResult(null);
    if (!selectedStudentId) {
      setExamError("Please select a student");
      return;
    }
    setExamLoading(true);
    try {
      // Body shape should match your ExamCreate schema
      const body = {
        term: term || null,
        maths: Number(marks.maths || 0),
        physics: Number(marks.physics || 0),
        chemistry: Number(marks.chemistry || 0),
        biology: Number(marks.biology || 0),
        social: Number(marks.social || 0),
        english: Number(marks.english || 0),
      };
      const res = await apiFetch(
        `/exams/teachers/${teacherId}/students/${selectedStudentId}`,
        {
          method: "POST",
          token,
          body,
        }
      );
      setLastExamResult(res);
    } catch (err) {
      console.error(err);
      const msg =
        err?.body?.detail ||
        (Array.isArray(err?.body) && err.body[0]?.msg) ||
        `Failed to upload exam (status ${err.status || "unknown"})`;
      setExamError(msg);
    } finally {
      setExamLoading(false);
    }
  }

  async function handleCompare(e) {
    e.preventDefault();
    setCompareError("");
    setCompareResult(null);
    if (!studentA || !studentB) {
      setCompareError("Please select two students to compare");
      return;
    }
    setCompareLoading(true);
    try {
      const params = new URLSearchParams({
        student_a: studentA,
        student_b: studentB,
      });
      if (compareTerm) {
        params.append("term", compareTerm);
      }
      const res = await apiFetch(`/exams/compare?${params.toString()}`, {
        method: "GET",
        token,
      });
      setCompareResult(res);
    } catch (err) {
      console.error(err);
      const msg =
        err?.body?.detail ||
        (Array.isArray(err?.body) && err.body[0]?.msg) ||
        `Failed to compare students (status ${err.status || "unknown"})`;
      setCompareError(msg);
    } finally {
      setCompareLoading(false);
    }
  }

  return (
    <section className="card">
      <h2>Teacher Dashboard</h2>
      <p className="hint">
        Uses your teacher JWT to call{" "}
        <code>/auth/teachers/&lt;id&gt;/students</code>,{" "}
        <code>/exams/teachers/&lt;id&gt;/students/&lt;student&gt;</code>, and{" "}
        <code>/exams/compare</code>. Backend RBAC ensures only teachers can
        perform these actions.
      </p>

      {/* Create student */}
      <div className="teacher-section">
        <h3>Create student</h3>
        <form onSubmit={handleCreateStudent} className="teacher-form">
          <label>
            <span>Name</span>
            <input
              type="text"
              required
              value={sName}
              onChange={(e) => setSName(e.target.value)}
              placeholder="Alice"
            />
          </label>
          <label>
            <span>Roll no</span>
            <input
              type="text"
              value={sRoll}
              onChange={(e) => setSRoll(e.target.value)}
              placeholder="A1"
            />
          </label>
          <label>
            <span>Class</span>
            <input
              type="text"
              value={sClass}
              onChange={(e) => setSClass(e.target.value)}
              placeholder="5A"
            />
          </label>
          <label>
            <span>Parent email</span>
            <input
              type="email"
              value={sParentEmail}
              onChange={(e) => setSParentEmail(e.target.value)}
              placeholder="parent@example.com"
            />
          </label>

          {studentError && <div className="error">{studentError}</div>}

          <button type="submit" disabled={studentLoading}>
            {studentLoading ? "Creating..." : "Create student"}
          </button>
        </form>

        {students.length > 0 && (
          <div className="teacher-list">
            <h4>Students (session)</h4>
            <table className="teacher-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Roll</th>
                  <th>Class</th>
                  <th>Parent</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s) => (
                  <tr key={s.id}>
                    <td>{s.name}</td>
                    <td>{s.roll_no || "-"}</td>
                    <td>{s.class_name || "-"}</td>
                    <td>{s.parent_id || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Upload exam */}
      <div className="teacher-section">
        <h3>Upload exam results</h3>
        <form onSubmit={handleUploadExam} className="teacher-form">
          <label>
            <span>Student</span>
            <select
              value={selectedStudentId}
              onChange={(e) => setSelectedStudentId(e.target.value)}
              required
            >
              <option value="">Select student</option>
              {students.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.class_name || "N/A"})
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Term</span>
            <input
              type="text"
              value={term}
              onChange={(e) => setTerm(e.target.value)}
              placeholder="midterm2025"
            />
          </label>

          <div className="marks-grid">
            {Object.keys(marks).map((subj) => (
              <label key={subj}>
                <span>{subj}</span>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={marks[subj]}
                  onChange={(e) => handleMarksChange(subj, e.target.value)}
                />
              </label>
            ))}
          </div>

          {examError && <div className="error">{examError}</div>}

          <button type="submit" disabled={examLoading || !students.length}>
            {examLoading ? "Uploading..." : "Upload exam"}
          </button>
        </form>

        {lastExamResult && (
          <div className="created-box">
            <h4>Exam saved (raw response)</h4>
            <pre>{JSON.stringify(lastExamResult, null, 2)}</pre>
          </div>
        )}
      </div>

      {/* Compare students */}
      <div className="teacher-section">
        <h3>Compare students</h3>
        <form onSubmit={handleCompare} className="teacher-form">
          <label>
            <span>Student A</span>
            <select
              value={studentA}
              onChange={(e) => setStudentA(e.target.value)}
              required
            >
              <option value="">Select student</option>
              {students.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Student B</span>
            <select
              value={studentB}
              onChange={(e) => setStudentB(e.target.value)}
              required
            >
              <option value="">Select student</option>
              {students.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Term (optional)</span>
            <input
              type="text"
              value={compareTerm}
              onChange={(e) => setCompareTerm(e.target.value)}
              placeholder="midterm2025"
            />
          </label>

          {compareError && <div className="error">{compareError}</div>}

          <button type="submit" disabled={compareLoading || students.length < 2}>
            {compareLoading ? "Comparing..." : "Compare"}
          </button>
        </form>

        {compareResult && (
          <div className="created-box">
            <h4>Comparison result (raw response)</h4>
            <pre>{JSON.stringify(compareResult, null, 2)}</pre>
          </div>
        )}
      </div>
    </section>
  );
}