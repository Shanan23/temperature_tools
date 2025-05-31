from machine import Pin
from fuzzy_logic import fuzzy_tsukamoto

backup_relay = Pin(14, Pin.OUT)  # Mocked D5 relay 4
humidifier_relay = Pin(12, Pin.OUT)  # Mocked D6 relay 1
fan_relay = Pin(13, Pin.OUT)  # Mocked D7 relay 2
heater_relay = Pin(15, Pin.OUT)  # Mocked D8 relay 3

def control_device_fuzzy(temp, humidity, manual_humidifier_flag, manual_heater_flag, manual_fan_flag, manual_backup_flag):
    if manual_humidifier_flag or manual_heater_flag or manual_fan_flag or manual_backup_flag:
        print("Manual control mode activated.")
        # If any manual control flag is set, use manual control
        heater_val = 100 if manual_heater_flag else 0
        fan_val = 100 if manual_fan_flag else 0
        humidifier_val = 100 if manual_humidifier_flag else 0
        backup_val = 100 if manual_backup_flag else 0
    else: 
        print("Automatic control mode activated.")
        heater_val, fan_val, humidifier_val = fuzzy_tsukamoto(temp, humidity)
    
    if heater_val == 100:
        heater_relay.value(1)  # Active low relay ON
    else:
        heater_relay.value(0)  # Active low relay OFF
    
    if fan_val == 100:
        fan_relay.value(1)  # Active low relay ON
    else:
        fan_relay.value(0)  # Active low relay OFF
    
    if humidifier_val == 100:
        humidifier_relay.value(1)  # Active low relay ON
    else:
        humidifier_relay.value(0)  # Active low relay OFF

    if backup_val == 100:
        backup_relay.value(1)
    else:
        backup_relay.value(0)

    return heater_val, fan_val, humidifier_val

def relay(device_name, action):
    """
    Manually control the device relay.
    device_name: 'heater', 'fan', or 'humidifier'
    action: 'on' or 'off'
    """
    if device_name == 'heater':
        if action == 'on':
            heater_relay.value(0)  # Active low relay ON
        elif action == 'off':
            heater_relay.value(1)  # Active low relay OFF
    elif device_name == 'fan':
        if action == 'on':
            fan_relay.value(0)  # Active low relay ON
        elif action == 'off':
            fan_relay.value(1)  # Active low relay OFF
    elif device_name == 'humidifier':
        if action == 'on':
            humidifier_relay.value(0)  # Active low relay ON
        elif action == 'off':
            humidifier_relay.value(1)  # Active low relay OFF
