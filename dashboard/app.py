"""
IoT Air Quality & Pollution Monitoring Dashboard
Streamlit Web Dashboard
-------------------------------------------------
Reads sensor logs from data/air_quality_log.csv and
displays real-time charts, current status, and alerts.

Run with: streamlit run dashboard/streamlit_app.py
"""

import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# ---------- CONFIG ----------
LOG_FILE = "data/air_quality_log.csv"
REFRESH_INTERVAL = 5  # seconds

AQI_GOOD_MAX = 1000
AQI_MODERATE_MAX = 2000
AQI_POOR_MAX = 3000

STATUS_COLORS = {
    "Good": "🟢",
    "Moderate": "🟡",
    "Poor": "🟠",
    "Hazardous": "🔴",
}

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Air Quality Monitoring Dashboard",
    page_icon="🌫️",
    layout="wide",
)

st.title("🌫️ IoT Air Quality & Pollution Monitoring Dashboard")
st.caption("Real-time air quality, temperature, and humidity monitoring")


def load_data():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame()
    df = pd.read_csv(LOG_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def display_dashboard():
    df = load_data()

    if df.empty:
        st.warning("No data found. Run the simulation first: `python main.py`")
        return

    latest = df.iloc[-1]

    # ---------- TOP METRICS ----------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Air Quality (MQ135)", f"{int(latest['mq135_value'])}")
    with col2:
        st.metric("Temperature", f"{latest['temperature_C']} °C")
    with col3:
        st.metric("Humidity", f"{latest['humidity_%']} %")
    with col4:
        status_icon = STATUS_COLORS.get(latest["status"], "⚪")
        st.metric("Status", f"{status_icon} {latest['status']}")

    # ---------- ALERT BANNER ----------
    if latest["status"] == "Hazardous":
        st.error(f"🚨 {latest['alert']}")
    elif latest["status"] == "Poor":
        st.warning(f"⚠️ {latest['alert']}")
    elif latest["status"] == "Moderate":
        st.info(f"ℹ️ {latest['alert']}")
    else:
        st.success(f"✅ {latest['alert']}")

    st.caption(f"Last updated: {latest['timestamp']}")

    st.divider()

    # ---------- CHARTS ----------
    st.subheader("📈 Air Quality Trend (MQ135)")
    chart_df = df.set_index("timestamp")[["mq135_value"]]
    st.line_chart(chart_df)

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🌡️ Temperature Trend")
        st.line_chart(df.set_index("timestamp")[["temperature_C"]])

    with col_b:
        st.subheader("💧 Humidity Trend")
        st.line_chart(df.set_index("timestamp")[["humidity_%"]])

    st.divider()

    # ---------- STATUS DISTRIBUTION ----------
    st.subheader("📊 Pollution Status Distribution")
    status_counts = df["status"].value_counts()
    st.bar_chart(status_counts)

    st.divider()

    # ---------- RAW DATA TABLE ----------
    with st.expander("📋 View Raw Sensor Log"):
        st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)

    # ---------- DOWNLOAD ----------
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Full Log (CSV)",
        data=csv_data,
        file_name="air_quality_log.csv",
        mime="text/csv",
    )


# ---------- SIDEBAR ----------
st.sidebar.header("⚙️ Dashboard Controls")
auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=False)
refresh_rate = st.sidebar.slider("Refresh interval (seconds)", 2, 30, REFRESH_INTERVAL)

st.sidebar.markdown("---")
st.sidebar.markdown("### Threshold Reference")
st.sidebar.markdown(f"""
- 🟢 **Good**: 0 – {AQI_GOOD_MAX}
- 🟡 **Moderate**: {AQI_GOOD_MAX+1} – {AQI_MODERATE_MAX}
- 🟠 **Poor**: {AQI_MODERATE_MAX+1} – {AQI_POOR_MAX}
- 🔴 **Hazardous**: > {AQI_POOR_MAX}
""")

st.sidebar.markdown("---")
st.sidebar.markdown("**Project**: IoT Air Quality Monitoring")
st.sidebar.markdown("**Author**: Rakshitha A S")

# ---------- MAIN ----------
display_dashboard()

if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()