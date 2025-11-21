import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import DashboardCards from "../components/DashboardCards";
import VitalsChart from "../components/VitalsChart";
import { getUserStatus, getUserHistory } from "../services/api";

export default function Dashboard() {
  const user = JSON.parse(localStorage.getItem("heartshield_user"));
  const userId = user?.id;

  const [statusData, setStatusData] = useState(null);
  const [historyData, setHistoryData] = useState([]);

  useEffect(() => {
    if (!userId) return;

    getUserStatus(userId).then((res) => {
      if (res.success) setStatusData(res);
    });

    getUserHistory(userId).then((res) => {
      if (res.success) setHistoryData(res.historyData);
    });
  }, [userId]);

  return (
    <div className="dashboard-page">
      <Header />

      <h2 className="welcome">Welcome Back, {user?.username}</h2>

      {statusData && (
        <DashboardCards
          status={statusData.status}
          latest={statusData.latest}
        />
      )}

      <VitalsChart history={historyData.slice(0, 10).reverse()} />

      <div className="quick-actions">
        <a href={`/history/${userId}`} className="quick-btn">📜 View History</a>
        <a href="/profile" className="quick-btn">👤 Profile</a>
        <a href={`/chatbot/${userId}`} className="quick-btn">🤖 Chat with AI</a>
      </div>
    </div>
  );
}
