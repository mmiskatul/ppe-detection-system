import React, { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Users from "./pages/Users.jsx";
import api from "./services/api";

const isAuthed = () => Boolean(localStorage.getItem("token"));
const isAdmin = () => localStorage.getItem("role") === "admin";

const RequireAuth = ({ children }) => {
  if (!isAuthed()) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const RequireAdmin = ({ children }) => {
  if (!isAuthed()) {
    return <Navigate to="/login" replace />;
  }
  if (!isAdmin()) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

export default function App() {
  const [roleLoaded, setRoleLoaded] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");
    if (!token || role) {
      setRoleLoaded(true);
      return;
    }
    const loadRole = async () => {
      try {
        const { data } = await api.get("/auth/me");
        if (data?.role) {
          localStorage.setItem("role", data.role);
        }
      } finally {
        setRoleLoaded(true);
      }
    };
    loadRole();
  }, []);

  if (!roleLoaded) {
    return <div className="min-h-screen bg-ink" />;
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <RequireAdmin>
            <Dashboard />
          </RequireAdmin>
        }
      />
      <Route
        path="/users"
        element={
          <RequireAdmin>
            <Users />
          </RequireAdmin>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
