import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import { useNavigate } from "react-router-dom";

export default function Profile() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const stored = localStorage.getItem("heartshield_user");
    if (!stored) {
      navigate("/login");
      return;
    }
    setUser(JSON.parse(stored));
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("heartshield_user");
    navigate("/login");
  };

  if (!user) return <p style={styles.loading}>Loading...</p>;

  return (
    <div style={styles.container}>
      <Header />

      <h2 style={styles.title}>My Profile</h2>

      <div style={styles.card}>
        <div style={styles.row}>
          <strong>User ID:</strong> {user.id}
        </div>

        <div style={styles.row}>
          <strong>Username:</strong> {user.username}
        </div>

        <div style={styles.row}>
          <strong>Email:</strong> {user.email}
        </div>

        {user.created_at && (
          <div style={styles.row}>
            <strong>Joined:</strong> {user.created_at}
          </div>
        )}

        <button style={styles.logoutBtn} onClick={handleLogout}>
          Logout
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    padding: "20px",
    maxWidth: "700px",
    margin: "0 auto",
  },
  loading: {
    textAlign: "center",
    marginTop: "40px",
  },
  title: {
    fontSize: "22px",
    fontWeight: "bold",
    marginBottom: "20px",
  },
  card: {
    background: "#fff",
    padding: "20px",
    borderRadius: "12px",
    boxShadow: "0 0 12px rgba(0,0,0,0.1)",
  },
  row: {
    marginBottom: "12px",
    fontSize: "15px",
  },
  logoutBtn: {
    marginTop: "20px",
    width: "100%",
    padding: "12px",
    background: "#E74C3C",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    fontSize: "16px",
    cursor: "pointer",
  },
};
