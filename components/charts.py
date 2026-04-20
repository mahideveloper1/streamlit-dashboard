# components/charts.py

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config import SENSORS, CHART_COLORS, get_aqi_info


# ✅ Helper: HEX → RGBA (IMPORTANT)
def hex_to_rgba(hex_color, alpha=0.2):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ─────────────────────────────────────────────
# AQI GAUGE
# ─────────────────────────────────────────────
def render_aqi_gauge(aqi_value: float):

    aqi_info = get_aqi_info(aqi_value)
    color = aqi_info["color"]
    label = aqi_info["label"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=aqi_value,
        number={"font": {"size": 52, "color": "#ffffff"}},
        delta={
            "reference": 100,
            "increasing": {"color": "#ff6b6b"},
            "decreasing": {"color": "#00e400"},
        },
        gauge={
            "axis": {"range": [0, 500]},
            "bar": {"color": color},
            "bgcolor": "#1a1a2e",
            "steps": [
                {"range": [0, 50], "color": "rgba(0,228,0,0.13)"},
                {"range": [51, 100], "color": "rgba(255,255,0,0.13)"},
                {"range": [101, 150], "color": "rgba(255,126,0,0.13)"},
                {"range": [151, 200], "color": "rgba(255,0,0,0.13)"},
                {"range": [201, 300], "color": "rgba(143,63,151,0.13)"},
                {"range": [301, 500], "color": "rgba(126,0,35,0.13)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "value": aqi_value,
            },
        },
        title={
            "text": f"AQI<br><span style='color:{color}'>{label}</span>",
        },
    ))

    fig.update_layout(
        paper_bgcolor="#0f0f23",
        font={"color": "#ffffff"},
        height=320,
    )

    st.plotly_chart(fig, width="stretch")


# ─────────────────────────────────────────────
# MINI GAUGE
# ─────────────────────────────────────────────
def render_mini_gauge(key: str, value: float):

    sensor = SENSORS[key]
    color = CHART_COLORS.get(key, "#74c0fc")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": f" {sensor['unit']}"},
        gauge={
            "axis": {"range": [sensor["min"], sensor["max"]]},
            "bar": {"color": color},
            "steps": [
                {"range": [sensor["min"], sensor["warning"]],
                 "color": hex_to_rgba("#00e400", 0.07)},
                {"range": [sensor["warning"], sensor["danger"]],
                 "color": hex_to_rgba("#ff7e00", 0.07)},
                {"range": [sensor["danger"], sensor["max"]],
                 "color": hex_to_rgba("#ff0000", 0.07)},
            ],
        },
        title={"text": sensor["label"]},
    ))

    fig.update_layout(
        paper_bgcolor="#1a1a2e",
        height=200,
    )

    st.plotly_chart(fig, width="stretch")


# ─────────────────────────────────────────────
# LINE CHART (FIXED)
# ─────────────────────────────────────────────
def render_line_chart(history_df, keys, title="Trends"):

    fig = go.Figure()

    for key in keys:
        if key not in history_df.columns:
            continue

        sensor = SENSORS.get(key, {})
        color = CHART_COLORS.get(key, "#74c0fc")
        label = sensor.get("label", key)
        unit = sensor.get("unit", "")

        fig.add_trace(go.Scatter(
            x=history_df["timestamp"],
            y=history_df[key],
            name=f"{label} ({unit})",
            mode="lines",
            line=dict(color=color, width=2.5),
            fill="tozeroy",
            fillcolor=hex_to_rgba(color, 0.1),  # ✅ FIXED
        ))

        # ✅ FIXED WARNING LINE
        warn = sensor.get("warning")
        if warn:
            fig.add_hline(
                y=warn,
                line_dash="dot",
                line_color=hex_to_rgba(color, 0.4),  # ✅ FIXED
                annotation_text=f"{label} warning",
                annotation_font_color=color,  # ✅ FIXED (no invalid hex)
            )

    fig.update_layout(
        title=title,
        paper_bgcolor="#0f0f23",
        font=dict(color="#aaaacc"),
        height=380,
    )

    st.plotly_chart(fig, width="stretch")


# ─────────────────────────────────────────────
# BAR
# ─────────────────────────────────────────────
def render_bar_snapshot(readings):

    labels, values, colors = [], [], []

    for key, value in readings.items():
        sensor = SENSORS.get(key, {})
        pct = (value - sensor.get("min", 0)) / (sensor.get("max", 100)) * 100

        labels.append(sensor.get("label", key))
        values.append(pct)
        colors.append(CHART_COLORS.get(key, "#74c0fc"))

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(color=colors),
    ))

    fig.update_layout(
        paper_bgcolor="#0f0f23",
        height=360,
    )

    st.plotly_chart(fig, width="stretch")


# ─────────────────────────────────────────────
# HEATMAP
# ─────────────────────────────────────────────
def render_heatmap(history_df):

    cols = [c for c in history_df.columns if c != "timestamp"]
    corr = history_df[cols].corr()

    fig = px.imshow(corr, text_auto=True)

    fig.update_layout(
        paper_bgcolor="#0f0f23",
        height=380,
    )

    st.plotly_chart(fig, width="stretch")