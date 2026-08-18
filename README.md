# Telecom SLA Control Tower

A local, free Python prototype demonstrating the skills asked for in a
"Backend Software Engineer — Data Engineering & AI / Workflow Automation"
freelance offer (Python, data engineering, workflow automation, AI-enabled
applications), built as a telecom-flavored reimagining of the Renault
Control Tower Inbound project (see `../renault/`).

Instead of tracking transport trips against an ETA, it tracks telecom
network incidents / service tickets against an SLA deadline — same concept
(status dashboard, breach alerts, map, folders), different domain and stack
(Python instead of Java, with an added AI layer).

## Stack

- **Data pipeline**: Apache Beam (Python SDK, `DirectRunner`)
- **Workflow orchestration**: Prefect (local, no cloud account needed)
- **AI**: scikit-learn (SLA-breach risk classifier + Isolation Forest anomaly detector)
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: React (Vite) + Leaflet (OpenStreetMap tiles, no API key/billing)
- **Dashboard (alternative, Python-only)**: Streamlit + pydeck, kept as a quick data-app view
- **Tests**: pytest
- **Containerization**: Docker / docker-compose
- **CI**: GitHub Actions (runs once pushed to GitHub)

Everything runs locally at no cost — no GCP/cloud billing required.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Run the pipeline (generates data, trains models if needed, scores, persists)

```bash
python -m pipeline.flows
```

## Run the backend API

```bash
uvicorn app.main:app --reload
```

Then visit `http://localhost:8000/docs` for the interactive API docs.
CORS is enabled for `http://localhost:5173` (the frontend dev server).

## Run the frontend (React + Leaflet)

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. Requires the backend API running on
`http://127.0.0.1:8000` (see above). Compare the result against
`../renault/renault 01.PNG` and `../renault/renault 02.PNG`.

## Run the alternative Streamlit dashboard (optional)

```bash
streamlit run dashboard/streamlit_app.py
```

A faster, Python-only view of the same data — useful if you want a UI
without running the React dev server.

## Run the tests

```bash
pytest -q
```

## Run everything in Docker (API + Streamlit dashboard)

```bash
docker compose up --build
```

API on `http://localhost:8000`, Streamlit dashboard on `http://localhost:8501`.
The React frontend is not containerized in this demo — run it with `npm run dev`.
