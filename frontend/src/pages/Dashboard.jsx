import React, { useEffect, useMemo, useState } from "react";
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip as ChartTooltip,
  Legend
} from "chart.js";
import Sidebar from "../components/Sidebar.jsx";
import KpiCard from "../components/KpiCard.jsx";
import ChartCard from "../components/ChartCard.jsx";
import api from "../services/api";
import { createAnalyticsSocket } from "../services/socket";

ChartJS.register(ArcElement, ChartTooltip, Legend);

const dayLabels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export default function Dashboard() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      const { data } = await api.get("/analytics/summary");
      setSummary(data);
    };
    fetchSummary();

    const socket = createAnalyticsSocket();
    socket.on("analytics_updated", (payload) => setSummary(payload));
    socket.on("prevention_saved", (payload) => setSummary(payload));
    socket.on("incident_saved", (payload) => setSummary(payload));

    return () => socket.disconnect();
  }, []);

  const weeklyData = useMemo(() => {
    if (!summary?.weekly_summaries) return [];
    return summary.weekly_summaries.map((item) => ({
      name: `W${item._id.week}`,
      compliant: item.compliant,
      violations: item.violations
    }));
  }, [summary]);

  const topViolations = useMemo(() => {
    if (!summary?.top_violation_types) return [];
    return summary.top_violation_types.map((item) => ({
      name: item._id,
      value: item.count
    }));
  }, [summary]);

  const highRiskDays = useMemo(() => {
    if (!summary?.high_risk_days) return [];
    return summary.high_risk_days.map((item) => ({
      name: dayLabels[item._id - 1],
      count: item.count
    }));
  }, [summary]);

  const doughnutData = useMemo(() => {
    const labels = topViolations.map((item) => item.name);
    const data = topViolations.map((item) => item.value);
    return {
      labels,
      datasets: [
        {
          data,
          backgroundColor: ["#14B8A6", "#F97316", "#38BDF8", "#FB7185", "#A3E635"]
        }
      ]
    };
  }, [topViolations]);

  return (
    <div className="min-h-screen bg-ink text-fog flex flex-col lg:flex-row">
      <Sidebar />
      <main className="flex-1 px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <KpiCard
            label="PPE Compliance"
            value={summary ? `${summary.ppe_compliance_percent}%` : "--"}
            tone="edge"
          />
          <KpiCard
            label="Total Incidents"
            value={summary ? summary.total_incidents : "--"}
            tone="accent"
          />
          <KpiCard
            label="Estimated Savings"
            value={summary ? `$${summary.estimated_savings.toFixed(2)}` : "--"}
            tone="fog"
          />
        </div>

        <div className="mt-10 grid grid-cols-1 xl:grid-cols-2 gap-6">
          <ChartCard title="Weekly Compliance vs Violations">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                  <XAxis dataKey="name" stroke="#94A3B8" />
                  <YAxis stroke="#94A3B8" />
                  <Tooltip contentStyle={{ background: "#0B0F1A", border: "1px solid #334155" }} />
                  <Line type="monotone" dataKey="compliant" stroke="#14B8A6" strokeWidth={2} />
                  <Line type="monotone" dataKey="violations" stroke="#F97316" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>

          <ChartCard title="Top Violation Types">
            <div className="h-64 flex items-center justify-center">
              {topViolations.length ? (
                <Doughnut data={doughnutData} />
              ) : (
                <p className="text-sm text-fog/60">No violations yet.</p>
              )}
            </div>
          </ChartCard>
        </div>

        <div className="mt-10 grid grid-cols-1 xl:grid-cols-2 gap-6">
          <ChartCard title="High-Risk Days">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={highRiskDays}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                  <XAxis dataKey="name" stroke="#94A3B8" />
                  <YAxis stroke="#94A3B8" />
                  <Tooltip contentStyle={{ background: "#0B0F1A", border: "1px solid #334155" }} />
                  <Bar dataKey="count" fill="#38BDF8" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>

          <ChartCard title="Realtime Feed">
            <div className="space-y-3 text-sm text-fog/70">
              <div className="flex items-center justify-between">
                <span>Socket status</span>
                <span className="text-edge">Connected</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Last refresh</span>
                <span>{summary ? new Date().toLocaleTimeString() : "--"}</span>
              </div>
              <p className="text-xs text-fog/60">
                Analytics update automatically when prevention or incident events are saved.
              </p>
            </div>
          </ChartCard>
        </div>
      </main>
    </div>
  );
}
