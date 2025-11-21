import React, { useState } from "react";
import { login } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState(""); // email or username
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      console.log('Sending login request to backend...');
      
      const response = await login({
        identifier,
        password,
      });

      console.log('Raw response:', response);
      
      if (response.success) {
        console.log('Login successful, user:', response.user);
        localStorage.setItem("heartshield_user", JSON.stringify(response.user));
        navigate("/dashboard");
      } else {
        setError(response.error || "Login failed");
      }
    } catch (err) {
      console.error('Login error details:', err);
      setError("Server error — check backend is running");
    }

    setLoading(false);
  };

  // Add this function to test backend connection
  const testBackendConnection = async () => {
    console.log('Testing backend connection...');
    try {
      const response = await fetch('http://127.0.0.1:5000');
      console.log('Backend connection test:', response.status, response.statusText);
      alert(`Backend connection: ${response.status} ${response.statusText}`);
    } catch (error) {
      console.error('Backend connection failed:', error);
      alert('Backend connection FAILED - check if server is running');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Sign In</h2>

        {error && <div style={styles.errorBox}>{error}</div>}

        <form onSubmit={handleLogin}>
          <label style={styles.label}>Email or Username</label>
          <input
            type="text"
            placeholder="example@gmail.com or username"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
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
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        {/* Temporary test button - add this */}
        <button 
          type="button" 
          onClick={testBackendConnection}
          style={{...styles.button, background: '#666', marginTop: '10px'}}
        >
          Test Backend Connection
        </button>

        <p style={styles.switchText}>
          Don't have an account?{" "}
          <span style={styles.link} onClick={() => navigate("/register")}>
            Register
          </span>
        </p>
      </div>
    </div>
  );
}

// Minimal inline styles
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