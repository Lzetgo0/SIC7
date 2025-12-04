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

# ==== STREAMLIT CONFIG ====
st.set_page_config(page_title="IoT + ML Dashboard", page_icon="🤖", layout="wide")

# ==== GLOBAL PREMIUM CSS ====
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
            color: #fff;
        }
        .glass-card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0px 0px 15px rgba(0,0,0,0.4);
            margin-bottom: 20px;
        }
        .title-text {
            font-size: 40px;
            text-align: center;
            font-weight: 700;
            color: #00e6a8;
            margin-bottom: -10px;
        }
        .subtitle-text {
            text-align: center;
            font-size: 18px;
            opacity: 0.7;
        }
    </style>
""", unsafe_allow_html=True)

# ==== TITLE ====
st.markdown('<p class="title-text">🌡 IoT Machine Learning Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Real-Time Monitoring with MQTT + AI</p>', unsafe_allow_html=True)


# ==== DATAFRAME ====
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["timestamp", "temperature", "humidity", "predicted"])

status_box = st.empty()

col1, col2 = st.columns(2)
chart_temp = col1.empty()
chart_hum = col2.empty()


# ==== UPDATE UI (DESIGN ONLY) ====
def update_dashboard(temp, hum, pred):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.df.loc[len(st.session_state.df)] = [timestamp, temp, hum, pred]

    # Color theme
    color_map = {
        "Panas": "#ff4d4d",
        "Normal": "#00e6a8",
        "Dingin": "#4da6ff"
    }
    icon_map = {
        "Panas": "🔥",
        "Normal": "🟢",
        "Dingin": "❄️"
    }

    color = color_map.get(pred, "#999")
    icon = icon_map.get(pred, "ℹ️")

    # Premium glass card
    status_box.markdown(
        f"""
        <div class="glass-card" style="border-left: 6px solid {color};">
            <h2 style="margin:0; color:{color};">{icon} Status: {pred}</h2>
            <p style="font-size:18px; margin:0;">
                Suhu: <b>{temp}°C</b><br>
                Kelembapan: <b>{hum}%</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Premium charts
    chart_temp.markdown('<div class="glass-card"><h3>📈 Grafik Suhu (°C)</h3></div>', unsafe_allow_html=True)
    chart_temp.line_chart(st.session_state.df[["temperature"]])

    chart_hum.markdown('<div class="glass-card"><h3>💧 Grafik Kelembapan (%)</h3></div>', unsafe_allow_html=True)
    chart_hum.line_chart(st.session_state.df[["humidity"]])


# ==== MQTT CALLBACK (TIDAK DIUBAH) ====
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


# ==== MQTT CLIENT ====
client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC_SUB)
client.loop_start()

# ==== INFO ====
st.markdown('<div class="glass-card">📡 Menunggu data dari ESP32...</div>', unsafe_allow_html=True)
