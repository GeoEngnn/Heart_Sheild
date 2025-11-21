import React from "react";

export default function StatusBadge({ status }) {
  const color =
    status === "improving"
      ? "#27ae60"
      : status === "worsening"
      ? "#e74c3c"
      : "#f1c40f";

  return (
    <span
      style={{
        background: color,
        color: "white",
        padding: "5px 12px",
        borderRadius: "6px",
        fontWeight: "bold",
        textTransform: "capitalize",
      }}
    >
      {status}
    </span>
  );
}
