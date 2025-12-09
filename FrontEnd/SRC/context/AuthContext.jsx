import React, { createContext, useContext, useEffect, useState } from "react";
import { apiFetch } from "../lib/apiClient";

const AuthContext = createContext(null);

function decodeUserFromToken(token) {
  if (!token) return null;
  try {
    const [, payload] = token.split(".");
    const json = JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
    return {
      id: json.sub,
      role: json.role,
      raw: json,
    };
  } catch (e) {
    console.warn("Failed to decode JWT", e);
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [initializing, setInitializing] = useState(true);

  // Load token from localStorage on first mount
  useEffect(() => {
    const saved = window.localStorage.getItem("schoolify_token");
    if (saved) {
      setToken(saved);
      setUser(decodeUserFromToken(saved));
    }
    setInitializing(false);
  }, []);

  async function login(email, password) {
    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: { email, password },
    });
    const newToken = data?.access_token;
    setToken(newToken);
    window.localStorage.setItem("schoolify_token", newToken);
    setUser(decodeUserFromToken(newToken));
    return data;
  }

  function logout() {
    setToken(null);
    setUser(null);
    window.localStorage.removeItem("schoolify_token");
  }

  const value = {
    token,
    user,
    initializing,
    isAuthenticated: !!token,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}