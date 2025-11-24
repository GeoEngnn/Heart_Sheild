import React from "react";

export default function StatusBadge({ status }) {
  const statusClass = status ? `status-${status.toLowerCase()}` : 'status-unknown';
  
  return (
    <span className={`status-badge ${statusClass}`}>
      {status || "Unknown"}
    </span>
  );
}