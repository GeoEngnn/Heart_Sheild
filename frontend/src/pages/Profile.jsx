import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import { useNavigate } from "react-router-dom";

export default function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const loadUserData = () => {
      console.log('=== PROFILE DEBUG START ===');
      
      const stored = localStorage.getItem("heartshield_user");
      console.log('Raw heartshield_user from localStorage:', stored);
      
      if (!stored) {
        console.log('No user data found in localStorage');
        navigate("/login");
        return;
      }

      try {
        const userData = JSON.parse(stored);
        console.log('Parsed user data in Profile:', userData);
        
        // Format user data with fallbacks
        const formattedUser = {
          id: userData.id || userData.user_id || "N/A",
          username: userData.username || "N/A",
          email: userData.email || "N/A",
          joined: userData.created_at || userData.joined_date || formatCurrentDate()
        };
        
        console.log('Formatted user data:', formattedUser);
        setUser(formattedUser);
      } catch (error) {
        console.error('Error parsing user data in Profile:', error);
        navigate("/login");
      } finally {
        setLoading(false);
      }
      
      console.log('=== PROFILE DEBUG END ===');
    };

    loadUserData();
  }, [navigate]);

  // Helper function to format current date as fallback
  const formatCurrentDate = () => {
    return new Date().toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleLogout = () => {
    localStorage.removeItem("heartshield_user");
    navigate("/login");
  };

  if (loading) {
    return (
      <div className="profile-page">
        <Header />
        <div className="loading-container">Loading profile...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="profile-page">
        <Header />
        <div className="error-container">
          <p>Unable to load user data. Please log in again.</p>
          <button onClick={() => navigate("/login")} className="auth-button">
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <Header />
      <div className="app-container">
        <h2 className="page-title">My Profile</h2>

        <div className="profile-card">
          <div className="profile-info">
            {/* User ID Field */}
            <div className="info-row">
              <strong>User ID:</strong> 
              <span className="field-data">{user.id}</span>
            </div>

            {/* Username Field */}
            <div className="info-row">
              <strong>Username:</strong> 
              <span className="field-data">{user.username}</span>
            </div>

            {/* Email Field */}
            <div className="info-row">
              <strong>Email:</strong> 
              <span className="field-data">{user.email}</span>
            </div>

            {/* Joined Date Field */}
            <div className="info-row">
              <strong>Joined:</strong> 
              <span className="field-data">{user.joined}</span>
            </div>
          </div>

          <button className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}