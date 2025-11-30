import React, { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import Header from "../components/Header"; // ✅ Fixed - removed curly braces
import { getUserHistory } from "../services/api";

export default function History() {
  const { userId: routeUserId } = useParams();
  const storedUser = JSON.parse(localStorage.getItem("heartshield_user"));
  const userId = routeUserId || storedUser?.id;

  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchHistory = useCallback(async () => {
    if (!userId) {
      setError("No logged-in user.");
      setLoading(false);
      return;
    }

    try {
      const res = await getUserHistory(userId);
      if (res.success) {
        setHistory(res.historyData);
        setError("");
      } else {
        setError(res.error || "Unable to load history.");
      }
    } catch {
      setError("Server error. Check backend.");
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  // Auto-refresh every 5 seconds to catch new predictions
  useEffect(() => {
    if (!userId) return;

    const interval = setInterval(() => {
      fetchHistory();
    }, 5000);

    return () => clearInterval(interval);
  }, [userId, fetchHistory]);

  if (loading) return <div className="loading-container">Loading history…</div>;
  if (error) return <div className="error-container">{error}</div>;

  return (
    <div className="history-page">
      <Header />
      <div className="app-container">
        <h2 className="page-title">Prediction History</h2>

        {history.length === 0 ? (
          <div className="empty-state">
            No previous predictions found.
          </div>
        ) : (
          <div className="history-list">
            {history.map((item) => (
              <div key={item.id} className="history-card">
                <div className="history-date">
                  <strong>Date: </strong> {new Date(item.created_at).toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>

                <div className="history-grid">
                  <div className="history-item">
                    <span className="item-label">Age:</span>
                    <span className="item-value">{item.age}</span>
                  </div>
                  <div className="history-item">
                    <span className="item-label">Gender:</span>
                    <span className="item-value">{item.gender}</span>
                  </div>
                  <div className="history-item">
                    <span className="item-label">Height:</span>
                    <span className="item-value">{item.height} cm</span>
                  </div>
                  <div className="history-item">
                    <span className="item-label">Weight:</span>
                    <span className="item-value">{item.weight} kg</span>
                  </div>
                  <div className="history-item">
                    <span className="item-label">BMI:</span>
                    <span className="item-value">{item.bmi}</span>
                  </div>

                  <div className="history-item">
                    <span className="item-label">Blood Pressure:</span>
                    <span className="item-value">{item.systolic_bp}/{item.diastolic_bp}</span>
                  </div>

                  <div className="history-item">
                    <span className="item-label">Cholesterol:</span>
                    <span className="item-value">{item.cholesterol}</span>
                  </div>
                  <div className="history-item">
                    <span className="item-label">Glucose:</span>
                    <span className="item-value">{item.glucose}</span>
                  </div>

                  <div className={`history-item risk-item risk-${item.risk_level?.toLowerCase()}`}>
                    <span className="item-label">Risk Level:</span>
                    <span className="item-value">{item.risk_level}</span>
                  </div>

                  <div className="history-item probability-item">
                    <span className="item-label">Probability:</span>
                    <span className="item-value">{item.probability}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}