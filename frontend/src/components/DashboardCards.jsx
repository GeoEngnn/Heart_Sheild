import React from "react";
import "./Dashboard.css";

export default function DashboardCards({ status, latest }) {
  // Safe color mapping including no_data
  const riskColor =
    status === "improving"
      ? "#27ae60"
      : status === "worsening"
      ? "#e74c3c"
      : status === "stable"
      ? "#f1c40f"
      : "#7f8c8d"; // no_data or unknown

  // Safe probability formatting
  const probability = latest?.probability != null
    ? (latest.probability * 100).toFixed(1)
    : "N/A";

  // Safe BMI formatting
  const bmiValue =
    latest?.bmi != null && !isNaN(Number(latest.bmi))
      ? Number(latest.bmi).toFixed(1)
      : "N/A";

  const bmiStatus =
    latest?.bmi != null && latest.bmi > 25
      ? "Overweight"
      : latest?.bmi != null
      ? "Healthy"
      : "N/A";

  return (
    <div className="dashboard-cards">
      {/* STATUS CARD */}
      <div
        className="card status-card"
        style={{ borderLeft: `6px solid ${riskColor}` }}
      >
        <h3>Status</h3>
        <p className="status-value">{status || "No Data"}</p>
        <small>Based on your latest prediction</small>
      </div>

      {/* LATEST RISK */}
      <div className="card">
        <h3>Latest Risk</h3>
        <p className="big-value">{latest?.risk_level || "N/A"}</p>
        <small>Probability: {probability}%</small>
      </div>

      {/* BMI */}
      <div className="card">
        <h3>BMI</h3>
        <p className="big-value">{bmiValue}</p>
        <small>{bmiStatus}</small>
      </div>
    </div>
  );
}

