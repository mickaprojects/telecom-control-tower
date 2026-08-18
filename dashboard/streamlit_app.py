"""Streamlit dashboard — a simplified rebuild of the Renault Control Tower UI
(see renault/renault 01.PNG and renault 02.PNG) for telecom SLA tickets.
"""
from __future__ import annotations

import pandas as pd
import pydeck as pdk
import streamlit as st

from app.database import get_session, init_db
from app.models import Incident

STATUS_COLOR = {
    "breached": [220, 38, 38],
    "at_risk": [245, 158, 11],
    "on_time": [22, 163, 74],
}

st.set_page_config(page_title="Telecom SLA Control Tower", layout="wide")


@st.cache_data(ttl=30)
def load_incidents() -> pd.DataFrame:
    init_db()
    with get_session() as session:
        rows = session.query(Incident).all()
        data = [
            {c.name: getattr(row, c.name) for c in Incident.__table__.columns}
            for row in rows
        ]
        return pd.DataFrame(data)


df = load_incidents()

if df.empty:
    st.warning("No data yet — run `python -m pipeline.flows` first to populate the database.")
    st.stop()

st.title("📡 Telecom SLA Control Tower")
st.caption("Local Python/AI rebuild of the Renault Control Tower concept, adapted to telecom SLA monitoring.")

col_sidebar, col_map = st.columns([1, 3])

with col_sidebar:
    st.subheader("Folders")
    folder_counts = df.groupby("folder").size().sort_values(ascending=False)
    selected_folder = st.radio("Filter by folder", ["All"] + list(folder_counts.index))

    breached_count = int((df["breach_status"] == "breached").sum())
    st.metric("Tickets past SLA deadline", breached_count)
    st.metric("Anomalies flagged by AI", int(df["anomaly_flag"].sum()))

view_df = df if selected_folder == "All" else df[df["folder"] == selected_folder]

with col_map:
    st.subheader("Incident map")
    map_df = view_df.copy()
    map_df["color"] = map_df["breach_status"].map(STATUS_COLOR)
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[lon, lat]",
        get_fill_color="color",
        get_radius=25000,
        pickable=True,
    )
    view_state = pdk.ViewState(latitude=48.5, longitude=10.0, zoom=3.5)
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{incident_type} - {region}\n{breach_status}"},
        )
    )

st.subheader("Tickets")
display_cols = [
    "incident_id",
    "region",
    "incident_type",
    "severity",
    "folder",
    "status",
    "breach_status",
    "hours_margin",
    "breach_risk",
    "anomaly_flag",
]
st.dataframe(
    view_df[display_cols].sort_values("breach_risk", ascending=False),
    use_container_width=True,
    height=420,
)
