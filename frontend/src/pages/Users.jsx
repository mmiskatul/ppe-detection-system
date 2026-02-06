import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar.jsx";
import api from "../services/api";

export default function Users() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({ username: "", password: "", role: "admin" });
  const [error, setError] = useState("");

  const loadUsers = async () => {
    const { data } = await api.get("/users");
    setUsers(data);
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleChange = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await api.post("/users", form);
      setForm({ username: "", password: "", role: "admin" });
      loadUsers();
    } catch (err) {
      setError("Unable to create user.");
    }
  };

  return (
    <div className="min-h-screen bg-ink text-fog flex flex-col lg:flex-row">
      <Sidebar />
      <main className="flex-1 px-6 py-8">
        <h2 className="font-display text-2xl text-fog">User Management</h2>
        <p className="text-sm text-fog/60">Admin-only access for system operators.</p>

        <div className="mt-6 grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="glow-card rounded-2xl p-6">
            <h3 className="font-display text-lg">Create User</h3>
            <form onSubmit={handleSubmit} className="mt-4 space-y-3">
              <input
                className="w-full rounded-xl bg-black/40 border border-white/10 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-edge/60"
                name="username"
                placeholder="Username"
                value={form.username}
                onChange={handleChange}
                required
              />
              <input
                className="w-full rounded-xl bg-black/40 border border-white/10 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-edge/60"
                name="password"
                type="password"
                placeholder="Password"
                value={form.password}
                onChange={handleChange}
                required
              />
              <select
                className="w-full rounded-xl bg-black/40 border border-white/10 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-edge/60"
                name="role"
                value={form.role}
                onChange={handleChange}
              >
                <option value="admin">Admin</option>
                <option value="viewer">Viewer</option>
              </select>
              {error ? <p className="text-sm text-accent">{error}</p> : null}
              <button className="w-full rounded-xl bg-edge px-4 py-3 text-sm font-semibold text-ink">
                Add user
              </button>
            </form>
          </div>

          <div className="glow-card rounded-2xl p-6 xl:col-span-2">
            <h3 className="font-display text-lg">Active Users</h3>
            <div className="mt-4 space-y-3 text-sm">
              {users.map((user) => (
                <div
                  key={user._id}
                  className="flex items-center justify-between rounded-xl bg-black/40 px-4 py-3"
                >
                  <div>
                    <p className="text-fog">{user.username}</p>
                    <p className="text-xs text-fog/60">{user.role}</p>
                  </div>
                  <span className="text-xs text-edge">
                    {user.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
              ))}
              {!users.length ? (
                <p className="text-fog/60">No users found.</p>
              ) : null}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
