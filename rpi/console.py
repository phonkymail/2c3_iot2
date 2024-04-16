import socket
import paho.mqtt.publish as publish
from datetime import datetime
import json
import requests
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import threading
import RPi.GPIO as GPIO
import time
import neopixel
import board

TRIGGER_PIN = 24
ECHO_PIN = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

RPI_SERVER_IP = "0.0.0.0"
RPI_SERVER_PORT1 = 12345
RPI_SERVER_PORT2 = 22345
MQTT_BROKER = "20.82.164.255"
SHELLY1_IP = "172.20.10.2"
SHELLY2_IP = "172.20.10.8"

mq2_readings = []
mq2_below_threshold = True
global shelly1_activated
shelly1_activated = False
global shelly2_activated
shelly2_activated = False

display_enabled = True
consecutive_zeros = 0  
consecutive_ones = 0  

pixel_pin = board.D18
num_pixels = 12
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER)

disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_address=0x3C)
disp.begin()
disp.clear()
disp.display()
font = ImageFont.load_default()
image = Image.new('1', (disp.width, disp.height))
draw = ImageDraw.Draw(image)

def read_distance():
    GPIO.output(TRIGGER_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIGGER_PIN, False)
    start_time = time.time()
    stop_time = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        stop_time = time.time()
    elapsed_time = stop_time - start_time
    distance_cm = (elapsed_time * 34300) / 2
    print(f"Distance: {distance_cm} cm")
    return distance_cm

def display_text(lines):
    if display_enabled:
        draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
        start_y_position = 10
        for i, line in enumerate(lines):
            y_position = start_y_position + i * 10
            draw.text((0, y_position), line, font=font, fill=255)
        disp.image(image)
        disp.display()
    else:
        print("Display is disabled, no update performed.")

def turn_on_display():
    global display_enabled
    display_enabled = True
    print("Display enabled.")

def turn_off_display():
    global display_enabled
    display_enabled = False
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    disp.image(image)
    disp.display()
    print("Display disabled.")

def display_sensor_info(temperature, humidity):
    date_str = datetime.now().strftime("%d/%m/%Y")
    time_str = datetime.now().strftime("%H:%M")
    lines = [f"Date: {date_str}", f"Time: {time_str}", f"Temp: {temperature}°C", f"Hum: {humidity}%"]
    display_text(lines)

def process_sensor_readings(mq2_reading, humidity):
    global shelly1_activated
    if humidity > 70 or mq2_reading > 100:
        if not shelly1_activated:
            print("Conditions met - Turning Shelly1 ON")
            control_shelly1_plug(True)

    elif humidity < 65 and mq2_reading < 100:
        if shelly1_activated:
            print("Conditions not met - Turning Shelly1 OFF")
            control_shelly1_plug(False)

def process_dht11_reading(sensor_data):
    global shelly1_activated, shelly2_activated, mq2_below_threshold
    print("Received DHT11 data:", sensor_data)
    temperature = sensor_data.get('temperature')
    humidity = sensor_data.get('humidity')
    
    if temperature is not None and humidity is not None:
        print(f"Displaying temperature: {temperature}, humidity: {humidity}")
        date_str = datetime.now().strftime("%d/%m/%Y")
        time_str = datetime.now().strftime("%H:%M")
        lines = [f"Date: {date_str}", f"Time: {time_str}", f"Temp: {temperature}°C", f"Hum: {humidity}%"]

        distance = read_distance()
        if distance <= 10:
            display_text(lines)
            turn_on_display()
        else:
            turn_off_display()

        publish_to_mqtt(sensor_data)

        if temperature < 19:
            print("Temperature is below 8°C, turning Shelly2 ON")
            control_shelly2_plug(True)
        else:
            print("Temperature is above 8°C, keeping Shelly2 OFF")
            control_shelly2_plug(False)

        if humidity > 70 or not mq2_below_threshold:
            print("Checking conditions for Shelly1 ON")
            publish_shelly1_state(True)
            if not shelly1_activated:
                print("Turning Shelly1 ON")                
                control_shelly1_plug(True)
        if humidity < 65 and mq2_below_threshold:
            print("Checking conditions for Shelly1 OFF")
            publish_shelly1_state(False)
            if shelly1_activated:
                print("Turning Shelly1 OFF")
                
                control_shelly1_plug(False)

    else:
        print("Missing temperature or humidity in DHT11 data")

def control_shelly1_plug(turn_on):
    global shelly1_activated
    action = "on" if turn_on else "off"
    if shelly1_activated != turn_on: 
        print(f"Action: Turning Shelly1 Plug {'ON' if turn_on else 'OFF'}")
        try:
            response = requests.get(f"http://{SHELLY1_IP}/relay/0?turn={action}")
            if response.status_code == 200:
                shelly1_activated = turn_on 
                publish_shelly1_state(turn_on)  
            else:
                print(f"Failed to turn {'ON' if turn_on else 'OFF'} Shelly1 Plug. HTTP Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error: {e}")
    else:
        print(f"Shelly1 Plug is already {'ON' if turn_on else 'OFF'}, no action needed.")
    
def control_shelly2_plug(turn_on):
    action = "on" if turn_on else "off"
    print(f"Turning Shelly2 Plug {'ON' if turn_on else 'OFF'}")
    try:
        requests.get(f"http://{SHELLY2_IP}/relay/0?turn={action}")
        publish_shelly2_state(turn_on) 
    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")

def process_mq2_reading(reading):
    global mq2_below_threshold
    print(f"Processing MQ2 reading: {reading}") 
    if reading < 100:
        mq2_below_threshold = True
        print("MQ2 reading is below threshold.")
    else:
        mq2_below_threshold = False
        print("MQ2 reading is above threshold.")

    mqtt_payload = {"mq2_value": reading}
    publish_to_mqtt({"sensor_type": "mq2", **mqtt_payload})
    print(f"Published MQ2 data to MQTT: {mqtt_payload}")

    if mq2_below_threshold and shelly1_activated:
        print("Conditions met to turn off Shelly1 due to MQ2 reading.")
        control_shelly1_plug(False)


def publish_shelly1_state(turn_on):
    action = "ON" if turn_on else "OFF"
    topic = "shelly1/state"
    payload = "1" if turn_on else "0"
    try:
        publish.single(topic, payload, hostname=MQTT_BROKER)
        print(f"Published Shelly1 state to MQTT broker: {action}, Payload: {payload}")
    except Exception as e:
        print(f"Failed to publish Shelly1 state: {e}")

def publish_shelly2_state(turn_on):
    action = "ON" if turn_on else "OFF"
    topic = "shelly2/state"
    payload = "1" if turn_on else "0" 
    publish.single(topic, payload, hostname=MQTT_BROKER)
    print(f"Published Shelly2 state to MQTT broker: {action}")

def publish_to_mqtt(sensor_data):
    sensor_type = sensor_data.get("sensor_type")
    if sensor_type:
        topic_prefix = "espair" if sensor_type in ['dht11', 'mq2', 'mq7', 'mq135'] else "espsafe"
        topic = f"{topic_prefix}/{sensor_type}"
        sensor_data["datetime"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        publish.single(topic, json.dumps(sensor_data), hostname=MQTT_BROKER)
        print(f"Published {sensor_type} data to MQTT broker: {topic}")
    else:
        print("Error: Sensor type missing in payload")

def tcp_server(port, process_function):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((RPI_SERVER_IP, port))
        s.listen()
        print(f"TCP server listening on port {port}...")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_connection, args=(conn, addr, process_function)).start()

def handle_connection(conn, addr, process_function):
    global consecutive_zeros, consecutive_ones 
    consecutive_zeros = 0 
    consecutive_ones = 0 
    with conn:
        print(f"Connected to: {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Received data from {addr}: {data.decode()}") 
            try:
                sensor_data = json.loads(data.decode())
                if sensor_data.get("sensor_type") == "mq2":
                    mq2_value = sensor_data.get("mq2_value")
                    if mq2_value is not None:
                        process_mq2_reading(mq2_value)
                    else:
                        print("MQ2 reading is missing in the data")
                elif sensor_data.get("sensor_type") == "dht11":
                    process_dht11_reading(sensor_data)

                elif sensor_data.get("sensor_type") == "pir":
                    if sensor_data.get("value") == 1:
                        consecutive_ones += 1
                        if consecutive_ones >= 3:
                            print("PIR sensor alert condition met, starting alert sequence.")
                            consecutive_ones = 0  
                            for _ in range(3):
                                pixels.fill((25, 0, 0)) 
                                pixels.show()
                                time.sleep(0.2)
                                pixels.fill((0, 0, 0))
                                pixels.show()
                                time.sleep(0.2)
                    else:
                        consecutive_ones = 0 
                
                elif sensor_data.get("sensor_type") in ["water", "flame"]:
                    if sensor_data.get("value") == 0:
                        consecutive_zeros += 1
                        if consecutive_zeros >= 3:
                            alert_type = "Water" if sensor_data.get("sensor_type") == "water" else "Flame"
                            print(f"{alert_type} sensor alert condition met, starting alert sequence.")
                            consecutive_zeros = 0 
                            for _ in range(3):
                                pixels.fill((25, 0, 0)) 
                                pixels.show()
                                time.sleep(0.2)
                                pixels.fill((0, 0, 0)) 
                                pixels.show()
                                time.sleep(0.2)
                    else:
                        consecutive_zeros = 0 

                else:
                    process_function(sensor_data) 
            except Exception as e:
                print(f"Error processing data from {addr}: {e}")


def start_tcp_server1():
    tcp_server(RPI_SERVER_PORT1, publish_to_mqtt)

def start_tcp_server2():
    tcp_server(RPI_SERVER_PORT2, publish_to_mqtt)

def main():
    threading.Thread(target=start_tcp_server1).start()
    threading.Thread(target=start_tcp_server2).start()

    try:

        while True:
            time.sleep(10) 
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Program terminated and GPIO cleaned up.")

        
if __name__ == "__main__":
    main()
