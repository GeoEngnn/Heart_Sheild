import React from "react";

export default function DashboardCards({ status, latest }) {
  // Safe color mapping including no_data
  const riskColor =
    status === "improving"
      ? "#27ae60"
      : status === "worsening"
      ? "#e74c3c"
      : status === "stable"
      ? "#f1c40f"
      : "#529ea3ff"; // no_data or unknown

  // Safe probability formatting
  const probability =
    latest?.probability != null
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
        className="dashboard-card status-card"
        style={{ borderLeft: `6px solid ${riskColor}` }}
      >
        <div className="card-header">
          <h3 className="card-title">Status</h3>
          <span className={`status-badge ${!status ? "status-No data" : ""}`}>
            {status || "No data"}
          </span>
        </div>
        <div className="card-content">
          <div className="metric-value">{status || "N/A"}</div>
          <div className="prediction-title">Based on your latest prediction</div>
        </div>
      </div>

      {/* LATEST RISK */}
      <div className="dashboard-card risk-card">
        <div className="card-header">
          <h3 className="card-title">Latest Risk</h3>
        </div>
        <div className="card-content">
          <div className="metric-label">Cardiovascular Risk</div>
          <div className="metric-value">{latest?.risk_level || "N/A"}</div>
          <div className="prediction-title">Probability: {probability}%</div>
        </div>
      </div>

      {/* BMI */}
      <div className="dashboard-card bmi-card">
        <div className="card-header">
          <h3 className="card-title">BMI</h3>
        </div>
        <div className="card-content">
          <div className="metric-label">Body Mass Index</div>
          <div className="metric-value">{bmiValue}</div>
          <div className="prediction-title">{bmiStatus}</div>
        </div>
      </div>
    </div>
  );
}