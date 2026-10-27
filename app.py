
from pathlib import Path
from datetime import datetime
import time
from PIL import Image
import cv2
import pandas as pd
import requests
import streamlit as st
import plotly.express as px
from ultralytics import YOLO

import database


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="UrbanGuard AI",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROOT_DIR = Path(__file__).resolve().parent

MODEL_PATHS = [
    ROOT_DIR / "runs" / "detect" / "runs" / "detect"
    / "vehicle_fast" / "weights" / "best.pt",

    ROOT_DIR / "runs" / "detect" / "models" / "vehicle_detection"
    / "yolo11_vehicle" / "weights" / "best.pt",

    ROOT_DIR / "runs" / "detect" / "models" / "vehicle_detection"
    / "yolo11_vehicle-2" / "weights" / "best.pt",
]
ACCIDENT_MODEL_PATH = (
    ROOT_DIR / "runs" / "detect" / "accident_fast"
    / "weights" / "best.pt"
)

# =========================================================
# STYLING
# =========================================================

st.markdown("""
<style>
    .stApp {
        background-color: #0b1220;
        color: #e5e7eb;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
    }

    [data-testid="stMetric"] {
        background-color: #172033;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #273449;
    }

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    h1, h2, h3 {
        color: #e5f0ff;
    }

    .small-note {
        color: #9ca3af;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "traffic_alert_last_time" not in st.session_state:
    st.session_state.traffic_alert_last_time = 0.0

if "pollution_alert_last_time" not in st.session_state:
    st.session_state.pollution_alert_last_time = 0.0

if "last_vehicle_count" not in st.session_state:
    st.session_state.last_vehicle_count = 0

if "last_pollution" not in st.session_state:
    st.session_state.last_pollution = None

if "camera_running" not in st.session_state:
    st.session_state.camera_running = False


# =========================================================
# MODEL LOADING
# =========================================================

@st.cache_resource
def load_model(model_path):
    return YOLO(str(model_path))


def find_model_path():
    for path in MODEL_PATHS:
        if path.is_file():
            return path
    return None


MODEL_PATH = find_model_path()


# =========================================================
# ALERT MANAGEMENT
# =========================================================

def add_alert(alert_type, message, severity="Medium"):
    """Save an alert to SQLite and show it in the current session."""

    try:
        database.save_alert(
            alert_type=alert_type,
            severity=severity,
            message=message
        )
    except Exception as exc:
        st.error(f"Could not save alert to database: {exc}")


def create_traffic_alert(vehicle_count, threshold):
    """Avoid saving the same traffic alert on every video frame."""

    now = time.time()

    if vehicle_count >= threshold:
        if now - st.session_state.traffic_alert_last_time >= 60:
            add_alert(
                "High Traffic",
                f"{vehicle_count} vehicles detected in the current frame.",
                "High"
            )
            st.session_state.traffic_alert_last_time = now


def create_pollution_alert(aqi):
    """Generate an alert when the reported AQI crosses a threshold."""

    now = time.time()

    if aqi >= 151:
        severity = "High"
        message = f"Reported US AQI is {aqi}. Air quality is unhealthy."
    elif aqi >= 101:
        severity = "Medium"
        message = f"Reported US AQI is {aqi}. Air quality may affect sensitive groups."
    else:
        return

    if now - st.session_state.pollution_alert_last_time >= 300:
        add_alert("Air Pollution", message, severity)
        st.session_state.pollution_alert_last_time = now


# =========================================================
# VEHICLE DETECTION HELPERS
# =========================================================

def count_detections(result):
    counts = {}

    if result.boxes is None or result.boxes.cls is None:
        return counts

    for class_id in result.boxes.cls.tolist():
        class_id = int(class_id)

        if isinstance(result.names, dict):
            name = result.names.get(class_id, str(class_id))
        else:
            name = result.names[class_id]

        counts[name] = counts.get(name, 0) + 1

    return counts


def detection_summary(counts):
    if not counts:
        return "No vehicles detected."

    return ", ".join(
        f"{name}: {count}"
        for name, count in sorted(counts.items())
    )


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

st.sidebar.title("🏙️ UrbanGuard AI")
st.sidebar.caption("Smart City Monitoring Platform")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
    "Live Dashboard",
    "Live Vehicle Detection",
    "Accident Detection",
    "Pollution Monitoring",
    "Alerts",
    "Analytics",
    "About"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("**System Status**")

if MODEL_PATH:
    st.sidebar.success("Vehicle model available")
else:
    st.sidebar.error("Vehicle model not found")

st.sidebar.caption(
    "Monitoring operates only when the app and relevant feature are running."
)


# =========================================================
# LIVE DASHBOARD
# =========================================================

if page == "Live Dashboard":

    st.title("🏙️ UrbanGuard AI Dashboard")
    st.write(
        "Monitor detected vehicles, air quality reports, and system alerts."
    )

    alerts = database.get_alerts(limit=500)
    traffic = database.get_traffic_history(limit=1000)

    alert_df = pd.DataFrame(alerts)
    traffic_df = pd.DataFrame(traffic)

    total_alerts = len(alert_df)

    if not alert_df.empty:
        high_alerts = int(
            (alert_df["Severity"] == "High").sum()
        )
    else:
        high_alerts = 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Last Vehicle Count",
        st.session_state.last_vehicle_count
    )

    col2.metric(
        "Stored Traffic Records",
        len(traffic_df)
    )

    col3.metric(
        "Total Stored Alerts",
        total_alerts
    )

    col4.metric(
        "High-Severity Alerts",
        high_alerts
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Recent Alerts")

        if alert_df.empty:
            st.info("No alerts have been recorded yet.")
        else:
            st.dataframe(
                alert_df.head(8),
                use_container_width=True,
                hide_index=True
            )

    with right:
        st.subheader("Recent Traffic Activity")

        if traffic_df.empty:
            st.info(
                "No traffic records yet. Open Live Vehicle Detection "
                "and start the camera."
            )
        else:
            recent = traffic_df.tail(30)

            fig = px.line(
                recent,
                x="Time",
                y="Vehicle Count",
                title="Vehicle Detections Over Time",
                markers=True
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0b1220",
                plot_bgcolor="#0b1220"
            )

            st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "The vehicle count represents detections in an individual frame, "
        "not a verified measure of road congestion."
    )


# =========================================================
# LIVE VEHICLE DETECTION
# =========================================================

elif page == "Live Vehicle Detection":

    st.title("🚗 Live Vehicle Detection")

    st.write(
        "Run your trained YOLO model against a camera feed."
    )

    if MODEL_PATH is None:
        st.error(
            "No model file was found. Make sure best.pt exists in one "
            "of the configured model paths."
        )

        st.code(
            "runs/detect/runs/detect/vehicle_fast/weights/best.pt",
            language="text"
        )

        st.stop()

    st.success(f"Model path: {MODEL_PATH.relative_to(ROOT_DIR)}")

    col1, col2, col3 = st.columns(3)

    with col1:
        camera_index = st.number_input(
            "Camera index",
            min_value=0,
            max_value=10,
            value=0,
            step=1
        )

    with col2:
        duration = st.slider(
            "Monitoring duration (seconds)",
            min_value=10,
            max_value=120,
            value=30,
            step=10
        )

    with col3:
        confidence = st.slider(
            "Detection confidence",
            min_value=0.10,
            max_value=0.95,
            value=0.40,
            step=0.05
        )

    traffic_threshold = st.number_input(
        "Vehicle alert threshold",
        min_value=1,
        max_value=100,
        value=10,
        help=(
            "Create an alert when this many vehicles are detected "
            "in one processed frame."
        )
    )

    st.warning(
        "Camera access requires a connected and permitted camera. "
        "On some Windows systems, another application may be using it."
    )

    start_camera = st.button(
        "▶ Start Live Detection",
        type="primary",
        use_container_width=True
    )

    if start_camera:

        try:
            model = load_model(str(MODEL_PATH))
        except Exception as exc:
            st.error(f"Could not load the YOLO model: {exc}")
            st.stop()

        camera = cv2.VideoCapture(int(camera_index))

        if not camera.isOpened():
            camera.release()
            st.error(
                "Could not open the camera. Check the camera index, "
                "permissions, and whether another app is using it."
            )
            st.stop()

        st.session_state.camera_running = True

        frame_placeholder = st.empty()
        status_placeholder = st.empty()
        counts_placeholder = st.empty()

        start_time = time.time()
        last_saved_time = 0.0
        frame_number = 0
        processed_count = 0

        try:
            while time.time() - start_time < duration:

                success, frame = camera.read()

                if not success:
                    status_placeholder.warning(
                        "Unable to read a camera frame. Stopping detection."
                    )
                    break

                frame_number += 1

                # Process every second frame to reduce CPU load.
                if frame_number % 2 == 0:
                    results = model.predict(
                        source=frame,
                        conf=confidence,
                        verbose=False
                    )

                    result = results[0]
                    counts = count_detections(result)
                    vehicle_count = sum(counts.values())

                    st.session_state.last_vehicle_count = vehicle_count

                    annotated_frame = result.plot()

                    counts_placeholder.write(
                        f"**Current detections:** "
                        f"{detection_summary(counts)}"
                    )

                    # Save traffic history at most once every 5 seconds.
                    now = time.time()

                    if now - last_saved_time >= 5:
                        database.save_traffic_count(vehicle_count)
                        last_saved_time = now
                        processed_count += 1

                    create_traffic_alert(
                        vehicle_count,
                        int(traffic_threshold)
                    )

                else:
                    annotated_frame = frame

                annotated_rgb = cv2.cvtColor(
                    annotated_frame,
                    cv2.COLOR_BGR2RGB
                )

                frame_placeholder.image(
                    annotated_rgb,
                    caption="Live camera feed",
                    use_container_width=True
                )

                elapsed = int(time.time() - start_time)
                remaining = max(0, duration - elapsed)

                status_placeholder.info(
                    f"Monitoring active — {remaining} seconds remaining."
                )

                time.sleep(0.02)

        except Exception as exc:
            st.error(f"Detection error: {exc}")

        finally:
            camera.release()
            st.session_state.camera_running = False

        status_placeholder.success(
            f"Monitoring finished. Saved {processed_count} traffic records."
        )

    st.divider()
    st.subheader("Latest Detection Status")

    st.metric(
        "Last detected vehicle count",
        st.session_state.last_vehicle_count
    )

    st.caption(
        "This feature detects vehicles only. It does not identify accidents "
        "or fires, and a single-frame vehicle count is not sufficient to "
        "confirm a traffic jam."
    )
elif page == "Accident Detection":

    st.title("🚨 Accident Detection")
    st.write(
        "Upload a road image to detect possible accident-related "
        "objects using your trained YOLO model."
    )

    # Path to the trained accident model
    ACCIDENT_MODEL_PATH = (
        ROOT_DIR / "runs" / "detect" / "accident_fast"
        / "weights" / "best.pt"
    )

    # Check whether the model exists
    if not ACCIDENT_MODEL_PATH.is_file():
        st.error("Accident model not found.")
        st.code(str(ACCIDENT_MODEL_PATH))
        st.info(
            "Check that best.pt exists inside "
            "runs/detect/accident_fast/weights/"
        )

    else:
        st.success("Accident model loaded from the expected path.")

        st.warning(
            "This is a prototype. Predictions can be incorrect. "
            "Always verify results manually; do not rely on this "
            "model for emergency decisions."
        )

        confidence = st.slider(
            "Detection confidence",
            min_value=0.10,
            max_value=0.95,
            value=0.35,
            step=0.05,
            key="accident_confidence"
        )

        uploaded_image = st.file_uploader(
            "Upload a road or accident image",
            type=["jpg", "jpeg", "png"],
            key="accident_image"
        )

        if uploaded_image is not None:
            image = Image.open(uploaded_image).convert("RGB")

            st.image(
                image,
                caption="Uploaded image",
                use_container_width=True
            )

            if st.button(
                "Run Accident Detection",
                type="primary",
                key="run_accident_detection"
            ):
                try:
                    with st.spinner("Analyzing image..."):
                        accident_model = load_model(
                            str(ACCIDENT_MODEL_PATH)
                        )

                        result = accident_model.predict(
                            source=image,
                            conf=confidence,
                            verbose=False
                        )[0]

                    # Display image with bounding boxes
                    annotated_image = result.plot()
                    annotated_image = cv2.cvtColor(
                        annotated_image,
                        cv2.COLOR_BGR2RGB
                    )

                    st.subheader("Detection Results")

                    st.image(
                        annotated_image,
                        caption="YOLO prediction",
                        use_container_width=True
                    )

                    # Extract detected objects
                    names = result.names
                    detections = []

                    accident_classes = {
                        "accident",
                        "car-accident",
                        "car-crash",
                        "moderate-accident",
                        "severe-accident",
                        "object-accident",
                        "colision",
                        "volcadura"
                    }

                    if result.boxes is not None:
                        for box in result.boxes:
                            class_id = int(box.cls.item())

                            if isinstance(names, dict):
                                class_name = names.get(
                                    class_id,
                                    str(class_id)
                                )
                            else:
                                class_name = names[class_id]

                            score = float(box.conf.item())

                            detections.append({
                                "Class": class_name,
                                "Confidence": round(score, 3)
                            })

                    if detections:
                        st.dataframe(
                            pd.DataFrame(detections),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info(
                            "No objects detected at this confidence "
                            "level. This does not prove that the image "
                            "is accident-free."
                        )

                    # Identify accident-related detections
                    accident_detections = [
                        item for item in detections
                        if item["Class"].strip().lower()
                        in accident_classes
                    ]

                    if accident_detections:
                        st.error(
                            "Possible accident-related objects detected. "
                            "Please verify the result manually."
                        )

                        summary = ", ".join(
                            f'{item["Class"]} '
                            f'({item["Confidence"]:.0%})'
                            for item in accident_detections
                        )

                        severity = (
                            "High"
                            if any(
                                item["Class"].strip().lower()
                                == "severe-accident"
                                for item in accident_detections
                            )
                            else "Medium"
                        )

                        # Save the alert immediately when detection runs.
                        # This avoids losing the results on a button rerun.
                        if st.session_state.get(
                            "last_accident_alert_image"
                        ) != uploaded_image.name + summary:
                            add_alert(
                                "Accident Detection",
                                f"Image prediction: {summary}",
                                severity
                            )

                            st.session_state[
                                "last_accident_alert_image"
                            ] = uploaded_image.name + summary

                            st.success(
                                "Accident alert saved to the database."
                            )
                        else:
                            st.info(
                                "This result has already been saved "
                                "as an alert in this session."
                            )

                    else:
                        st.info(
                            "No configured accident-related classes "
                            "were detected. The model may still miss "
                            "an accident."
                        )

                except Exception as exc:
                    st.error(
                        f"Accident detection failed: {exc}"
                    )


# =========================================================
# POLLUTION MONITORING
# =========================================================

elif page == "Pollution Monitoring":

    st.title("🌫️ Pollution Monitoring")

    st.write(
        "Retrieve current air-quality readings from the Open-Meteo "
        "Air Quality API for the selected coordinates."
    )

    with st.form("pollution_form"):

        col1, col2 = st.columns(2)

        with col1:
            latitude = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                value=17.3850,
                format="%.4f"
            )

        with col2:
            longitude = st.number_input(
                "Longitude",
                min_value=-180.0,
                max_value=180.0,
                value=78.4867,
                format="%.4f"
            )

        check_pollution = st.form_submit_button(
            "Check Current Air Quality",
            type="primary"
        )

    if check_pollution:

        endpoint = "https://air-quality-api.open-meteo.com/v1/air-quality"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "us_aqi,pm2_5,pm10",
            "timezone": "auto"
        }

        try:
            with st.spinner("Retrieving air-quality readings..."):

                response = requests.get(
                    endpoint,
                    params=params,
                    timeout=20
                )

                response.raise_for_status()
                payload = response.json()

            current = payload.get("current", {})

            aqi = current.get("us_aqi")
            pm25 = current.get("pm2_5")
            pm10 = current.get("pm10")

            if aqi is None and pm25 is None and pm10 is None:
                st.error(
                    "The API returned no current air-quality readings "
                    "for these coordinates."
                )
            else:
                st.session_state.last_pollution = {
                    "AQI (US)": aqi,
                    "PM2.5": pm25,
                    "PM10": pm10,
                    "Location": f"{latitude}, {longitude}",
                    "Retrieved At": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                }

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "US AQI",
                    round(aqi, 1) if aqi is not None else "N/A"
                )

                col2.metric(
                    "PM2.5",
                    f"{pm25} µg/m³" if pm25 is not None else "N/A"
                )

                col3.metric(
                    "PM10",
                    f"{pm10} µg/m³" if pm10 is not None else "N/A"
                )

                if aqi is not None:
                    create_pollution_alert(float(aqi))

                    if aqi <= 50:
                        st.success("AQI category: Good")
                    elif aqi <= 100:
                        st.info("AQI category: Moderate")
                    elif aqi <= 150:
                        st.warning(
                            "AQI category: Unhealthy for sensitive groups"
                        )
                    elif aqi <= 200:
                        st.error("AQI category: Unhealthy")
                    elif aqi <= 300:
                        st.error("AQI category: Very Unhealthy")
                    else:
                        st.error("AQI category: Hazardous")

                st.caption(
                    "These readings are API-provided estimates, not "
                    "measurements from a local physical pollution sensor."
                )

        except requests.RequestException as exc:
            st.error(f"Could not retrieve air-quality data: {exc}")

        except (ValueError, TypeError) as exc:
            st.error(f"Could not interpret the air-quality response: {exc}")

    if st.session_state.last_pollution:
        st.divider()
        st.subheader("Last Retrieved Reading")
        st.json(st.session_state.last_pollution)


# =========================================================
# ALERTS
# =========================================================

elif page == "Alerts":

    st.title("🚨 Alert Management")

    st.write(
        "View alert records saved in the local SQLite database."
    )

    alerts = database.get_alerts(limit=5000)
    alerts_df = pd.DataFrame(alerts)

    if alerts_df.empty:
        st.info(
            "No alerts are stored yet. Run vehicle detection or check "
            "air quality to generate alerts."
        )
    else:

        col1, col2 = st.columns(2)

        with col1:
            severity_options = ["All"] + sorted(
                alerts_df["Severity"].dropna().unique().tolist()
            )

            selected_severity = st.selectbox(
                "Filter by severity",
                severity_options
            )

        with col2:
            type_options = ["All"] + sorted(
                alerts_df["Alert Type"].dropna().unique().tolist()
            )

            selected_type = st.selectbox(
                "Filter by alert type",
                type_options
            )

        filtered_df = alerts_df.copy()

        if selected_severity != "All":
            filtered_df = filtered_df[
                filtered_df["Severity"] == selected_severity
            ]

        if selected_type != "All":
            filtered_df = filtered_df[
                filtered_df["Alert Type"] == selected_type
            ]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        csv_data = filtered_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download Alerts as CSV",
            data=csv_data,
            file_name="urbanguard_alerts.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("Database Maintenance")

    st.warning(
        "Deleting records permanently removes them from the local database."
    )

    confirm_delete = st.checkbox(
        "I understand that deleting alert history is permanent."
    )

    if st.button("🗑 Clear All Alerts", disabled=not confirm_delete):
        database.clear_alerts()
        st.success("Alert history cleared.")
        st.rerun()


# =========================================================
# ANALYTICS
# =========================================================

elif page == "Analytics":

    st.title("📊 Urban Analytics")

    traffic = database.get_traffic_history(limit=5000)
    alerts = database.get_alerts(limit=5000)

    traffic_df = pd.DataFrame(traffic)
    alerts_df = pd.DataFrame(alerts)

    st.subheader("Traffic History")

    if traffic_df.empty:
        st.info(
            "No traffic history available. Start live vehicle detection "
            "to record vehicle counts."
        )
    else:

        traffic_df["Time"] = pd.to_datetime(
            traffic_df["Time"],
            errors="coerce"
        )

        traffic_df = traffic_df.dropna(subset=["Time"])

        fig = px.line(
            traffic_df,
            x="Time",
            y="Vehicle Count",
            title="Vehicle Detections Recorded Over Time",
            markers=True
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b1220",
            plot_bgcolor="#0b1220"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.metric(
            "Average vehicles per sampled frame",
            round(traffic_df["Vehicle Count"].mean(), 2)
        )

        st.metric(
            "Maximum vehicles in a sampled frame",
            int(traffic_df["Vehicle Count"].max())
        )

        st.download_button(
            "⬇ Download Traffic History",
            data=traffic_df.to_csv(index=False).encode("utf-8"),
            file_name="urbanguard_traffic_history.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("Alert Analytics")

    if alerts_df.empty:
        st.info("No alert data available yet.")
    else:

        severity_counts = (
            alerts_df.groupby("Severity")
            .size()
            .reset_index(name="Alert Count")
        )

        fig_severity = px.bar(
            severity_counts,
            x="Severity",
            y="Alert Count",
            title="Alerts by Severity",
            color="Severity"
        )

        fig_severity.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b1220",
            plot_bgcolor="#0b1220"
        )

        st.plotly_chart(
            fig_severity,
            use_container_width=True
        )

        type_counts = (
            alerts_df.groupby("Alert Type")
            .size()
            .reset_index(name="Alert Count")
        )

        fig_types = px.pie(
            type_counts,
            names="Alert Type",
            values="Alert Count",
            title="Alerts by Type"
        )

        fig_types.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b1220"
        )

        st.plotly_chart(
            fig_types,
            use_container_width=True
        )


# =========================================================
# ABOUT
# =========================================================

elif page == "About":

    st.title("ℹ️ About UrbanGuard AI")

    st.markdown("""
    **UrbanGuard AI** is a prototype smart-city monitoring platform
    designed to bring together computer vision, air-quality information,
    alerts, and basic analytics.

    ### Current features

    - YOLO-based vehicle detection using a trained model.
    - Live camera monitoring while the detection page is running.
    - Traffic threshold alerts based on vehicles in a single frame.
    - Air-quality readings retrieved from the Open-Meteo API.
    - Pollution threshold alerts.
    - SQLite storage for alerts and traffic history.
    - Charts, alert filtering, and CSV exports.

    ### Current limitations

    - The current vehicle model does not detect accidents or fires.
    - A dedicated, trained model is required for accident or fire detection.
    - Traffic counts alone do not reliably establish congestion.
    - Air-quality readings are API-provided, not local sensor readings.
    - Camera monitoring stops when the detection run finishes.
    - SQLite stores data locally on this computer.
    - This version does not include user authentication or role-based access.
    - Alerts are created by the running application; it is not a 24/7
      background monitoring service.

    ### Technologies

    Python, Streamlit, OpenCV, Ultralytics YOLO, Plotly, Pandas,
    Requests, and SQLite.
    """)

    st.divider()

    st.write("**Database location:**")
    st.code(str(database.DB_PATH), language="text")

    if MODEL_PATH:
        st.write("**Loaded model candidate:**")
        st.code(str(MODEL_PATH), language="text")
    else:
        st.error("No trained YOLO model file was found.")
