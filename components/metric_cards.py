# components/metric_cards.py — KPI cards for all sensors

import streamlit as st
from config import SENSORS, get_sensor_status, STATUS_COLORS

def render_metric_cards(readings: dict):
    """
    Renders a responsive grid of metric cards.
    readings: dict like { "aqi": 85, "temperature": 28.5, ... }
    """

    keys = list(readings.keys())
    cols = st.columns(len(keys) if len(keys) <= 4 else 4)

    for i, key in enumerate(keys):
        col = cols[i % 4]
        value = readings[key]
        sensor = SENSORS.get(key, {})

        label = sensor.get("label", key.upper())
        unit = sensor.get("unit", "")
        icon = sensor.get("icon", "📊")
        status = get_sensor_status(key, value)
        status_color = STATUS_COLORS[status]

        # Delta placeholder — in real app pass previous reading
        with col:
            _render_card(icon, label, value, unit, status, status_color)

        # New row every 4 cards
        if (i + 1) % 4 == 0 and (i + 1) < len(keys):
            cols = st.columns(min(len(keys) - (i + 1), 4))


def _render_card(icon, label, value, unit, status, status_color):
    """Renders a single styled metric card."""

    # Format value nicely
    if isinstance(value, float):
        display_val = f"{value:.1f}"
    else:
        display_val = str(int(value))

    st.markdown(f"""
        <div style="
            background: #1a1a2e;
            border: 1px solid #2a2a4a;
            border-left: 4px solid {status_color};
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
            ">
                <div>
                    <div style="
                        font-size: 1.6rem;
                        margin-bottom: 6px;
                    ">{icon}</div>
                    <div style="
                        color: #8888aa;
                        font-size: 0.75rem;
                        font-weight: 600;
                        letter-spacing: 0.8px;
                        text-transform: uppercase;
                    ">{label}</div>
                </div>
                <div style="
                    background: {status_color}22;
                    color: {status_color};
                    border-radius: 20px;
                    padding: 3px 10px;
                    font-size: 0.7rem;
                    font-weight: 700;
                    letter-spacing: 0.5px;
                ">{status.upper()}</div>
            </div>

            <div style="margin-top: 14px;">
                <span style="
                    font-size: 2rem;
                    font-weight: 800;
                    color: #ffffff;
                    line-height: 1;
                ">{display_val}</span>
                <span style="
                    font-size: 0.9rem;
                    color: #8888aa;
                    margin-left: 4px;
                ">{unit}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)