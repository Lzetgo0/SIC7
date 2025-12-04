import streamlit as st
import paho.mqtt.client as mqtt
import json
import pandas as pd
import joblib
from datetime import datetime

BROKER = "broker.hivemq.com"
TOPIC_SUB = "iot/sensor/data"
TOPIC_PUB = "iot/output"
MODEL_PATH = "iot_temp_model.pkl"

model = joblib.load(MODEL_PATH)

# Streamlit page config
st.set_page_config(page_title="IoT + ML Dashboard", page_icon="🤖", layout="wide")
st.title("🌡 IoT + Machine Learning Real-Time Dashboard")

# Dataframe for plotting
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["timestamp", "temperature", "humidity", "predicted"])

status_box = st.empty()
chart_box = st.empty()

def update_dashboard(temp, hum, pred):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.df.loc[len(st.session_state.df)] = [timestamp, temp, hum, pred]

    # Status box visual
    if pred == "Panas":
        status_box.markdown(f"### 🔥 **Status: PANAS** — Buzzer Aktif\nSuhu: **{temp}°C** | Kelembapan: **{hum}%**")
    elif pred == "Normal":
        status_box.markdown(f"### 🟢 **Status: NORMAL**\nSuhu: **{temp}°C** | Kelembapan: **{hum}%**")
    else:
        status_box.markdown(f"### 🔵 **Status: DINGIN**\nSuhu: **{temp}°C** | Kelembapan: **{hum}%**")

    chart_box.line_chart(st.session_state.df[["temperature", "humidity"]])


# MQTT callback
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        temp = float(data["temp"])
        hum = float(data["hum"])
    except:
        return

    pred = model.predict([[temp, hum]])[0]

    if pred == "Panas":
        client.publish(TOPIC_PUB, "BUZZER_ON")
    else:
        client.publish(TOPIC_PUB, "BUZZER_OFF")

    update_dashboard(temp, hum, pred)


client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC_SUB)
client.loop_start()

st.success("Dashboard connected to MQTT — waiting sensor data...")
st.info("Pastikan ESP32 berjalan untuk mulai menampilkan data")
