import socket
import ujson as json
import time
from machine import Pin, ADC
import dht
import wifi
import network
from time import sleep

dht11_sensor = dht.DHT11(Pin(18))
mq2_pin = ADC(33)
mq7_pin = ADC(35)
mq135_pin = ADC(32)

RPI_SERVER_IP = "172.20.10.4"
RPI_SERVER_PORT = 12345

LED_PIN = 14
led = Pin(LED_PIN, Pin.OUT)

def toggle_led(x):
    led.value(1)
    sleep(x)
    led.value(0)

def send_data_to_rpi(data):
    ports = [RPI_SERVER_PORT]
    for port in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((RPI_SERVER_IP, port))
            s.sendall(data.encode())
            s.close()
        except OSError as e:
            print(f'Failed to send data to Raspberry Pi on port {port}:', e)

def read_dht11():
    try:
        dht11_sensor.measure()
        temp = dht11_sensor.temperature()
        hum = dht11_sensor.humidity()
        dht_data = {"sensor_type": "dht11", "temperature": temp, "humidity": hum}
        data = json.dumps(dht_data)
        send_data_to_rpi(data)
    except OSError as e:
        print('Not able to read DHT11 data:', e)

def read_mq2():
    try:
        mq2_value = mq2_pin.read()
        mq2_data = {"sensor_type": "mq2", "mq2_value": mq2_value}
        data = json.dumps(mq2_data)
        send_data_to_rpi(data)
    except OSError as e:
        print('Not able to read MQ2 data:', e)

def read_mq7():
    try:
        mq7_value = mq7_pin.read()
        mq7_data = {"sensor_type": "mq7", "mq7_value": mq7_value}
        data = json.dumps(mq7_data)
        send_data_to_rpi(data)
    except OSError as e:
        print('Not able to read MQ7 data:', e)

def read_mq135():
    try:
        mq135_value = mq135_pin.read()
        mq135_data = {"sensor_type": "mq135", "mq135_value": mq135_value}
        data = json.dumps(mq135_data)
        send_data_to_rpi(data)
    except OSError as e:
        print('Not able to read MQ135 data:', e)

def main():
    wifi.connect_wifi()
    while True:
        read_dht11()
        sleep(5)
        read_mq2()
        sleep(5)
        read_mq7()
        sleep(5)
        read_mq135()
        sleep(5)
        toggle_led(1)

if __name__ == "__main__":
    main()
