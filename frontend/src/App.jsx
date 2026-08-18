import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { fetchFolders, fetchIncidents, fetchStats } from "./api";
import IncidentTable from "./components/IncidentTable";
import MapView from "./components/MapView";
import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";

export default function App() {
  const [incidents, setIncidents] = useState([]);
  const [folders, setFolders] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedFolder, setSelectedFolder] = useState("All");
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setLoading(true);
        const [incidentsData, foldersData, statsData] = await Promise.all([
          fetchIncidents({ limit: 1000 }),
          fetchFolders(),
          fetchStats(),
        ]);
        if (!cancelled) {
          setIncidents(incidentsData);
          setFolders(foldersData);
          setStats(statsData);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    const interval = setInterval(load, 30000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const visibleIncidents = useMemo(() => {
    let result = incidents;

    if (selectedFolder !== "All") {
      result = result.filter((incident) => incident.folder === selectedFolder);
    }

    const query = searchTerm.trim().toLowerCase();
    if (query) {
      result = result.filter((incident) =>
        [
          incident.incident_id,
          incident.region,
          incident.incident_type,
          incident.folder,
          incident.severity,
          incident.status,
          incident.breach_status,
        ]
          .join(" ")
          .toLowerCase()
          .includes(query)
      );
    }

    return result;
  }, [incidents, selectedFolder, searchTerm]);

  return (
    <div className="app">
      <TopBar stats={stats} searchTerm={searchTerm} onSearchChange={setSearchTerm} />
      {error && (
        <div className="error-banner">
          Backend unreachable ({error}). Start it with: uvicorn app.main:app --reload
        </div>
      )}
      <div className="app-body">
        <Sidebar
          folders={folders}
          selectedFolder={selectedFolder}
          onSelectFolder={setSelectedFolder}
          stats={stats}
        />
        <main className="main-panel">
          <MapView
            incidents={visibleIncidents}
            selectedIncidentId={selectedIncidentId}
            onSelectIncident={setSelectedIncidentId}
          />
          <IncidentTable
            incidents={visibleIncidents}
            selectedIncidentId={selectedIncidentId}
            onSelectIncident={setSelectedIncidentId}
            loading={loading}
          />
        </main>
      </div>
    </div>
  );
}
