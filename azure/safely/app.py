from datetime import datetime
import base64
from io import BytesIO
from flask import Flask, render_template, request
from get_air_sensors import get_mq_data, get_room_data, get_battery_data, get_shelly1_state, get_shelly2_state
from matplotlib.figure import Figure
import numpy as np

app = Flask(__name__)

def room_temp():
    timestamps, room_temperatures, _ = get_room_data(20)
    fig = Figure()
    ax = fig.subplots()
    fig.subplots_adjust(bottom=0.3)
    ax.tick_params(axis='x', which='both', rotation=65, labelsize=8)
    ax.set_facecolor("#DBF4A7")
    ax.plot(timestamps, room_temperatures, linestyle="solid", c="#004E66", linewidth="2", marker="o", mec="#2374AB", mfc="#BFD7EA", markersize="3")
    ax.set_xlabel("Timestamps", fontsize=8)
    ax.set_ylabel("Temperature °C", fontsize=10)
    fig.patch.set_facecolor("#EBEBFF")
    ax.grid(color='#DC1829', linestyle='--', linewidth=0.2)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data

def room_hum():
    timestamps, _, room_humidities = get_room_data(20)
    fig = Figure()
    ax = fig.subplots()
    fig.subplots_adjust(bottom=0.3)
    ax.tick_params(axis='x', which='both', rotation=65, labelsize=8)
    ax.set_facecolor("#DBF4A7")
    ax.plot(timestamps, room_humidities, linestyle="solid", c="#BA1F33", linewidth="2", marker="o", mec="#2374AB", mfc="#BFD7EA", markersize="3")
    ax.set_xlabel("Timestamps", fontsize=8)
    ax.set_ylabel("Humidity %", fontsize=10)
    fig.patch.set_facecolor("#EBEBFF")
    ax.grid(color='#DC1829', linestyle='--', linewidth=0.2)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data

def room_ppm():
    mq_data = get_mq_data(20)
    encoded_images = {}
    for sensor_name, color in [('mq2', '#69D025'), ('mq7', '#FF5733'), ('mq135', '#00798C')]:
        fig = Figure()
        ax = fig.subplots()
        fig.subplots_adjust(bottom=0.3)
        ax.tick_params(axis='x', which='both', rotation=65, labelsize=8)
        fig.patch.set_facecolor("#EBEBFF")
        datetimes = np.array(mq_data[sensor_name]["datetimes"])
        values = np.array(mq_data[sensor_name]["values"])
        sorted_indices = np.argsort(datetimes)
        ax.plot(datetimes[sorted_indices], values[sorted_indices], linestyle="solid", color=color, linewidth=2, marker="o", mec="#2374AB", mfc="#BFD7EA", markersize=3)
        ax.set_xlabel("Timestamps", fontsize=8)
        ax.set_ylabel("PPM", fontsize=10)
        ax.grid(color='#DC1829', linestyle='--', linewidth=0.2)
        ax.legend([sensor_name.upper().replace('MQ', 'MQ-')], loc='lower left', fontsize=7)
        buf = BytesIO()
        fig.savefig(buf, format="png")
        encoded_images[sensor_name] = base64.b64encode(buf.getbuffer()).decode("ascii")
    return encoded_images['mq2'], encoded_images['mq7'], encoded_images['mq135']

def battery_data():
    timestamps, battery_values = get_battery_data(100)
    if not timestamps or not battery_values:
        print("No data available for plotting.")
        return None  # Handle the case where there is no data gracefully
    fig = Figure(figsize=(8, 4), dpi=120)  # Increased size and DPI
    fig.patch.set_facecolor("#EBEBFF")
    ax = fig.subplots()
    ax.plot(timestamps, battery_values, linestyle="solid", c="#FF4500", linewidth=2)
    ax.set_xlabel('Timestamp', fontsize=8)
    ax.set_ylabel('Battery %', fontsize=8)
    ax.set_title('Battery % over time', fontsize=10)
    ax.grid(color='gray', linestyle='--', linewidth=0.5)
    ax.tick_params(axis='x', rotation=90, labelsize=4)
    ax.set_ylim(0, 100)
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode('ascii')
    return data

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/room_1')
def room_1():
    room_temperature = room_temp()
    room_humidity = room_hum()
    room_ppm_mq2, room_ppm_mq7, room_ppm_mq135 = room_ppm()
    return render_template('room_1.html', room_temperature=room_temperature, room_humidity=room_humidity, room_ppm_mq2=room_ppm_mq2, room_ppm_mq7=room_ppm_mq7, room_ppm_mq135=room_ppm_mq135)

@app.route('/room_2')
def room_2():
    battery_graph = battery_data()
    if not battery_graph:
        print("Failed to generate battery graph.")
    shelly1_state = get_shelly1_state()
    shelly2_state = get_shelly2_state()
    return render_template('room_2.html', battery_graph=battery_graph, shelly1_state=shelly1_state, shelly2_state=shelly2_state)


@app.route('/room_3')
def room_3():
    return render_template('room_3.html')

if __name__ == '__main__':
    app.run(debug=True)
