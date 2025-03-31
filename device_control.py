from machine import Pin
from fuzzy_logic import fuzzy_tsukamoto

heater_relay = Pin(12, Pin.OUT)  # Mocked D6 relay 2
fan_relay = Pin(13, Pin.OUT)  # Mocked D7 relay 3
humidifier_relay = Pin(15, Pin.OUT)  # Mocked D8 relay 4

def relay(device, action):
    if device == 'heater':
        if action == 'on':
            heater_relay.on()
        else:
            heater_relay.off()
    elif device == 'fan':
        if action == 'on':
            fan_relay.on()
        else:
            fan_relay.off()
    elif device == 'humidifier':
        if action == 'on':
            humidifier_relay.on()
        else:
            humidifier_relay.off()

def control_device_fuzzy(temp, humidity):
    heater_val, fan_val, humidifier_val = fuzzy_tsukamoto(temp, humidity)
    
    if heater_val > 50:
        heater_relay.on()
    else:
        heater_relay.off()
    
    if fan_val > 50:
        fan_relay.on()
    else:
        fan_relay.off()
    
    if humidifier_val > 50:
        humidifier_relay.on()
    else:
        humidifier_relay.off()

    return heater_val, fan_val, humidifier_val
