# config.py — Central configuration for AQI Dashboard

# ─────────────────────────────────────────────
#  APP SETTINGS
# ─────────────────────────────────────────────
APP_TITLE = "AQI Monitor Dashboard"
REFRESH_INTERVAL_MS = 3600000         # Auto-refresh every 1 hour
HISTORY_POINTS = 60                 # Number of data points to keep in history

# ─────────────────────────────────────────────
#  AQI BREAKPOINTS & LABELS
#  Based on US EPA standard
# ─────────────────────────────────────────────
AQI_LEVELS = [
    {"min": 0,   "max": 50,  "label": "Good",              "color": "#00e400"},
    {"min": 51,  "max": 100, "label": "Moderate",          "color": "#ffff00"},
    {"min": 101, "max": 150, "label": "Unhealthy for SG",  "color": "#ff7e00"},
    {"min": 151, "max": 200, "label": "Unhealthy",         "color": "#ff0000"},
    {"min": 201, "max": 300, "label": "Very Unhealthy",    "color": "#8f3f97"},
    {"min": 301, "max": 500, "label": "Hazardous",         "color": "#7e0023"},
]

def get_aqi_info(aqi_value: float) -> dict:
    """Return label and color for a given AQI value."""
    for level in AQI_LEVELS:
        if level["min"] <= aqi_value <= level["max"]:
            return level
    return {"label": "Hazardous", "color": "#7e0023"}


# ─────────────────────────────────────────────
#  SENSOR THRESHOLDS
#  Each sensor has: unit, min, max, warning, danger
# ─────────────────────────────────────────────
SENSORS = {
    "aqi": {
        "label": "AQI",
        "unit": "",
        "min": 0,
        "max": 500,
        "warning": 100,
        "danger": 200,
        "icon": "🌫️",
    },
    "temperature": {
        "label": "Temperature",
        "unit": "°C",
        "min": 10,
        "max": 50,
        "warning": 35,
        "danger": 42,
        "icon": "🌡️",
    },
    "humidity": {
        "label": "Humidity",
        "unit": "%",
        "min": 0,
        "max": 100,
        "warning": 70,
        "danger": 85,
        "icon": "💧",
    },
    "co2": {
        "label": "CO₂",
        "unit": "ppm",
        "min": 300,
        "max": 5000,
        "warning": 1000,
        "danger": 2000,
        "icon": "☁️",
    },
    "oxygen": {
        "label": "Oxygen (O₂)",
        "unit": "%",
        "min": 0,
        "max": 25,
        "warning": 19.5,   # Below this is oxygen deficient
        "danger": 16.0,
        "icon": "🫁",
    },
    "pm25": {
        "label": "PM2.5",
        "unit": "µg/m³",
        "min": 0,
        "max": 500,
        "warning": 35,
        "danger": 150,
        "icon": "🔬",
    },
    "pm10": {
        "label": "PM10",
        "unit": "µg/m³",
        "min": 0,
        "max": 600,
        "warning": 150,
        "danger": 350,
        "icon": "💨",
    },
    "voc": {
        "label": "VOC",
        "unit": "ppb",
        "min": 0,
        "max": 1000,
        "warning": 220,
        "danger": 660,
        "icon": "⚗️",
    },
    "noise": {
        "label": "Noise Level",
        "unit": "dB",
        "min": 20,
        "max": 120,
        "warning": 70,
        "danger": 90,
        "icon": "🔊",
    },
}

# ─────────────────────────────────────────────
#  CHART COLORS
# ─────────────────────────────────────────────
CHART_COLORS = {
    "aqi":         "#ff6b6b",
    "temperature": "#ffa94d",
    "humidity":    "#4dabf7",
    "co2":         "#a9e34b",
    "oxygen":      "#63e6be",
    "pm25":        "#da77f2",
    "pm10":        "#f783ac",
    "voc":         "#74c0fc",
    "noise":       "#ffe066",
}

# ─────────────────────────────────────────────
#  STATUS HELPERS
# ─────────────────────────────────────────────
def get_sensor_status(key: str, value: float) -> str:
    """Return 'normal', 'warning', or 'danger' for a sensor reading."""
    sensor = SENSORS.get(key, {})
    
    # Special case: oxygen is dangerous when LOW
    if key == "oxygen":
        if value <= sensor.get("danger", 0):
            return "danger"
        elif value <= sensor.get("warning", 0):
            return "warning"
        return "normal"
    
    # All other sensors: dangerous when HIGH
    if value >= sensor.get("danger", float("inf")):
        return "danger"
    elif value >= sensor.get("warning", float("inf")):
        return "warning"
    return "normal"


STATUS_COLORS = {
    "normal":  "#00e400",
    "warning": "#ff7e00",
    "danger":  "#ff0000",
}