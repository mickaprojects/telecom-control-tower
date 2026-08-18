const API_BASE = "http://127.0.0.1:8000";

async function getJson(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`${path} failed: ${res.status}`);
  }
  return res.json();
}

export function fetchIncidents(params = {}) {
  const query = new URLSearchParams(params).toString();
  return getJson(`/incidents${query ? `?${query}` : ""}`);
}

export function fetchFolders() {
  return getJson("/folders");
}

export function fetchStats() {
  return getJson("/stats");
}
