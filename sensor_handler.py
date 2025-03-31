import dht
import time
from machine import Pin

sensor = dht.DHT11(Pin(14))

def read_sensor():
    try:
        sensor.measure()
        temp = sensor.temperature()
        humidity = sensor.humidity()
        return temp, humidity
    except Exception as e:
        print("Error reading sensor:", e)
        return None, None
