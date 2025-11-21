import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Header from "../components/Header";
import { getUserHistory } from "../services/api";

export default function History() {
  const { userId: routeUserId } = useParams();
  const storedUser = JSON.parse(localStorage.getItem("heartshield_user"));
  const userId = routeUserId || storedUser?.id;

  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!userId) {
      setError("No logged-in user.");
      setLoading(false);
      return;
    }

    (async () => {
      try {
        const res = await getUserHistory(userId);
        if (res.success) {
          setHistory(res.historyData);
        } else {
          setError(res.error || "Unable to load history.");
        }
      } catch (e) {
        setError("Server error. Check backend.");
      }
      setLoading(false);
    })();
  }, [userId]);

  if (loading) return <p style={styles.loading}>Loading history…</p>;
  if (error) return <p style={styles.error}>{error}</p>;

  return (
    <div style={styles.container}>
      <Header />
      <h2 style={styles.title}>Prediction History</h2>

      {history.length === 0 ? (
        <p>No previous predictions found.</p>
      ) : (
        <div style={styles.list}>
          {history.map((item) => (
            <div key={item.id} style={styles.card}>
              <div style={styles.row}>
                <strong>Date: </strong> {item.created_at}
              </div>

              <div style={styles.grid}>
                <div style={styles.item}>Age: {item.age}</div>
                <div style={styles.item}>Gender: {item.gender}</div>
                <div style={styles.item}>Height: {item.height} cm</div>
                <div style={styles.item}>Weight: {item.weight} kg</div>
                <div style={styles.item}>BMI: {item.bmi}</div>

                <div style={styles.item}>
                  BP: {item.systolic_bp}/{item.diastolic_bp}
                </div>

                <div style={styles.item}>Cholesterol: {item.cholesterol}</div>
                <div style={styles.item}>Glucose: {item.glucose}</div>

                <div style={{ ...styles.item, color: getRiskColor(item.risk_level), fontWeight: "bold" }}>
                  Risk: {item.risk_level}
                </div>

                <div style={styles.item}>
                  Probability: {(item.probability * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function getRiskColor(level) {
  if (level === "High") return "#e74c3c";
  if (level === "Moderate") return "#f1c40f";
  if (level === "Low") return "#2ecc71";
  return "#333";
}

const styles = {
  container: {
    padding: "20px",
    maxWidth: "900px",
    margin: "0 auto",
  },
  loading: {
    textAlign: "center",
    marginTop: "30px",
    fontSize: "16px",
  },
  error: {
    color: "red",
    textAlign: "center",
    marginTop: "30px",
  },
  title: {
    fontSize: "24px",
    fontWeight: "bold",
    marginBottom: "20px",
  },
  list: {
    marginTop: "15px",
  },
  card: {
    background: "#fff",
    padding: "15px",
    borderRadius: "10px",
    boxShadow: "0 0 10px rgba(0,0,0,0.1)",
    marginBottom: "15px",
  },
  row: {
    marginBottom: "12px",
    fontSize: "15px",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
    gap: "10px",
  },
  item: {
    background: "#f7f7f7",
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #ddd",
  },
};
