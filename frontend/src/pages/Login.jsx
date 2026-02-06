import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await api.post("/auth/login", form);
      localStorage.setItem("token", data.access_token);
      navigate("/");
    } catch (err) {
      setError("Invalid credentials or inactive user.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid place-items-center bg-ink px-6">
      <div className="w-full max-w-md glow-card rounded-2xl p-8">
        <p className="text-xs uppercase tracking-[0.3em] text-fog/60">Secure Access</p>
        <h1 className="mt-3 font-display text-3xl text-fog">PPE Admin Portal</h1>
        <p className="mt-2 text-sm text-fog/70">
          Sign in to monitor compliance analytics in real time.
        </p>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
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
          {error ? <p className="text-sm text-accent">{error}</p> : null}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-edge px-4 py-3 text-sm font-semibold text-ink hover:bg-edge/90 disabled:opacity-60"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
