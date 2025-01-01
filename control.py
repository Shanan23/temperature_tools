from machine import Pin

# Konfigurasi perangkat
heater_relay = Pin(12, Pin.OUT)
fan_relay = Pin(13, Pin.OUT)
humidifier_relay = Pin(15, Pin.OUT)

def control_device(intensity):
    if intensity < 25:
        heater_relay.off()
        fan_relay.off()
        humidifier_relay.off()
    elif intensity < 50:
        heater_relay.on()
        fan_relay.off()
        humidifier_relay.off()
    elif intensity < 75:
        heater_relay.on()
        fan_relay.off()
        humidifier_relay.on()
    elif intensity == 100:
        heater_relay.off()
        fan_relay.on()
        humidifier_relay.off()
    elif intensity == 200:
        heater_relay.on()
        fan_relay.of()
        humidifier_relay.off()
    elif intensity == 300:
        heater_relay.off()
        fan_relay.off()
        humidifier_relay.on()
    else:
        heater_relay.off()
        fan_relay.on()
        humidifier_relay.on()

def periodic_read(timer):
    from sensor import read_sensor
    temp, humidity, control_intensity, history = read_sensor()
    if temp is not None:
        print(f"Suhu: {temp}°C, Kelembaban: {humidity}%, Kontrol: {control_intensity}")