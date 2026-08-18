import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const STATUS_COLOR = {
  breached: "#dc2626",
  at_risk: "#f59e0b",
  on_time: "#16a34a",
};

export default function MapView({ incidents, selectedIncidentId, onSelectIncident }) {
  return (
    <div className="map-panel">
      <MapContainer center={[48.5, 10.0]} zoom={4} scrollWheelZoom className="leaflet-container">
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {incidents.map((incident) => (
          <CircleMarker
            key={incident.incident_id}
            center={[incident.lat, incident.lon]}
            radius={incident.incident_id === selectedIncidentId ? 12 : 7}
            pathOptions={{
              color: STATUS_COLOR[incident.breach_status] || "#64748b",
              fillColor: STATUS_COLOR[incident.breach_status] || "#64748b",
              fillOpacity: incident.anomaly_flag ? 0.9 : 0.6,
              weight: incident.anomaly_flag ? 3 : 1,
            }}
            eventHandlers={{ click: () => onSelectIncident(incident.incident_id) }}
          >
            <Popup>
              <strong>{incident.incident_type}</strong> — {incident.region}
              <br />
              Status: {incident.breach_status}
              <br />
              Breach risk: {(incident.breach_risk * 100).toFixed(0)}%
              {incident.anomaly_flag && (
                <>
                  <br />
                  <em>Flagged as anomaly</em>
                </>
              )}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
