const STATUS_LABEL = {
  breached: "Breached",
  at_risk: "At risk",
  on_time: "On time",
};

export default function IncidentTable({ incidents, selectedIncidentId, onSelectIncident, loading }) {
  const sorted = [...incidents].sort((a, b) => b.breach_risk - a.breach_risk);

  return (
    <div className="table-panel">
      <div className="table-header">
        <h3>Tickets</h3>
        {loading && <span className="loading-tag">Refreshing...</span>}
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Region</th>
              <th>Type</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Breach risk</th>
              <th>Anomaly</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((incident) => (
              <tr
                key={incident.incident_id}
                className={incident.incident_id === selectedIncidentId ? "selected" : ""}
                onClick={() => onSelectIncident(incident.incident_id)}
              >
                <td>{incident.region}</td>
                <td>{incident.incident_type}</td>
                <td>{incident.severity}</td>
                <td>
                  <span className={`status-pill ${incident.breach_status}`}>
                    {STATUS_LABEL[incident.breach_status]}
                  </span>
                </td>
                <td>{(incident.breach_risk * 100).toFixed(0)}%</td>
                <td>{incident.anomaly_flag ? "⚠️" : ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
