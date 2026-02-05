import streamlit as st
import requests
import socketio
import cv2
import base64
import numpy as np
import time

API_URL = "http://localhost:8000"
SOCKET_URL = "http://127.0.0.1:8001"

st.set_page_config(layout="wide")
st.title("🦺 PPE Detection System")

mode = st.sidebar.radio("Select Mode", ["Image Upload", "Video Upload", "Realtime Camera"])

if mode == "Image Upload":
    uploaded_file = st.file_uploader("Upload Image", type=["jpg","jpeg","png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Original Image", use_column_width=True)
        with st.spinner("Detecting..."):
            r = requests.post(f"{API_URL}/detect/image", files={"file": uploaded_file})
            data = r.json()

        st.subheader("Detected Image")
        st.image(API_URL + "/download?path=" + data["output_path"], use_column_width=True)

        st.subheader("Objects Detected:")
        if data.get("summary"):
            for cls, count in data["summary"].items():
                st.write(f"- {count} {cls}")

elif mode == "Video Upload":
    uploaded_file = st.file_uploader("Upload Video", type=["mp4","avi","mov"])
    if uploaded_file:
        st.video(uploaded_file)
        with st.spinner("Processing video..."):
            r = requests.post(f"{API_URL}/detect/video", files={"file": uploaded_file})
            data = r.json()
        st.success("Detection complete")
        st.video(API_URL + "/download?path=" + data["output_path"])

elif mode == "Realtime Camera":
    start = st.button("▶ Start Realtime Detection")
    frame_placeholder = st.empty()
    latest_frame = None
    latest_counts = {}

    sio = socketio.Client()

    @sio.event
    def connect():
        st.success("Connected to realtime server")

    @sio.event
    def disconnect():
        st.warning("Disconnected from server")

    @sio.event
    def result(data):
        global latest_frame, latest_counts
        try:
            img_bytes = base64.b64decode(data["frame"])
            np_img = np.frombuffer(img_bytes, np.uint8)
            latest_frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
            latest_counts = data.get("counts", {})
        except Exception as e:
            st.error(f"Error decoding frame: {e}")

    if start:
        try:
            sio.connect(SOCKET_URL, transports=["polling"])
        except Exception as e:
            st.error(f"Socket.IO connection failed: {e}")
            st.stop()

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("❌ Camera not found or in use.")
            st.stop()

        while True:
            ret, frame = cap.read()
            if not ret:
                st.error("❌ Unable to read from camera.")
                break

            _, buffer = cv2.imencode(".jpg", frame)
            encoded_frame = base64.b64encode(buffer).decode("utf-8")
            sio.emit("frame", encoded_frame)

            if latest_frame is not None:
                frame_placeholder.image(cv2.cvtColor(latest_frame, cv2.COLOR_BGR2RGB), channels="RGB")
                if latest_counts:
                    st.subheader("Objects Detected:")
                    for cls, count in latest_counts.items():
                        st.write(f"- {count} {cls}")

            time.sleep(0.03)

        cap.release()
        sio.disconnect()
