import network
from machine import Pin
from time import sleep


ssid = ""
password = ""

led_pin = Pin(14, Pin.OUT)

def toggle_led(x):
    led_pin.value(1)
    sleep(x)
    led_pin.value(0)

def connect_wifi():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)
    while not station.isconnected():
        print("Connecting to WiFi...")
        toggle_led(0.3)
        sleep(1)

    print("Connected to WiFi.")
    print("IP Address:", station.ifconfig()[0])
    return station 
