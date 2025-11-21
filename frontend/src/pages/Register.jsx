import React, { useState } from "react";
import { register } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await register({
        username,
        email,
        password,
      });

      if (response.success) {
        navigate("/login");
      } else {
        setError(response.error || "Registration failed");
      }
    } catch (err) {
      console.error(err);
      setError("Server error — check backend");
    }

    setLoading(false);
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Create Account</h2>

        {error && <div style={styles.errorBox}>{error}</div>}

        <form onSubmit={handleRegister}>
          <label style={styles.label}>Username</label>
          <input
            type="text"
            placeholder="Choose a username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={styles.input}
          />

          <label style={styles.label}>Email</label>
          <input
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={styles.input}
          />

          <label style={styles.label}>Password</label>
          <input
            type="password"
            placeholder="••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={styles.input}
          />

          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? "Registering..." : "Register"}
          </button>
        </form>

        <p style={styles.switchText}>
          Already have an account?{" "}
          <span style={styles.link} onClick={() => navigate("/login")}>
            Login
          </span>
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    padding: "40px",
  },
  card: {
    width: "100%",
    maxWidth: "420px",
    background: "#fff",
    padding: "25px",
    borderRadius: "12px",
    boxShadow: "0 0 18px rgba(0,0,0,0.1)",
  },
  title: {
    textAlign: "center",
    marginBottom: "20px",
    fontSize: "24px",
    fontWeight: "bold",
  },
  label: {
    fontWeight: "bold",
    marginTop: "12px",
  },
  input: {
    width: "100%",
    padding: "10px",
    marginTop: "5px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    fontSize: "16px",
  },
  button: {
    width: "100%",
    marginTop: "20px",
    padding: "12px",
    background: "#4A4AE1",
    fontSize: "16px",
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
  },
  switchText: {
    marginTop: "15px",
    textAlign: "center",
    fontSize: "14px",
  },
  link: {
    color: "#4A4AE1",
    cursor: "pointer",
    fontWeight: "bold",
  },
  errorBox: {
    background: "#ffb3b3",
    padding: "10px",
    borderRadius: "6px",
    marginBottom: "15px",
    color: "#900",
    fontSize: "14px",
  },
};
