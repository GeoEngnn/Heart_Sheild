import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Header() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const stored = localStorage.getItem("heartshield_user");
    if (stored) {
      setUser(JSON.parse(stored));
    }
  }, []);

  function logout() {
    localStorage.removeItem("heartshield_user");
    navigate("/login");
  }

  return (
    <div
      style={{
        width: "100%",
        padding: "12px 20px",
        background: "#111",
        color: "white",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "20px",
      }}
    >
      {/* Left side - logo */}
      <div
        style={{
          fontSize: "20px",
          fontWeight: "bold",
          cursor: "pointer",
        }}
        onClick={() => navigate("/dashboard")}
      >
        HeartShield
      </div>

      {/* Right side */}
      <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
        {user ? (
          <>
            <a
              style={styles.link}
              href="http://localhost:5000/"
              target="_blank"
              rel="noopener noreferrer"
            >
              HeartShield
            </a>
            <Link style={styles.link} to="/history">
              History
            </Link>

            <Link style={styles.link} to="/profile">
              Profile
            </Link>

            {/* NEW: Correct chat route */}
            <Link style={styles.link} to="/chatbot/:userId">
              Chat
            </Link>

            <button style={styles.logout} onClick={logout}>
              Logout
            </button>
          </>
        ) : (
          <>
            <Link style={styles.link} to="/login">
              Login
            </Link>

            <Link style={styles.link} to="/register">
              Register
            </Link>
          </>
        )}
      </div>
    </div>
  );
}

const styles = {
  link: {
    color: "white",
    textDecoration: "none",
    fontSize: "15px",
  },
  logout: {
    padding: "6px 12px",
    background: "red",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
};
