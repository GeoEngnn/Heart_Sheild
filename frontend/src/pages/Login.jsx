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
      console.log('=== LOGIN DEBUG START ===');
      console.log('Sending login request to backend...');
      
      const response = await login({
        identifier,
        password,
      });

      console.log('=== RAW API RESPONSE ===');
      console.log('Full response:', response);
      console.log('Response keys:', Object.keys(response));
      
      if (response.success) {
        console.log('=== SUCCESSFUL LOGIN DATA ===');
        console.log('Response success:', response.success);
        console.log('User object:', response.user);
        console.log('User object type:', typeof response.user);
        
        if (response.user) {
          console.log('User object keys:', Object.keys(response.user));
          console.log('User ID:', response.user.id);
          console.log('Username:', response.user.username);
          console.log('Email:', response.user.email);
        } else {
          console.log('NO USER OBJECT IN RESPONSE!');
          console.log('Available keys in response:', Object.keys(response));
        }
        
        // Save to localStorage
        localStorage.setItem("heartshield_user", JSON.stringify(response.user));
        
        // Verify it was saved correctly
        const saved = localStorage.getItem("heartshield_user");
        console.log('=== LOCALSTORAGE VERIFICATION ===');
        console.log('Saved raw string:', saved);
        
        if (saved) {
          const parsedSaved = JSON.parse(saved);
          console.log('Parsed saved data:', parsedSaved);
          console.log('Parsed data keys:', Object.keys(parsedSaved));
          console.log('Parsed ID:', parsedSaved.id);
          console.log('Parsed username:', parsedSaved.username);
          console.log('Parsed email:', parsedSaved.email);
        }
        
        console.log('=== LOGIN DEBUG END ===');
        navigate("/dashboard");
      } else {
        console.log('Login failed:', response.error);
        setError(response.error || "Login failed");
      }
    } catch (err) {
      console.error('Login error details:', err);
      setError("Server error — check backend is running");
    }

    setLoading(false);
  };

  return (
    <div className="center-page">
      <div className="auth-card">
        <h2 className="auth-title">Sign In</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleLogin} className="auth-form">
          <div className="form-group">
            <label className="form-label">Email or Username</label>
            <input
              type="text"
              placeholder="example@gmail.com or username"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              placeholder="••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="form-input"
            />
          </div>

          <button 
            type="submit" 
            className="auth-button" 
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className="auth-switch-text">
          Don't have an account?{" "}
          <span className="auth-link" onClick={() => navigate("/register")}>
            Register
          </span>
        </p>
      </div>
    </div>
  );
}