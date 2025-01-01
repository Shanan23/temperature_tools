import network
import ujson
import os
import time
import ntptime


def load_wifi_config():
    try:
        with open("wifi_config.json", "r") as f:
            config = ujson.load(f)
            return config.get("ssid"), config.get("password")
    except Exception:
        return None, None

def save_wifi_config(ssid, password):
    try:
        with open("wifi_config.json", "w") as f:
            ujson.dump({"ssid": ssid, "password": password}, f)
    except Exception as e:
        print("Could not save WiFi config:", e)

def reset_wifi_config():
    try:
        os.remove("wifi_config.json")
    except Exception:
        pass

def connect_wifi():
    ssid, password = load_wifi_config()
    if not ssid or not password:
        return False

    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(ssid, password)
    for _ in range(10):
        if wifi.isconnected():
            print("Connected to WiFi:", wifi.ifconfig())
            return True
        time.sleep(2)
    return False

def setup_ap_mode():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="NodeMCU_AP", password="12345678")

def sync_time():
    try:
        ntptime.settime()
        print("Time synchronized")
    except Exception as e:
        print("Failed to sync time:", e)