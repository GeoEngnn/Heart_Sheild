import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import History from "./pages/History.jsx";
import Profile from "./pages/Profile.jsx";
import Chatbot from "./pages/Chatbot.jsx";   // ✅ NEW IMPORT

export default function AppRouter() {
  return (
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

      {/* NEW: Chatbot */}
      <Route path="/chatbot/:userId" element={<Chatbot />} />   {/* ✅ NEW ROUTE */}

      {/* Catch-all */}
      <Route path="*" element={<h1>404 - Not Found</h1>} />
    </Routes>
  );
}
