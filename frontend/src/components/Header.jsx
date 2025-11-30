import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Header() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const initializeUser = () => {
      const stored = localStorage.getItem("heartshield_user");
      if (stored) {
        try {
          const userData = JSON.parse(stored);
          setUser(userData);
        } catch (error) {
          console.error("Error parsing user data:", error);
          localStorage.removeItem("heartshield_user");
        }
      }
    };

    initializeUser();
  }, []);

  function logout() {
    localStorage.removeItem("heartshield_user");
    setUser(null); // Clear user state
    navigate("/login");
  }

  return (
    <div className="navbar">
      {/* Left side - logo */}
      <div 
        className="logo"
        onClick={() => navigate("/dashboard")}
        style={{ cursor: "pointer" }}
      >
        HeartShield
      </div>

      {/* Right side */}
      <div className="nav-links">
        {user ? (
          <>
            {/* ADDED USER GREETING WITH FULL NAME */}
            <div className="user-greeting">
              Hello, {user.full_name || user.username}!
            </div>
            
            <a href="http://localhost:5000/" style={{color:"white"}}>Scan & Predict</a>
            <Link className="nav-link" to="/history">
              History
            </Link>
            <Link className="nav-link" to="/profile">
              Profile
            </Link>
            <Link className="nav-link" to="/chatbot">
              Chat
            </Link>
            <button className="logout-btn" onClick={logout}>
              Logout
            </button>
          </>
        ) : (
          <>
            <Link className="nav-link" to="/login">
              Login
            </Link>
            <Link className="nav-link" to="/register">
              Register
            </Link>
          </>
        )}
      </div>
    </div>
  );
}