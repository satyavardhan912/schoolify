import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch } from "../lib/apiClient";

export default function ChangePasswordForm() {
  const { token, logout } = useAuth();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setMsg("");
    setLoading(true);
    try {
      await apiFetch("/auth/change-password", {
        method: "POST",
        token,
        body: {
          current_password: currentPassword,
          new_password: newPassword,
        },
      });
      setMsg("Password changed successfully. Please log in again.");
      setCurrentPassword("");
      setNewPassword("");
      // optional: force logout
      logout();
    } catch (err) {
      console.error(err);
      const text =
        err?.body?.detail ||
        (Array.isArray(err?.body) && err.body[0]?.msg) ||
        `Failed to change password (status ${err.status || "unknown"})`;
      setMsg(text);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="change-password-form">
      <label>
        <span>Current password</span>
        <input
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          required
        />
      </label>
      <label>
        <span>New password</span>
        <input
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
        />
      </label>
      <button type="submit" disabled={loading}>
        {loading ? "Updating..." : "Update password"}
      </button>
      {msg && <p className="hint">{msg}</p>}
    </form>
  );
}