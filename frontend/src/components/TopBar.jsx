export default function TopBar({ stats, searchTerm, onSearchChange }) {
  return (
    <header className="top-bar">
      <div className="top-bar-left">
        <div className="operator-badge">TC</div>
        <div>
          <div className="operator-title">Telecom SLA Control Tower</div>
          <div className="operator-subtitle">Network Operator</div>
        </div>
      </div>
      <div className="top-bar-search">
        <input
          type="text"
          placeholder="Search incidents, regions, folders..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>
      <div className="top-bar-right">
        <span className="top-bar-item">MAP</span>
        <span className="top-bar-item">ALERTS{stats ? ` (${stats.breached})` : ""}</span>
      </div>
    </header>
  );
}
