import paho.mqtt.subscribe as subscribe
import sqlite3
import json
from datetime import datetime as dt

conn = sqlite3.connect('database/sensor_data.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS dht11_data
             (datetime TEXT, temperature REAL NOT NULL, humidity REAL NOT NULL)''')
c.execute('''CREATE TABLE IF NOT EXISTS mq2_data
             (datetime TEXT, MQ2 REAL NOT NULL)''')
c.execute('''CREATE TABLE IF NOT EXISTS mq7_data
             (datetime TEXT, MQ7 REAL NOT NULL)''')
c.execute('''CREATE TABLE IF NOT EXISTS mq135_data
             (datetime TEXT, MQ135 REAL NOT NULL)''')
c.execute('''CREATE TABLE IF NOT EXISTS bat_data
             (datetime TEXT, BAT REAL NOT NULL)''')
c.execute('''CREATE TABLE IF NOT EXISTS shelly1_state
             (datetime TEXT, state INTEGER NOT NULL)''')

conn.commit()

print("MQTT subscription is active")

def on_message(client, userdata, message):
    print(f"Message received on topic {message.topic}: {message.payload.decode()}")
    payload_data = json.loads(message.payload.decode())

    if message.topic == "espair/dht11":
        if "temperature" in payload_data and "humidity" in payload_data:
            current_datetime = payload_data.get("datetime", dt.now().strftime("%d/%m/%Y %H:%M:%S"))
            c.execute("INSERT INTO dht11_data (datetime, temperature, humidity) VALUES (?, ?, ?)", 
                      (current_datetime, payload_data["temperature"], payload_data["humidity"]))
            conn.commit()

    elif message.topic == "espair/mq2":
        if "mq2_value" in payload_data:
            current_datetime = payload_data.get("datetime", dt.now().strftime("%d/%m/%Y %H:%M:%S"))
            c.execute("INSERT INTO mq2_data (datetime, MQ2) VALUES (?, ?)",
                      (current_datetime, payload_data["mq2_value"]))
            conn.commit()

    elif message.topic == "espair/mq7":
        if "mq7_value" in payload_data:
            current_datetime = payload_data.get("datetime", dt.now().strftime("%d/%m/%Y %H:%M:%S"))
            c.execute("INSERT INTO mq7_data (datetime, MQ7) VALUES (?, ?)",
                      (current_datetime, payload_data["mq7_value"]))
            conn.commit()

    elif message.topic == "espair/mq135":
        if "mq135_value" in payload_data:
            current_datetime = payload_data.get("datetime", dt.now().strftime("%d/%m/%Y %H:%M:%S"))
            c.execute("INSERT INTO mq135_data (datetime, MQ135) VALUES (?, ?)",
                      (current_datetime, payload_data["mq135_value"]))
            conn.commit()

    elif message.topic == "espsafe/bat":
        if "value" in payload_data:
            current_datetime = payload_data.get("datetime", dt.now().strftime("%d/%m/%Y %H:%M:%S"))
            c.execute("INSERT INTO bat_data (datetime, BAT) VALUES (?, ?)",
                    (current_datetime, payload_data["value"]))
            conn.commit()

    elif message.topic == "shelly1/state":
        current_datetime = dt.now().strftime("%d/%m/%Y %H:%M:%S")
        payload_value = message.payload.decode()
        state_value = 1 if payload_value == "1" else 0
        c.execute("INSERT INTO shelly1_state (datetime, state) VALUES (?, ?)", (current_datetime, state_value))
        conn.commit()

    if userdata["message_count"] >= 5:
        client.disconnect()

def process_mq2_reading(reading):
    if reading > 250:
        publish_shelly_state(True)
    else:
        publish_shelly_state(False)

def publish_shelly_state(turn_on):
    action = "ON" if turn_on else "OFF"
    topic = "shelly1/state"
    payload = "1" if turn_on else "0"
    subscribe.simple(topic, payload, hostname=MQTT_BROKER)
    print(f"Published Shelly1 state to MQTT broker: {action}")

topics = ["espair/dht11", "espair/mq2", "espair/mq7", "espair/mq135", "espsafe/bat", "espsafe/flame", "espsafe/knust", "espsafe/water", "espsafe/pir", "shelly1/state"]
subscribe.callback(on_message, topics=topics, hostname="74.234.16.173", userdata={"message_count": 0})
