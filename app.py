# app.py — Main entry point, ties all components together

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from config import (
    APP_TITLE, REFRESH_INTERVAL_MS, HISTORY_POINTS,
    SENSORS, CHART_COLORS
)
# from components.header import render_header
from components.metric_cards import render_metric_cards
from components.charts import (
    render_aqi_gauge,
    render_mini_gauge,
    render_line_chart,
    render_bar_snapshot,
    render_heatmap,
)
from components.table import render_table



# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  LOAD CUSTOM CSS
# ─────────────────────────────────────────────
def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ─────────────────────────────────────────────
#  AUTO REFRESH
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
#  SESSION STATE — History buffer
# ─────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(
        columns=["timestamp"] + list(SENSORS.keys())
    )

# ─────────────────────────────────────────────
#  DATA INGESTION
#  Replace this function with your real sensor
#  API call, MQTT read, or CSV import.
# ─────────────────────────────────────────────
def get_latest_readings() -> dict:
    """
    ── REPLACE THIS WITH YOUR REAL DATA SOURCE ──
    Expected return format:
    {
        "aqi":         85.0,
        "temperature": 28.5,
        "humidity":    60.0,
        "co2":         750.0,
        "oxygen":      20.5,
        "pm25":        22.0,
        "pm10":        45.0,
        "voc":         180.0,
        "noise":       52.0,
    }
    """
    # ── Placeholder: random values within realistic ranges ──
    # Delete this block once you connect real sensors
    return {
        "aqi":         float(np.random.randint(30, 180)),
        "temperature": round(np.random.uniform(22, 38), 1),
        "humidity":    round(np.random.uniform(40, 80), 1),
        "co2":         float(np.random.randint(400, 1500)),
        "oxygen":      round(np.random.uniform(19.0, 21.0), 1),
        "pm25":        round(np.random.uniform(5, 80), 1),
        "pm10":        round(np.random.uniform(10, 150), 1),
        "voc":         float(np.random.randint(50, 400)),
        "noise":       float(np.random.randint(35, 85)),
    }


def append_to_history(readings: dict):
    """Appends latest readings to session history, trims to HISTORY_POINTS."""
    row = {"timestamp": datetime.now(), **readings}
    new_row = pd.DataFrame([row])
    st.session_state.history = pd.concat(
        [st.session_state.history, new_row], ignore_index=True
    )
    # Keep only last N points
    if len(st.session_state.history) > HISTORY_POINTS:
        st.session_state.history = st.session_state.history.iloc[-HISTORY_POINTS:]


# ─────────────────────────────────────────────
#  FETCH CURRENT DATA
# ─────────────────────────────────────────────
readings = get_latest_readings()
append_to_history(readings)
history_df = st.session_state.history.copy()


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 10px 0 20px 0;'>
            <div style='font-size: 2.5rem;'>🌬️</div>
            <div style='color:#ccccee; font-weight:700; font-size:1.1rem;'>AQI Monitor</div>
            <div style='color:#8888aa; font-size:0.75rem;'>Air Quality Dashboard</div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Sensor toggles ──
    st.markdown("**📡 Sensors to Display**")
    selected_sensors = []
    for key, sensor in SENSORS.items():
        checked = st.checkbox(
            f"{sensor['icon']} {sensor['label']}",
            value=True,
            key=f"toggle_{key}"
        )
        if checked:
            selected_sensors.append(key)

    st.divider()

    # ── Chart selectors ──
    st.markdown("**📈 Chart Options**")
    show_gauges   = st.toggle("Show Mini Gauges",   value=True)
    show_linechart = st.toggle("Show Line Charts",  value=True)
    show_bar      = st.toggle("Show Bar Snapshot",  value=True)
    show_heatmap  = st.toggle("Show Heatmap",       value=False)

    st.divider()

    # ── Line chart sensor picker ──
    if show_linechart:
        st.markdown("**📉 Line Chart Sensors**")
        chart_sensors = st.multiselect(
            "Pick sensors",
            options=selected_sensors,
            default=selected_sensors[:4] if len(selected_sensors) >= 4 else selected_sensors,
            label_visibility="collapsed",
        )

    st.divider()

    # ── Info box ──
    st.markdown(f"""
        <div style='
            background:#1a1a2e;
            border:1px solid #2a2a4a;
            border-radius:10px;
            padding:12px 16px;
            font-size:0.78rem;
            color:#8888aa;
            line-height:1.6;
        '>
            🔄 Refreshes every {REFRESH_INTERVAL_MS // 1000}s<br>
            📦 Stores last {HISTORY_POINTS} readings<br>
            🕐 {datetime.now().strftime("%H:%M:%S")}
        </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN LAYOUT
# ─────────────────────────────────────────────

# ── Header ──────────────────────────────────

# ── Tabs ────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Overview",
    "📈  Trends",
    "🔬  Deep Dive",
    "📋  History",
])


# ════════════════════════════════════════════
#  TAB 1 — OVERVIEW
# ════════════════════════════════════════════
with tab1:

    # Metric cards — filtered by sidebar toggles
    filtered_readings = {k: v for k, v in readings.items() if k in selected_sensors}
    render_metric_cards(filtered_readings)

    st.markdown("---")

    # AQI Gauge + Bar snapshot side by side
    col_left, col_right = st.columns([1, 1.4])

    with col_left:
        render_aqi_gauge(readings["aqi"])

    with col_right:
        if show_bar and filtered_readings:
            render_bar_snapshot(filtered_readings)
        else:
            st.info("Enable 'Bar Snapshot' in sidebar to view.")


# ════════════════════════════════════════════
#  TAB 2 — TRENDS
# ════════════════════════════════════════════
with tab2:

    if history_df.empty or len(history_df) < 2:
        st.info("⏳ Collecting data... Trends will appear after a few readings.")
    else:
        if show_linechart:
            sensors_to_plot = chart_sensors if chart_sensors else selected_sensors
            if sensors_to_plot:
                # Group 1: AQI + Particulates
                primary = [s for s in sensors_to_plot if s in ["aqi", "pm25", "pm10", "voc"]]
                if primary:
                    render_line_chart(history_df, primary, "🌫️ AQI & Particulates")

                # Group 2: Climate
                climate = [s for s in sensors_to_plot if s in ["temperature", "humidity"]]
                if climate:
                    render_line_chart(history_df, climate, "🌡️ Temperature & Humidity")

                # Group 3: Gas levels
                gases = [s for s in sensors_to_plot if s in ["co2", "oxygen", "noise"]]
                if gases:
                    render_line_chart(history_df, gases, "☁️ Gas Levels & Noise")
            else:
                st.warning("Select at least one sensor in the sidebar.")
        else:
            st.info("Enable 'Line Charts' in sidebar to view trends.")


# ════════════════════════════════════════════
#  TAB 3 — DEEP DIVE
# ════════════════════════════════════════════
with tab3:

    st.markdown("### 🔬 Individual Sensor Gauges")

    if not selected_sensors:
        st.warning("No sensors selected. Enable them in the sidebar.")
    else:
        # Render mini gauges in rows of 3
        sensor_chunks = [
            selected_sensors[i:i+3]
            for i in range(0, len(selected_sensors), 3)
        ]

        for chunk in sensor_chunks:
            cols = st.columns(len(chunk))
            for col, key in zip(cols, chunk):
                with col:
                    if show_gauges:
                        render_mini_gauge(key, readings[key])
                    else:
                        sensor = SENSORS[key]
                        st.metric(
                            label=f"{sensor['icon']} {sensor['label']}",
                            value=f"{readings[key]:.1f} {sensor['unit']}",
                        )

        st.markdown("---")

        # Heatmap
        if show_heatmap:
            if len(history_df) > 5:
                render_heatmap(history_df[["timestamp"] + selected_sensors])
            else:
                st.info("⏳ Need more data points for heatmap.")
        else:
            st.info("Enable 'Show Heatmap' in the sidebar to view correlations.")


# ════════════════════════════════════════════
#  TAB 4 — HISTORY TABLE
# ════════════════════════════════════════════
with tab4:

    if history_df.empty:
        st.info("No data yet. Readings will appear here automatically.")
    else:
        table_df = history_df[["timestamp"] + selected_sensors].copy()
        render_table(table_df)
