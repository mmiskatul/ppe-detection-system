import React from "react";

export default function ChartCard({ title, children }) {
  return (
    <div className="glow-card rounded-2xl p-6">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-lg text-fog">{title}</h3>
      </div>
      <div className="mt-4">{children}</div>
    </div>
  );
}
