import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import { useNavigate } from "react-router-dom";

// Helper function to format current date as fallback
const formatCurrentDate = () => {
  return new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

// NEW FUNCTION: Format join date to readable format
const formatJoinDate = (dateString) => {
  if (!dateString) {
    return formatCurrentDate(); // Fallback to current date if no date provided
  }

  try {
    const date = new Date(dateString);
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      console.warn('Invalid date string:', dateString);
      return formatCurrentDate();
    }

    // Format to readable string, e.g., "November 27, 2025 at 3:02 PM"
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      hour12: true
    });
  } catch (error) {
    console.error('Error formatting date:', error, dateString);
    return formatCurrentDate();
  }
};

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

        // Format user data with fallbacks - ADDED FULL_NAME
        const formattedUser = {
          id: userData.id || userData.user_id || "N/A",
          username: userData.username || "N/A",
          email: userData.email || "N/A",
          full_name: userData.full_name || "Not set",
          joined: formatJoinDate(userData.created_at || userData.joined_date) // UPDATED THIS LINE
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

    // Auto-refresh user data every 5 seconds to catch any updates
    const interval = setInterval(() => {
      loadUserData();
    }, 5000);

    return () => clearInterval(interval);
  }, [navigate]);

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
            {/* ADDED FULL NAME FIELD */}
            <div className="info-row">
              <strong>Full Name:</strong> 
              <span className="field-data">{user.full_name}</span>
            </div>

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
