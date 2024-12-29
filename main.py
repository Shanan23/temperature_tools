import dht
from machine import I2C, Pin, Timer
import time
import network
import socket
import ujson
import ntptime
import os

# Konfigurasi sensor DHT11 dan pin relay
sensor = dht.DHT11(Pin(14))
heater_relay = Pin(12, Pin.OUT)
fan_relay = Pin(13, Pin.OUT)
humidifier_relay = Pin(15, Pin.OUT)

history = []

# Fungsi membaca data dari sensor
def read_sensor():
    try:
        sensor.measure()
        time.sleep(2)
        temp = sensor.temperature()
        humidity = sensor.humidity()

        # Tambahkan data ke history
        ntptime.settime()  # Waktu UTC
        print("Waktu berhasil disinkronisasi dengan NTP (UTC).")
        
        # Menambahkan offset GMT+7
        gmt_offset = 7 * 3600  # 7 jam dalam detik
        adjusted_time = time.time() + gmt_offset
        local_time = time.localtime(adjusted_time)
        formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            local_time[0], local_time[1], local_time[2], local_time[3], local_time[4], local_time[5]
        )

        history.append({"Suhu": temp, "Kelembaban": humidity, "Timestamp": formatted_time})
        if len(history) > 5:
            history.pop(0)

        return temp, humidity
    except Exception as e:
        print("Error reading sensor:", e)
        return None, None

# Fungsi untuk mengontrol perangkat
def control_device(action):
    if action == "Heater":
        heater_relay.on()
        fan_relay.off()
        humidifier_relay.off()
    elif action == "Fan":
        heater_relay.off()
        fan_relay.on()
        humidifier_relay.off()
    elif action == "Humidifier":
        heater_relay.off()
        fan_relay.off()
        humidifier_relay.on()
    else:
        heater_relay.off()
        fan_relay.off()
        humidifier_relay.off()

# Fungsi untuk memeriksa file konfigurasi WiFi
def load_wifi_config():
    try:
        with open("wifi_config.json", "r") as f:
            config = ujson.load(f)
            return config.get("ssid"), config.get("password")
    except Exception as e:
        print("Could not load WiFi config:", e)
        return None, None

# Fungsi untuk menyimpan file konfigurasi WiFi
def save_wifi_config(ssid, password):
    try:
        with open("wifi_config.json", "w") as f:
            config = {"ssid": ssid, "password": password}
            ujson.dump(config, f)
            print("WiFi config saved")
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
    wifi.connect(ssid, password)

    for _ in range(10):
        if wifi.isconnected():
            print("Connected to WiFi:", wifi.ifconfig())
            return True
        time.sleep(1)

    print("Failed to connect to WiFi. Switching to AP mode.")
    setup_ap_mode()
    return False

# Fungsi untuk mengaktifkan mode Access Point (AP)
def setup_ap_mode():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="NodeMCU_AP", password="12345678")
    print("AP Mode active:", ap.ifconfig())

# Fungsi untuk sinkronisasi waktu menggunakan NTP
def sync_time():
    try:
        ntptime.settime()
        print("Time synchronized")
    except Exception as e:
        print("Failed to sync time:", e)

# Fungsi Web Server
def start_webserver():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Web server running at:', addr)

    while True:
        cl, addr = s.accept()
        request = cl.recv(1024).decode()
        print('Request:', request)

        # Handle request
        if '/sensor' in request:
            temp, humidity = read_sensor()
            response = {
                "Suhu": temp,
                "Kelembaban": humidity,
                "History": history
            } if temp is not None else {"error": "Unable to read sensor"}
        elif '/heater/on' in request:
            control_device("Heater")
            response = {"message": "Heater turned on"}
        elif '/fan/on' in request:
            control_device("Fan")
            response = {"message": "Fan turned on"}
        elif '/humidifier/on' in request:
            control_device("Humidifier")
            response = {"message": "Humidifier turned on"}
        elif '/off' in request:
            control_device("Idle")
            response = {"message": "Devices turned off"}
        elif '/wifi' in request and 'ssid=' in request and 'password=' in request:
            try:
                ssid = request.split("ssid=")[1].split("&")[0]
                password = request.split("password=")[1].split(" ")[0]
                save_wifi_config(ssid, password)
                response = {"message": "WiFi config saved. Restart device to connect."}
            except Exception as e:
                response = {"error": "Invalid WiFi config"}
        elif '/reset' in request:
            reset_wifi_config()
            setup_ap_mode()
            response = {"message": "WiFi config reset. AP mode activated."}
        else:
            response = {"error": "Invalid endpoint"}

        response_json = ujson.dumps(response)
        cl.send('HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n')
        cl.send(response_json)
        cl.close()

# Fungsi Timer untuk pembacaan periodik
def periodic_read(t):
    temp, humidity = read_sensor()
    if temp is not None:
        print(f"Suhu: {temp}°C, Kelembaban: {humidity}%")

# Program Utama
if __name__ == "__main__":
    if not connect_wifi():
        setup_ap_mode()
    else:
        sync_time()

    timer = Timer(-1)
    timer.init(period=300000, mode=Timer.PERIODIC, callback=periodic_read)
    start_webserver()