import React, { useEffect, useRef } from "react";

export default function KpiCard({ label, value, tone = "edge" }) {
  const ref = useRef(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.classList.remove("animate-kpi");
      void ref.current.offsetWidth;
      ref.current.classList.add("animate-kpi");
    }
  }, [value]);

  const toneMap = {
    edge: "text-edge",
    accent: "text-accent",
    fog: "text-fog"
  };

  return (
    <div ref={ref} className="glow-card rounded-2xl p-5 grid-bg">
      <p className="text-xs uppercase tracking-[0.2em] text-fog/60">{label}</p>
      <p className={`mt-3 font-display text-3xl ${toneMap[tone]}`}>{value}</p>
    </div>
  );
}
