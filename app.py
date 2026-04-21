import streamlit as st
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os

from utils import detect_faces_yolo as detect_faces
from tracker import track_faces
from face_recognition import recognize_face, create_embeddings
from database import create_table, mark_attendance, get_attendance
#from alerts import send_email

st.set_page_config(page_title="Smart Attendance", layout="wide")

st.title("🎯 Smart Attendance System (AI Powered)")

create_table()

menu = ["Register Face", "Mark Attendance", "View Attendance"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- REGISTER ----------------
if choice == "Register Face":
    st.subheader("📸 Register New User")

    name = st.text_input("Enter Name")

    img_file = st.camera_input("Capture Face")

    if img_file and name:
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)

        faces = detect_faces(img)

        for (x, y, w, h) in faces:
            face = img[y:y+h, x:x+w]

            path = f"dataset/{name}"
            os.makedirs(path, exist_ok=True)

            count = len(os.listdir(path))
            cv2.imwrite(f"{path}/{count}.jpg", face)

        st.success("Face saved successfully!")

    if st.button("Generate Embeddings"):
        create_embeddings()
        st.success("Embeddings created successfully!")

# ---------------- ATTENDANCE ----------------
elif choice == "Mark Attendance":
    st.subheader("📷 Smart Attendance (YOLO + DeepSORT)")

    img_file = st.camera_input("Capture")

    if img_file:
        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)

        # YOLO detection
        faces = detect_faces(frame)

        # DeepSORT tracking
        tracked_faces = track_faces(faces, frame)

        for (x, y, w, h, track_id) in tracked_faces:
            face = frame[y:y+h, x:x+w]

            name = recognize_face(face)

            label = f"{name} | ID:{track_id}"

            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(frame, label, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

            # Mark attendance + send alert
            if name not in ["Unknown", "No Data"]:
                mark_attendance(name)
                try:
                    send_email(name)
                except:
                    pass  # avoid crash if email fails

        st.image(frame, channels="BGR")

# ---------------- PREMIUM DASHBOARD ----------------
elif choice == "View Attendance":
    st.subheader("📊 Premium Attendance Dashboard")

    data = get_attendance()

    if len(data) == 0:
        st.warning("No attendance data yet.")
    else:
        df = pd.DataFrame(data, columns=["ID", "Name", "Date", "Time"])
        df["Date"] = pd.to_datetime(df["Date"])

        # -------- METRICS --------
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Records", len(df))
        col2.metric("Unique Users", df["Name"].nunique())
        col3.metric("Active Days", df["Date"].nunique())

        st.divider()

        # -------- TABLE --------
        st.dataframe(df, use_container_width=True)

        # -------- DAILY TREND --------
        st.subheader("📈 Daily Attendance Trend")

        daily = df.groupby("Date").size().reset_index(name="Count")
        fig1 = px.line(daily, x="Date", y="Count", markers=True,
                       title="Daily Attendance")
        st.plotly_chart(fig1, use_container_width=True)

        # -------- PERSON WISE --------
        st.subheader("👤 Person-wise Attendance")

        person = df["Name"].value_counts().reset_index()
        person.columns = ["Name", "Count"]

        fig2 = px.bar(person, x="Name", y="Count", text="Count",
                      title="Attendance by Person")
        st.plotly_chart(fig2, use_container_width=True)

        # -------- HEATMAP --------
        st.subheader("🟩 GitHub Style Heatmap")

        df["Week"] = df["Date"].dt.isocalendar().week
        df["Day"] = df["Date"].dt.weekday

        pivot = df.pivot_table(
            index="Week",
            columns="Day",
            values="Name",
            aggfunc="count",
            fill_value=0
        )

        fig3, ax = plt.subplots(figsize=(12, 4))
        sns.heatmap(pivot, cmap="Greens", linewidths=0.5, ax=ax)

        ax.set_xlabel("Day of Week")
        ax.set_ylabel("Week Number")

        st.pyplot(fig3)

        # -------- DOWNLOAD --------
        st.subheader("⬇️ Download Report")

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="attendance.csv",
            mime="text/csv"
        )