export default function StatusIndicator({ status }) {
  if (!status) return null;

  // Default values
  let statusClass = "status-unknown";
  let text = "Unknown";

  switch (status) {
    case "improving":
      statusClass = "status-improving";
      text = "Improving";
      break;

    case "worsening":
      statusClass = "status-worsening";
      text = "Worsening";
      break;

    case "stable":
      statusClass = "status-stable";
      text = "Stable";
      break;

    case "no_data":
      statusClass = "status-no-data";
      text = "No Data";
      break;

    default:
      statusClass = "status-unknown";
      text = "Unknown";
  }

  return (
    <div className={`status-indicator ${statusClass}`}>
      <div className="status-dot"></div>
      {text}
    </div>
  );
}