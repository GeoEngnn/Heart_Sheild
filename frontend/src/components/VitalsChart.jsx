import React from "react";

export default function VitalsChart({ history }) {
  if (!history || history.length === 0) return null;

  // If only one point → just duplicate it so SVG works
  const safeHistory =
    history.length === 1
      ? [...history, history[0]]
      : history;

  const points = safeHistory
    .map((item, index) => {
      const x = (index / (safeHistory.length - 1)) * 100;

      const prob = item?.probability != null
        ? Number(item.probability)
        : 0;

      const y = 100 - prob * 100;

      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className="chart-container">
      <h3>Probability Trend</h3>
      <svg viewBox="0 0 100 100" className="chart-svg">
        <polyline
          fill="none"
          stroke="#3498db"
          strokeWidth="2"
          points={points}
        />
      </svg>
    </div>
  );
}
