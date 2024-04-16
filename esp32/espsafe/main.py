import socket
import json
from machine import Pin, ADC
import _thread
import time
import wifi

flame = Pin(22, Pin.IN)
knust = Pin(26, Pin.IN)
water = ADC(Pin(35))
pir = Pin(5, Pin.IN)
bat = ADC(Pin(34))
bat.atten(ADC.ATTN_11DB)
water.atten(ADC.ATTN_11DB)

led_pin = Pin(14, Pin.OUT)

RPI_SERVER_IP = "172.20.10.4"
RPI_SERVER_PORT2 = 22345

def toggle_led(x):
    while True:
        led_pin.value(1)
        time.sleep(1)
        led_pin.value(0)
        time.sleep(x)

def send_data_to_rpi(data):
    retry_count = 0
    max_retries = 3
    success = False

    while retry_count < max_retries and not success:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((RPI_SERVER_IP, RPI_SERVER_PORT2))
            s.send(data.encode())
            s.close()
            print(f"Data sent successfully to {RPI_SERVER_IP}:{RPI_SERVER_PORT2}")
            success = True
        except OSError as e:
            retry_count += 1
            time.sleep(2)

    if not success:
        print("Failed to send data after retries")

def read_sensors():
    while True:
        flame_value = flame.value()
        send_data_to_rpi(json.dumps({"sensor_type": "flame", "value": flame_value}))
        print("flame   ",flame_value)

        knust_value = knust.value()
        send_data_to_rpi(json.dumps({"sensor_type": "knust", "value": knust_value}))
        print("knust    ",knust_value)
        
        water_value = water.read()
        send_data_to_rpi(json.dumps({"sensor_type": "water", "value": water_value}))
        print("water     ",water_value)

        pir_value = pir.value()
        send_data_to_rpi(json.dumps({"sensor_type": "pir", "value": pir_value}))
        print("pir   ",pir_value)

        sum_bat_value = 0
        num_measurements = 60
        for _ in range(num_measurements):
            sum_bat_value += bat.read()

        average_bat_value = sum_bat_value // num_measurements
        bat_pr = (- average_bat_value + 1670) * -0.105
        bat_pr = max(0, min(bat_pr, 100))
        send_data_to_rpi(json.dumps({"sensor_type": "bat", "value": bat_pr}))
        print("bat%    ", bat_pr)

        time.sleep(5)

def main():
    _thread.start_new_thread(read_sensors, ())
    _thread.start_new_thread(toggle_led, (15,))

if __name__ == "__main__":
    main()

