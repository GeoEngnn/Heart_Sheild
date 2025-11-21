import React, { useEffect, useState } from "react";
import StatusBadge from "../components/StatusBadge";
import { getUserStatus } from "../services/api";

export default function Status() {
  const user = JSON.parse(localStorage.getItem("heartshield_user"));
  const userId = user?.id;

  const [status, setStatus] = useState(null);
  const [latest, setLatest] = useState(null);

  useEffect(() => {
    if (!userId) return;

    getUserStatus(userId).then((res) => {
      if (res.success) {
        setStatus(res.status);
        setLatest(res.latest);
      }
    });
  }, [userId]);

  return (
    <div className="status-page">
      <h2 className="title">Overall Health Status</h2>

      {status && <StatusBadge status={status} />}

      {latest ? (
        <>
          <div className="status-box">
            <h3>Your Latest Prediction</h3>
            <p>
              <strong>Risk Level:</strong> {latest.risk_level}
            </p>
            <p>
              <strong>Probability:</strong>{" "}
              {(latest.probability * 100).toFixed(1)}%
            </p>
            <p>
              <strong>Last Updated:</strong> {latest.created_at}
            </p>
          </div>

          <div className="vitals-grid">
            <div className="vital-card">
              <h4>Blood Pressure</h4>
              <p>
                {latest.systolic_bp}/{latest.diastolic_bp}
              </p>
            </div>
            <div className="vital-card">
              <h4>Cholesterol</h4>
              <p>{latest.cholesterol}</p>
            </div>
            <div className="vital-card">
              <h4>Glucose</h4>
              <p>{latest.glucose}</p>
            </div>
            <div className="vital-card">
              <h4>BMI</h4>
              <p>{latest.bmi}</p>
            </div>
          </div>
        </>
      ) : (
        <p>No prediction found.</p>
      )}

      <div className="actions">
        <a href="/dashboard" className="btn">
          ← Back to Dashboard
        </a>
      </div>
    </div>
  );
}
