import network
import os
import ssd1306
from machine import I2C, Pin, Timer, reset
from time import sleep_ms
from sensor_handler import read_sensor
from device_control import heater_relay, fan_relay, humidifier_relay
from fuzzy_logic import fuzzy_tsukamoto
from device_control import control_device_fuzzy, relay
from web_server import start_webserver
import ntptime  # Importing ntptime to fix the synchronization issue
import urequests  # Importing urequests for HTTP requests
import ujson  # Importing ujson for JSON handling
# import logging  # Importing logging for logging functionality
import gc  # Importing garbage collector
from i2c_lcd import I2cLcd, I2C_ADDR, I2C_SCL, I2C_SDA, I2C_FREQ

# Optimize imports by removing unused ones

import ufirebase as firebase

# Load configuration
def load_config():
    config = {}
    try:
        with open("setting.ini", "r") as f:
            for line in f:
                if line.strip() and not line.startswith('['):
                    key, value = line.strip().split('=')
                    config[key] = value
    except Exception as e:
        print("Error loading config:", e)
    return config

config = load_config()
ssid = config.get("ssid")
password = config.get("password")
ipAddress = ""
isShowSSID = True
try:
    timer_period = int(config.get("period", 60000))  # Increased timer period to reduce memory usage
except ValueError:
    print("Invalid value for period in configuration. Using default of 30000.")
    timer_period = 30000

# Initialize I2C (SDA, SCL pins)
i2c = I2C(scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=I2C_FREQ)

# Function to scan all I2C addresses from 0x03 to 0x77
def scan_all_i2c_addresses():
    print("Scanning I2C addresses from 0x03 to 0x77...")
    devices = i2c.scan()
    if devices:
        print("I2C devices found at:")
        for device in devices:
            print(hex(device))
        return True
    else:
        print("No I2C devices found")
        return False

def running_text_lines(line3, line4, lcd, delay=300):
    lcd.move_to(0, 2)
    lcd.putstr(line3[:20])  # Tampilkan teks statis jika <= 20
    lcd.move_to(0, 3)
    lcd.putstr(line4[:20])  # Tampilkan teks statis jika <= 20

    # Jalankan scrolling hanya jika panjang teks lebih dari 20
    if len(line3) > 20 or len(line4) > 20:
        padding = " " * 20  # Padding untuk efek scrolling
        text3 = (padding + line3 + padding) if len(line3) > 20 else line3
        text4 = (padding + line4 + padding) if len(line4) > 20 else line4

        for i in range(max(len(text3), len(text4)) - 19):  # Scroll hanya jika perlu
            lcd.move_to(0, 2)
            lcd.putstr(text3[i:i+20]) if len(line3) > 20 else None
            lcd.move_to(0, 3)
            lcd.putstr(text4[i:i+20]) if len(line4) > 20 else None
            sleep_ms(delay)

# Fungsi utama untuk menampilkan teks
def display_message(temp, humidity, line3, line4):
    if lcd is not None:  # Only clear LCD if initialized
        lcd.clear()  # Clear LCD screen
        gc.collect()  # Trigger garbage collection
    sleep_ms(1)
    lcd.putstr(f"Suhu: {temp}°C")  # Display temperature
    sleep_ms(1)
    lcd.move_to(0, 1)
    sleep_ms(1)
    lcd.putstr(f"Kelembaban: {humidity}%")  # Display humidity
    sleep_ms(1)
    running_text_lines(line3, line4, lcd)  # Display running text

def periodic_read(t):
    global stop_script  # Ensure stop_script is recognized as a global variable
    if not stop_script:  # Check if the script should continue running
        gc.collect()  # Trigger garbage collection to free up memory
        try:
            temp, humidity = read_sensor()
            if temp is not None:
                print(f"Suhu: {temp}°C, Kelembaban: {humidity}%")
                heater_val, fan_val, humidifier_val = control_device_fuzzy(temp, humidity)  # Kontrol dengan fuzzy logic
                print(f"Heater Value: {heater_val}, Fan Value: {fan_val}, Humidifier Value: {humidifier_val}")
                line3 = f"HV: {heater_val} FV: {fan_val} HV: {humidifier_val}"  # Shortened variable names for display
                line4 = "IP: " + ipAddress
                
                if(isShowSSID):
                    line4 = "ssid: " + ssid +", pwd: " + password
                
                if lcd is not None:  # Only update LCD if initialized
                    display_message(temp, humidity, line3, line4)  # Perbarui tampilan LCD
                
                send_data_to_firebase(temp, humidity, ntptime.time())  # Send data to Firebase
            else:
                print("Failed to read sensor")
                line4 = "IP: " + ipAddress
                if lcd is not None:  # Only update LCD if initialized
                    display_message(0, 0,"Failed to read sensor", line4)  # Perbarui tampilan LCD
        except MemoryError:
            print("MemoryError: Insufficient memory available.")
        except Exception as e:
            print(f"An error occurred: {e}")

# Fungsi untuk memeriksa file konfigurasi WiFi
def load_wifi_config():
    try:
        config = load_config()  # Load from setting.ini
        ssid = config.get("ssid")
        password = config.get("password")
        return ssid, password
    except Exception as e:
        print("Could not load WiFi config:", e)
        return None, None

# Fungsi untuk menyimpan file konfigurasi WiFi
def save_wifi_config(ssid, password):
    try:
        with open("setting.ini", "w") as f:
            f.write(f"ssid={ssid}\n")
            f.write(f"password={password}\n")
            print("WiFi config saved to config.txt")
    except Exception as e:
        print("Could not save WiFi config:", e)

# Fungsi untuk menghapus file konfigurasi WiFi
def reset_wifi_config():
    try:
        if "wifi_config.json" in os.listdir():
            os.remove("wifi_config.json")
            print("WiFi config reset. File deleted.")
    except Exception as e:
        print("Error resetting WiFi config:", e)

# Fungsi koneksi WiFi
def connect_wifi():
    ssid, password = load_wifi_config()
    if not ssid or not password:
        print("WiFi config not found. Switching to AP mode.")
        setup_ap_mode()
        return False

    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.disconnect()
    sleep_ms(500)
    print(f"wifi_config:{ssid}:{password}:")

    wifi.connect(ssid, password)
    for i in range(10):
        if wifi.isconnected():
            ip, _, gateway, _ = wifi.ifconfig()
            print("Connected to WiFi")
            print("IP Address:", ip)
            print("Gateway:", gateway)

            data = '{"ip": "' + ip + '"}'
            # urequests.put(FIREBASE_URL, data=data)
            print(f"IP {ip} tersimpan di Firebase")
            return True
        print(f"Koneksi gagal, percobaan ke-{i+1}")  # Debug log
        sleep_ms(1000)

    print("Failed to connect to WiFi. Switching to AP mode.")
    setup_ap_mode()
    return False

# Fungsi untuk mengaktifkan mode Access Point (AP)
def setup_ap_mode():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    try:
        ap.config(essid=ssid, password=password)
        print("AP Mode active:", ap.ifconfig())
    except OSError as e:
        print("Error setting AP config:", e)

# Fungsi untuk sinkronisasi waktu menggunakan NTP
def sync_time():
    try:
        ntptime.settime()
        print("Time synchronized ")
    except Exception as e:
        print("Failed to sync time:", e)

FIREBASE_URL = config.get("firebase_url", "http://temperatureapp-94d6a.firebaseio.com/")  # Firebase URL from config

def send_data_to_firebase(temp, humidity, timestamp):
    print(f"Sending data to Firebase: Temperature: {temp}, Humidity: {humidity}")  # Log data being sent
    data = { 
        "timestamp": timestamp,
        "suhu": temp,
        "kelembaban": humidity
    }
    
    firebase.setURL(FIREBASE_URL)  # Set Firebase URL
    gc.collect()  # Trigger garbage collection after sending data
    try:
        firebase.put("history", ujson.dumps(data))  # Send data to Firebase
        print(f"Data sent to Firebase: {data}")  # Print successful data send
    except Exception as e:
        print(f"Failed to send data to Firebase: {e}")  # Print any errors

# Program Utama
if __name__ == "__main__":
    read_sensor()
    
    # Call the function to scan all I2C addresses
    devices_found = scan_all_i2c_addresses()
    
    if devices_found:
        lcd = I2cLcd(i2c, I2C_ADDR, 4, 20)
        lcd.clear()
    else:
        print("No I2C devices found, skipping LCD initialization")
        lcd = None  # Explicitly set lcd to None if no devices are found

    if lcd is not None:  # Only update LCD if initialized
        sleep_ms(200)
        lcd.move_to(0, 0)
        lcd.putstr("Welcome")  # Display on the first line
        sleep_ms(200)
        lcd.move_to(0, 1)
        lcd.putstr("")  # Display on the second line
        sleep_ms(200)
        lcd.move_to(0, 2)
        lcd.putstr("initialize sensor")     # Display on the third line
        sleep_ms(200)
        lcd.move_to(0, 3)
        lcd.putstr("initialize wifi")     # Display on the third line
        sleep_ms(200)

    if not connect_wifi(): 
        setup_ap_mode()  # Switch to AP mode if WiFi config is not found
    else:
        sync_time()

    wifi = network.WLAN(network.STA_IF)
    isShowSSID = False
    ipAddress = f"{wifi.ifconfig()[0]}"

    timer = Timer(-1)
    timer.init(period=timer_period, mode=Timer.PERIODIC, callback=periodic_read)
    gc.collect()  # Trigger garbage collection after setting up the timer
    
    # Add a mechanism to handle the stopScript command
    stop_script = False  # Flag to control the script execution

    def handle_stop_script():
        global stop_script
        stop_script = True  # Set the flag to stop the script

    start_webserver()
    print("Web server started at:", ipAddress)
</create_file>
