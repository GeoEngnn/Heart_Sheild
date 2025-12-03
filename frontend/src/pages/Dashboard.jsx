import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getUserStatus, getUserHistory } from "../services/api";
import DashboardCards from "../components/DashboardCards";
import VitalsChart from "../components/VitalsChart";
import bgImage from "../assets/app.png"

export default function Dashboard() {
  const user = JSON.parse(localStorage.getItem("heartshield_user"));
  const userId = user?.id;

  const [status, setStatus] = useState(null);
  const [historyData, setHistoryData] = useState([]);

  // Function to refresh data from backend
  const refreshData = async () => {
    if (!userId) return;
    try {
      const statusRes = await getUserStatus(userId);
      setStatus(statusRes);
      console.log("✅ Fetched user status:", statusRes);
      const historyRes = await getUserHistory(userId);
      if (historyRes.success) setHistoryData(historyRes.historyData);

      console.log("✅ Dashboard data refreshed at", new Date().toLocaleTimeString());
    } catch (error) {
      console.error("Error refreshing data:", error);
    }
  };

  // Initial load
  useEffect(() => {
    if (userId) {
      refreshData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  // Auto-refresh every 2 seconds to catch new predictions immediately
  useEffect(() => {
    if (!userId) return;

    const interval = setInterval(() => {
      refreshData();
    }, 2000);

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const handleLogout = () => {
    localStorage.removeItem("heartshield_user");
    window.location.href = "/login";
  };

  return (
    <div className="dashboard-page" style={{
      backgroundImage: `url(${bgImage})`,
      backgroundSize: 'cover',
      backgroundRepeat: 'no-repeat',
      backgroundPosition: 'center',
      width: '100%',
      height: '100vh'
    }}>
      <div className="navbar">
        <h2>HeartShield</h2>
        <div className="nav-links">
          <a href="http://localhost:5000/">Scan & Predict</a>
          <Link to="/history">History</Link>
          <Link to="/profile">Profile</Link>
          <Link to="/chatbot">Chat</Link>
          <button
            className="btn-cta logout-btn"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </div>

      <div className="app-container">
        <h1 className="welcome-title">Welcome Back, {user?.username}</h1>

        <div className="dashboard-cards">
          <div className="dashboard-card status-card">
            <div className="card-header">
              <h3 className="card-title">Status</h3>
              <span className={`status-badge ${status?.status === 'no_data' ? 'status-no-data' : ''}`}>
                {status?.status === 'no_data'
                  ? "No Data Yet"
                  : status?.status
                    ? status.status.charAt(0).toUpperCase() + status.status.slice(1)
                    : "Loading..."}
              </span>
            </div>
            <div className="card-content">
              <div className="metric-value">
                {status?.status === 'no_data'
                  ? "Complete a scan to see your status"
                  : status?.status
                    ? status.status.charAt(0).toUpperCase() + status.status.slice(1)
                    : "N/A"}
              </div>
            </div>
          </div>

          <div className="dashboard-card risk-card">
            <div className="card-header">
              <h3 className="card-title">Latest Risk</h3>
            </div>
            <div className="card-content">
              <div className="metric-label">Cardiovascular Risk</div>
              <div className="metric-value">
                {status?.latest_risk
                  ? status.latest_risk
                  : "No prediction yet"}
              </div>
            </div>
          </div>

          <div className="dashboard-card bmi-card">
            <div className="card-header">
              <h3 className="card-title">BMI</h3>
            </div>
            <div className="card-content">
              <div className="metric-label">Body Mass Index</div>
              <div className="metric-value">
                {status?.latest?.bmi
                  ? status.latest.bmi.toFixed(1)
                  : "No data"}
              </div>
            </div>
          </div>
        </div>

        <div className="chart-section">
          <VitalsChart history={historyData.slice(0, 10).reverse()} />
        </div>

        <div className="quick-actions">
          <Link className="btn-cta action-btn" to="/history">View History</Link>
          <Link className="btn-cta action-btn" to="/profile">Profile</Link>
          <Link className="btn-cta action-btn" to="/chatbot">Chat with AI</Link>
          <Link className="btn-cta action-btn" to="/reviews">Reviews</Link>
        </div>
      </div>
    </div>
  );
}