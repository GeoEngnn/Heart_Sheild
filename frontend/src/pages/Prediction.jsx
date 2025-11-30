import React, { useState } from "react";
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

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: isNaN(value) ? value : Number(value),
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const requestData = {
        ...formData,
        user_id: user?.id
      };

      console.log("📤 Sending prediction request...");
      console.log("🔑 User ID:", user?.id);

      const result = await makePrediction(requestData);

      if (result.success) {
        if (result.saved) {
          setMessage("✅ Prediction saved and analyzed successfully!");
        } else {
          setMessage("✅ Prediction analyzed successfully (not saved - user not logged in)");
        }
        setTimeout(() => {
          navigate("/dashboard");
        }, 2000);
      } else {
        setMessage("❌ Error: " + (result.error || "Unknown error"));
      }
    } catch (error) {
      console.error("Error:", error);
      setMessage("❌ Network error: " + error.message);
    } finally {
      setLoading(false);
    }
  };

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
                  <input
                    type="number"
                    name="Age"
                    value={formData.Age}
                    onChange={handleChange}
                    min="1"
                    max="120"
                    required
                  />
                </label>
                <label>
                  Height (cm):
                  <input
                    type="number"
                    name="Height"
                    value={formData.Height}
                    onChange={handleChange}
                    min="100"
                    max="250"
                    required
                  />
                </label>
                <label>
                  Weight (kg):
                  <input
                    type="number"
                    name="Weight"
                    value={formData.Weight}
                    onChange={handleChange}
                    min="30"
                    max="200"
                    required
                  />
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
                  Systolic BP (mmHg):
                  <input
                    type="number"
                    name="Systolic_BP"
                    value={formData.Systolic_BP}
                    onChange={handleChange}
                    min="60"
                    max="250"
                    required
                  />
                </label>
                <label>
                  Diastolic BP (mmHg):
                  <input
                    type="number"
                    name="Diastolic_BP"
                    value={formData.Diastolic_BP}
                    onChange={handleChange}
                    min="40"
                    max="150"
                    required
                  />
                </label>
                <label>
                  Cholesterol (mg/dL):
                  <input
                    type="number"
                    name="Cholesterol"
                    value={formData.Cholesterol}
                    onChange={handleChange}
                    min="50"
                    max="500"
                    required
                  />
                </label>
                <label>
                  Glucose (mg/dL):
                  <input
                    type="number"
                    name="Glucose"
                    value={formData.Glucose}
                    onChange={handleChange}
                    min="50"
                    max="500"
                    required
                  />
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

            {message && <div className={`message ${message.includes("✅") ? "success" : "error"}`}>{message}</div>}

            <button type="submit" className="btn-cta" disabled={loading}>
              {loading ? "Processing..." : "Get Prediction"}
            </button>
          </form>
        </div>
      </div>

      <style jsx>{`
        .prediction-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .prediction-card {
          background: white;
          padding: 40px;
          border-radius: 15px;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
          max-width: 900px;
          margin: 30px auto;
        }

        .form-section {
          margin-bottom: 30px;
          padding-bottom: 25px;
          border-bottom: 1px solid #eee;
        }

        .form-section h3 {
          color: #3498db;
          margin-bottom: 20px;
          font-size: 1.3rem;
        }

        .form-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
        }

        label {
          display: flex;
          flex-direction: column;
          font-weight: 600;
          color: #2c3e50;
          gap: 8px;
        }

        input,
        select {
          padding: 10px;
          border: 2px solid #e1e8ed;
          border-radius: 8px;
          font-size: 1rem;
          transition: border-color 0.3s;
        }

        input:focus,
        select:focus {
          outline: none;
          border-color: #3498db;
        }

        .message {
          padding: 15px;
          border-radius: 8px;
          margin: 20px 0;
          font-weight: 600;
        }

        .message.success {
          background: #d4edda;
          color: #155724;
          border: 1px solid #c3e6cb;
        }

        .message.error {
          background: #f8d7da;
          color: #721c24;
          border: 1px solid #f5c6cb;
        }

        .btn-cta {
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          padding: 15px 40px;
          border: none;
          border-radius: 8px;
          font-size: 1.1rem;
          font-weight: 600;
          cursor: pointer;
          width: 100%;
          margin-top: 20px;
          transition: all 0.3s;
        }

        .btn-cta:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .btn-cta:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
}
