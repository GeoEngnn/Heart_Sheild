import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import { makePrediction } from "../services/api";

export default function Prediction() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("heartshield_user"));

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [formData, setFormData] = useState({
    Age: 52,
    Height: 175,
    Weight: 80,
    Gender: "Male",
    Systolic_BP: 125,
    Diastolic_BP: 85,
    Cholesterol: 212,
    Glucose: 98,
    Smoking: 0,
    Alcohol_Intake: 0,
    Physical_Activity: 1,
  });

  // 🔥 Guarantee log prints when component loads
  useEffect(() => {
    console.log("🔥 Prediction component mounted");
    console.log("👤 User object from localStorage:", user);

    if (!user) {
      console.warn("⚠️ No user found — redirecting to login");
    }
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: isNaN(value) ? value : Number(value),
    });

    console.log(`✏️ Updated field: ${name} →`, value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    console.log("🚀 handleSubmit() TRIGGERED");
    console.log("📌 Current formData:", formData);
    console.log("👤 Active User:", user);

    setLoading(true);
    setMessage("");

    try {
      const requestData = {
        ...formData,
        user_id: user?.id,
      };

      console.log("📤 Sending prediction request to backend with payload:", requestData);

      const result = await makePrediction(requestData);

      console.log("📥 Backend Response Received:", result);

      if (result.success) {
        if (result.saved) {
          setMessage("✅ Prediction saved and analyzed successfully!");
        } else {
          setMessage("✅ Prediction analyzed successfully (not saved - user not logged in)");
        }

        console.log("➡️ Navigating to dashboard in 2 seconds...");

        setTimeout(() => {
          navigate("/dashboard");
        }, 2000);
      } else {
        console.error("❌ Backend returned an error:", result.error);
        setMessage("❌ Error: " + (result.error || "Unknown error"));
      }
    } catch (error) {
      console.error("❌ NETWORK ERROR:", error);
      setMessage("❌ Network error: " + error.message);
    } finally {
      console.log("⏳ Finished processing prediction request");
      setLoading(false);
    }
  };

  // If user not logged in
  if (!user) {
    return (
      <div className="auth-container">
        <h2>Please log in to make predictions</h2>
        <button onClick={() => navigate("/login")} className="btn-cta">
          Go to Login
        </button>
      </div>
    );
  }

  return (
    <div className="prediction-page">
      <Header />
      <div className="app-container">
        <h1>🧪 Heart Disease Risk Prediction</h1>
        <p>Enter your health data to get an AI-powered risk assessment</p>

        <div className="prediction-card">
          <form onSubmit={handleSubmit}>
            <div className="form-section">
              <h3>📊 Basic Information</h3>
              <div className="form-grid">
                <label>
                  Age (years):
                  <input type="number" name="Age" value={formData.Age} onChange={handleChange} required />
                </label>
                <label>
                  Height (cm):
                  <input type="number" name="Height" value={formData.Height} onChange={handleChange} required />
                </label>
                <label>
                  Weight (kg):
                  <input type="number" name="Weight" value={formData.Weight} onChange={handleChange} required />
                </label>
                <label>
                  Gender:
                  <select name="Gender" value={formData.Gender} onChange={handleChange} required>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                  </select>
                </label>
              </div>
            </div>

            <div className="form-section">
              <h3>❤️ Vital Signs</h3>
              <div className="form-grid">
                <label>
                  Systolic BP:
                  <input type="number" name="Systolic_BP" value={formData.Systolic_BP} onChange={handleChange} required />
                </label>
                <label>
                  Diastolic BP:
                  <input type="number" name="Diastolic_BP" value={formData.Diastolic_BP} onChange={handleChange} required />
                </label>
                <label>
                  Cholesterol:
                  <input type="number" name="Cholesterol" value={formData.Cholesterol} onChange={handleChange} required />
                </label>
                <label>
                  Glucose:
                  <input type="number" name="Glucose" value={formData.Glucose} onChange={handleChange} required />
                </label>
              </div>
            </div>

            <div className="form-section">
              <h3>🏃 Lifestyle Factors</h3>
              <div className="form-grid">
                <label>
                  Smoking:
                  <select name="Smoking" value={formData.Smoking} onChange={handleChange} required>
                    <option value="0">No</option>
                    <option value="1">Yes</option>
                  </select>
                </label>
                <label>
                  Alcohol Intake:
                  <select name="Alcohol_Intake" value={formData.Alcohol_Intake} onChange={handleChange} required>
                    <option value="0">No</option>
                    <option value="1">Yes</option>
                  </select>
                </label>
                <label>
                  Physical Activity:
                  <select name="Physical_Activity" value={formData.Physical_Activity} onChange={handleChange} required>
                    <option value="1">Active</option>
                    <option value="0">Inactive</option>
                  </select>
                </label>
              </div>
            </div>

            {message && (
              <div className={`message ${message.includes("✅") ? "success" : "error"}`}>{message}</div>
            )}

            <button type="submit" className="btn-cta" disabled={loading}>
              {loading ? "Processing..." : "Get Prediction"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
