export default function StatusIndicator({ status }) {
  if (!status) return null;

  // Default values
  let color = "#999";
  let text = "Unknown";

  switch (status) {
    case "improving":
      color = "#2ecc71"; // green
      text = "Improving";
      break;

    case "worsening":
      color = "#e74c3c"; // red
      text = "Worsening";
      break;

    case "stable":
      color = "#f1c40f"; // yellow
      text = "Stable";
      break;

    case "no_data":
      color = "#7f8c8d"; // grey
      text = "No Data";
      break;

    default:
      color = "#999";
      text = "Unknown";
  }

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        padding: "6px 12px",
        borderRadius: "5px",
        background: "#1b1b1b",
        color: color,
        border: `1px solid ${color}`,
        fontSize: "14px",
        fontWeight: "bold",
      }}
    >
      <div
        style={{
          width: "10px",
          height: "10px",
          background: color,
          borderRadius: "50%",
          marginRight: "8px",
        }}
      ></div>

      {text}
    </div>
  );
}

