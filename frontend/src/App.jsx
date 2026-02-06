import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Users from "./pages/Users.jsx";

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
    return <Navigate to="/" replace />;
  }
  return children;
};

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <Dashboard />
          </RequireAuth>
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
