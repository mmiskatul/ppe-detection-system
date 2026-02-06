import React from "react";
import { NavLink, useNavigate } from "react-router-dom";

const navLinkClass = ({ isActive }) =>
  `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition ${
    isActive ? "bg-edge text-ink" : "text-fog/80 hover:text-fog hover:bg-white/5"
  }`;

export default function Sidebar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <aside className="w-full lg:w-64 bg-steel/60 border-r border-white/10 px-4 py-6">
      <div className="mb-8">
        <p className="text-xs uppercase tracking-[0.3em] text-fog/50">Admin</p>
        <h1 className="font-display text-2xl text-fog">PPE Command</h1>
      </div>
      <nav className="space-y-2">
        <NavLink to="/" className={navLinkClass}>
          Dashboard
        </NavLink>
        <NavLink to="/users" className={navLinkClass}>
          Users
        </NavLink>
      </nav>
      <button
        onClick={handleLogout}
        className="mt-8 w-full rounded-xl border border-white/20 px-4 py-2 text-sm text-fog/80 hover:text-fog hover:border-white/40"
      >
        Sign out
      </button>
    </aside>
  );
}
