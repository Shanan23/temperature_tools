from machine import Pin
import dht
import time
from control import control_device
from utils import fuzzy_membership, defuzzification, get_current_time

# Konfigurasi sensor DHT11 dan perangkat
sensor = dht.DHT11(Pin(14))
history = []

temp_fuzzy = {
    "low": [0, 15, 20],
    "normal": [18, 25, 30],
    "high": [28, 35, 40]
}

humidity_fuzzy = {
    "low": [0, 20, 40],
    "normal": [30, 50, 70],
    "high": [60, 80, 100]
}

control_fuzzy = {
    "off": [0, 0, 25],
    "low": [20, 40, 60],
    "medium": [50, 70, 90],
    "high": [80, 100, 100]
}

rules = [
    {"if": ("temp", "low"), "and": ("humidity", "low"), "then": "high"},
    {"if": ("temp", "low"), "and": ("humidity", "normal"), "then": "medium"},
    {"if": ("temp", "normal"), "and": ("humidity", "low"), "then": "medium"},
    {"if": ("temp", "high"), "or": ("humidity", "high"), "then": "off"},
]

def read_sensor():
    try:
        sensor.measure()
        time.sleep(2)
        temp = sensor.temperature()
        humidity = sensor.humidity()

        # Hitung derajat keanggotaan
        temp_membership = {key: fuzzy_membership(temp, temp_fuzzy[key]) for key in temp_fuzzy}
        print("Temp:", temp, temp_membership)

        humidity_membership = {key: fuzzy_membership(humidity, humidity_fuzzy[key]) for key in humidity_fuzzy}
        print("Membership:", temp_membership, humidity_membership)

        # Evaluasi aturan fuzzy
        fuzzy_outputs = {}
        for rule in rules:
            temp_degree = temp_membership[rule["if"][1]]
            humidity_degree = humidity_membership[rule["and"][1]] if "and" in rule else 0
            degree = min(temp_degree, humidity_degree) if "and" in rule else max(temp_degree, humidity_degree)
            fuzzy_outputs[rule["then"]] = max(fuzzy_outputs.get(rule["then"], 0), degree)

        print("Fuzzy Outputs:", fuzzy_outputs)

        # Defuzzifikasi
        control_intensity = defuzzification(fuzzy_outputs)
        print("Control Intensity:", control_intensity)

        # Kontrol perangkat
        control_device(control_intensity)

        # Tambahkan data ke history
        timestamp = get_current_time()
        history.append({"Suhu": temp, "Kelembaban": humidity, "Timestamp": timestamp, "Control": control_intensity})
        if len(history) > 5:
            history.pop(0)

        return temp, humidity, control_intensity, history
    except Exception as e:
        print("Error reading sensor:", e)
        return None, None, None, None