export default function Sidebar({ folders, selectedFolder, onSelectFolder, stats }) {
  const totalTickets = folders.reduce((sum, f) => sum + f.total, 0);

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <h3>Folders</h3>
        <ul className="folder-list">
          <li
            className={selectedFolder === "All" ? "active" : ""}
            onClick={() => onSelectFolder("All")}
          >
            <span>All incidents</span>
            <span className="folder-count">{totalTickets}</span>
          </li>
          {folders.map((folder) => (
            <li
              key={folder.folder}
              className={selectedFolder === folder.folder ? "active" : ""}
              onClick={() => onSelectFolder(folder.folder)}
            >
              <span>{folder.folder}</span>
              <span className="folder-count">{folder.total}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="sidebar-section alert-panel">
        <div className="alert-metric">
          <span className="alert-number">{stats ? stats.breached : "-"}</span>
          <span className="alert-label">tickets past SLA deadline</span>
        </div>
        <div className="alert-metric secondary">
          <span className="alert-number">{stats ? stats.anomalies : "-"}</span>
          <span className="alert-label">anomalies flagged by AI</span>
        </div>
      </div>
    </aside>
  );
}
