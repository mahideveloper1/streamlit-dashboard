# components/table.py — Historical data table with color-coded rows

import streamlit as st
import pandas as pd
from config import SENSORS, get_sensor_status, STATUS_COLORS, get_aqi_info

# ─────────────────────────────────────────────
#  MAIN TABLE RENDERER
# ─────────────────────────────────────────────
def render_table(history_df: pd.DataFrame):
    """
    Renders a styled historical data table.
    history_df must have 'timestamp' + one column per sensor key.
    """

    if history_df.empty:
        st.info("No historical data yet. Readings will appear here.")
        return

    st.markdown("### 📋 Historical Readings")

    # ── Controls row ──────────────────────────
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        search = st.text_input(
            "🔍 Filter by AQI status",
            placeholder="e.g. Good, Moderate, Unhealthy...",
            label_visibility="collapsed",
        )

    with col2:
        sensor_options = [k for k in history_df.columns if k != "timestamp"]
        sort_by = st.selectbox(
            "Sort by",
            options=["timestamp"] + sensor_options,
            index=0,
            label_visibility="collapsed",
        )

    with col3:
        sort_order = st.radio(
            "Order",
            options=["↓ Desc", "↑ Asc"],
            horizontal=True,
            label_visibility="collapsed",
        )

    # ── Build display dataframe ────────────────
    display_df = _build_display_df(history_df)

    # ── Apply search filter ────────────────────
    if search.strip():
        mask = display_df["AQI Status"].str.contains(search.strip(), case=False, na=False)
        display_df = display_df[mask]

    # ── Apply sort ─────────────────────────────
    sort_col = _map_sort_col(sort_by)
    ascending = sort_order == "↑ Asc"

    if sort_col in display_df.columns:
        display_df = display_df.sort_values(sort_col, ascending=ascending)

    # ── Summary pills ──────────────────────────
    _render_summary_pills(display_df)

    # ── Styled table ───────────────────────────
    styled = _style_table(display_df)
    st.dataframe(
        styled,
        width="stretch",
        height=420,
        hide_index=True,
    )

    # ── Download button ────────────────────────
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv,
        file_name="aqi_history.csv",
        mime="text/csv",
        use_container_width=False,
    )


# ─────────────────────────────────────────────
#  BUILD DISPLAY DATAFRAME
# ─────────────────────────────────────────────
def _build_display_df(history_df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts raw history dataframe into a human-readable
    display dataframe with units, labels, and AQI status column.
    """

    df = history_df.copy()

    # Format timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["timestamp"] = df["timestamp"].dt.strftime("%d %b %Y  %H:%M:%S")

    # Rename columns to labels with units
    rename_map = {"timestamp": "Timestamp"}
    for key in df.columns:
        if key == "timestamp":
            continue
        sensor = SENSORS.get(key, {})
        label  = sensor.get("label", key.upper())
        unit   = sensor.get("unit", "")
        rename_map[key] = f"{label} ({unit})" if unit else label

    # Add AQI status column before rename
    if "aqi" in df.columns:
        df["AQI Status"] = df["aqi"].apply(
            lambda v: get_aqi_info(v)["label"]
        )

    df.rename(columns=rename_map, inplace=True)

    # Round numeric columns
    num_cols = df.select_dtypes(include="number").columns
    df[num_cols] = df[num_cols].round(1)

    # Reorder: Timestamp first, AQI Status second
    cols = df.columns.tolist()
    ordered = ["Timestamp"]
    if "AQI Status" in cols:
        ordered.append("AQI Status")
    ordered += [c for c in cols if c not in ordered]
    df = df[ordered]

    return df


# ─────────────────────────────────────────────
#  STYLE TABLE
# ─────────────────────────────────────────────
from pandas.io.formats.style import Styler

def _style_table(df: pd.DataFrame) -> Styler:
    """Applies background color styling row by row based on AQI status."""

    # Color map for AQI status rows
    STATUS_BG = {
        "Good":             "#00e40012",
        "Moderate":         "#ffff0012",
        "Unhealthy for SG": "#ff7e0012",
        "Unhealthy":        "#ff000012",
        "Very Unhealthy":   "#8f3f9712",
        "Hazardous":        "#7e002312",
    }

    STATUS_TEXT = {
        "Good":             "#00e400",
        "Moderate":         "#cccc00",
        "Unhealthy for SG": "#ff7e00",
        "Unhealthy":        "#ff4444",
        "Very Unhealthy":   "#cc77ff",
        "Hazardous":        "#ff6666",
    }

    def row_style(row):
        status = row.get("AQI Status", "")
        bg     = STATUS_BG.get(status, "")
        styles = [f"background-color: {bg}" if bg else ""] * len(row)
        return styles

    def aqi_status_style(val):
        color = STATUS_TEXT.get(val, "#ccccee")
        return (
            f"color: {color}; font-weight: 700; "
            f"background: {color}18; border-radius: 6px; "
            f"padding: 2px 8px; text-align: center;"
        )

    styler = df.style.apply(row_style, axis=1)

    if "AQI Status" in df.columns:
        styler = styler.map(aqi_status_style, subset=["AQI Status"])

    styler = styler.set_properties(**{
        "color":       "#ccccee",
        "font-size":   "13px",
        "text-align":  "center",
        "white-space": "nowrap",
    })

    styler = styler.set_table_styles([
        {
            "selector": "th",
            "props": [
                ("background-color", "#16213e"),
                ("color",            "#aaaacc"),
                ("font-size",        "12px"),
                ("font-weight",      "700"),
                ("text-align",       "center"),
                ("border-bottom",    "1px solid #2a2a4a"),
                ("padding",          "10px 14px"),
                ("white-space",      "nowrap"),
            ],
        },
        {
            "selector": "td",
            "props": [
                ("border-bottom", "1px solid #1e1e3a"),
                ("padding",       "8px 14px"),
            ],
        },
        {
            "selector": "tr:hover td",
            "props": [
                ("background-color", "#ffffff08"),
            ],
        },
    ])

    return styler


# ─────────────────────────────────────────────
#  SUMMARY PILLS
# ─────────────────────────────────────────────
def _render_summary_pills(df: pd.DataFrame):
    """Shows count of readings per AQI status as colored pills."""

    if "AQI Status" not in df.columns:
        return

    counts = df["AQI Status"].value_counts().to_dict()

    STATUS_COLORS_MAP = {
        "Good":             "#00e400",
        "Moderate":         "#cccc00",
        "Unhealthy for SG": "#ff7e00",
        "Unhealthy":        "#ff4444",
        "Very Unhealthy":   "#cc77ff",
        "Hazardous":        "#ff6666",
    }

    pills_html = '<div style="display:flex; flex-wrap:wrap; gap:10px; margin: 12px 0 18px 0;">'

    total = sum(counts.values())
    pills_html += f"""
        <div style="
            background: #2a2a4a;
            color: #ccccee;
            border-radius: 20px;
            padding: 5px 14px;
            font-size: 0.8rem;
            font-weight: 600;
        ">Total: {total}</div>
    """

    for status, count in counts.items():
        color = STATUS_COLORS_MAP.get(status, "#8888aa")
        pills_html += f"""
            <div style="
                background: {color}22;
                color: {color};
                border: 1px solid {color}55;
                border-radius: 20px;
                padding: 5px 14px;
                font-size: 0.8rem;
                font-weight: 600;
            ">{status}: {count}</div>
        """

    pills_html += "</div>"
    st.markdown(pills_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────
def _map_sort_col(sort_by: str) -> str:
    """Maps raw sensor key to display column name for sorting."""
    if sort_by == "timestamp":
        return "Timestamp"
    sensor = SENSORS.get(sort_by, {})
    label  = sensor.get("label", sort_by.upper())
    unit   = sensor.get("unit", "")
    return f"{label} ({unit})" if unit else label