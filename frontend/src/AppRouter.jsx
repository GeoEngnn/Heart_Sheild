import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import History from "./pages/History.jsx";
import Profile from "./pages/Profile.jsx";
import Chatbot from "./pages/Chatbot.jsx";
import Reviews from "./pages/Reviews";
import Prediction from "./pages/Prediction.jsx";

export default function AppRouter() {
  return (
    <div className="router-container">
      <Routes>
        {/* Default route */}
        <Route path="/" element={<Navigate to="/login" />} />

        {/* Auth */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* App pages */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/history" element={<History />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/prediction" element={<Prediction />} />

        {/* Chatbot - Added optional userId parameter and base route */}
        <Route path="/chatbot" element={<Chatbot />} />
        <Route path="/chatbot/:userId" element={<Chatbot />} />

        {/* Reviews Page */}
        <Route path="/reviews" element={<Reviews />} />

        {/* Catch-all */}
        <Route path="*" element={<div className="not-found-page">404 - Page Not Found</div>} />
      </Routes>
    </div>
  );
}