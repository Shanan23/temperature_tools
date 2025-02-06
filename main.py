import dht
import time
import network
import socket
import ujson
import ntptime
import os
import ssd1306
from machine import I2C, Pin, Timer
from i2c_lcd import I2cLcd, I2C_ADDR, I2C_SCL, I2C_SDA, I2C_FREQ
from time import sleep_ms


# Konfigurasi sensor DHT11 dan pin relay
sensor = dht.DHT11(Pin(14))
heater_relay = Pin(12, Pin.OUT) # D6 relay 2
fan_relay = Pin(13, Pin.OUT) # D7 relay 3
humidifier_relay = Pin(15, Pin.OUT) # D8 relay 4
ssid = "NodeMCU_AP"
password = "1234567"
ipAddress = ""
isShowSSID = True

history = []

# Initialize I2C (SDA, SCL pins)
i2c = I2C(scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=I2C_FREQ)

def fuzzy_tsukamoto(temp, humidity):
    # Membership functions untuk suhu
    dingin = max(0, min(1, (25 - temp) / (25 - 20)))
    normal = max(0, min((temp - 20) / (25 - 20), (30 - temp) / (30 - 25)))
    panas = max(0, min(1, (temp - 25) / (35 - 25)))
    
    # Membership functions untuk kelembaban
    kering = max(0, min(1, (50 - humidity) / (50 - 30)))
    sedang = max(0, min((humidity - 30) / (50 - 30), (70 - humidity) / (70 - 50)))
    lembab = max(0, min(1, (humidity - 50) / (80 - 50)))
    
    # Inferensi berdasarkan aturan fuzzy
    output_heater = min(dingin, kering)
    output_fan = min(panas, lembab)
    output_humidifier = min(dingin, sedang)
    
    # Defuzzifikasi dengan metode rata-rata terbobot
    heater_value = output_heater * 100  # Skala 0-100
    fan_value = output_fan * 100
    humidifier_value = output_humidifier * 100
    
    return heater_value, fan_value, humidifier_value

# Fungsi untuk mengontrol perangkat berdasarkan fuzzy logic
def control_device_fuzzy(temp, humidity):
    heater_val, fan_val, humidifier_val = fuzzy_tsukamoto(temp, humidity)
    
    if heater_val > 50:
        heater_relay.on()
    # else:
    #     heater_relay.off()
    
    if fan_val > 50:
        fan_relay.on()
    # else:
    #     fan_relay.off()
    
    if humidifier_val > 50:
        humidifier_relay.on()
    # else:
    #     humidifier_relay.off()

    return heater_val, fan_val, humidifier_val


# Function to scan all I2C addresses from 0x03 to 0x77
def scan_all_i2c_addresses():
    print("Scanning I2C addresses from 0x03 to 0x77...")
    devices = i2c.scan()
    if devices:
        print("I2C devices found at:")
        for device in devices:
            print(hex(device))
    else:
        print("No I2C devices found")
        
def running_text_lines(line3, line4, lcd, delay=300):
    """
    Menjalankan scrolling text hanya jika panjang teks > 20 karakter
    :param line3: String untuk baris ke-3
    :param line4: String untuk baris ke-4
    :param lcd: Object LCD
    :param delay: Delay scrolling dalam milidetik (ms)
    """
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
    lcd.clear()  # Clear LCD screen
    sleep_ms(1)
    lcd.putstr(f"Suhu: {temp}°C")  # Display temperature
    sleep_ms(1)
    lcd.move_to(0, 1)
    sleep_ms(1)
    lcd.putstr(f"Kelembaban: {humidity}%")  # Display humidity
    sleep_ms(1)
    running_text_lines(line3, line4, lcd)  # Display running text
    

def periodic_read(t):
    temp, humidity = read_sensor()
    if temp is not None:
        print(f"Suhu: {temp}°C, Kelembaban: {humidity}%")
        heater_val, fan_val, humidifier_val = control_device_fuzzy(temp, humidity)  # Kontrol dengan fuzzy logic
        line3 = f"heater_val:{heater_val} fan_val:{fan_val} humidifier_val:{humidifier_val}"
        line4 = "IP: " + ipAddress
        
        if(isShowSSID):
            line4 = "ssid: " + ssid +", pwd: " + password
        
        display_message(temp, humidity, line3, line4)  # Perbarui tampilan LCD
    else:
        print("Failed to read sensor")
        line4 = "IP: " + ipAddress
        display_message(0, 0,"Failed to read sensor", line4)  # Perbarui tampilan LCD


# Fungsi membaca data dari sensor
def read_sensor():
    try:

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

        sensor.measure()
        temp = sensor.temperature()
        humidity = sensor.humidity()

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
        # fan_relay.off()
        # humidifier_relay.off()
    elif action == "Fan":
        # heater_relay.off()
        fan_relay.on()
        # humidifier_relay.off()
    elif action == "Humidifier":
        # heater_relay.off()
        # fan_relay.off()
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
    wifi.disconnect()
    sleep_ms(500)
    print(f"wifi_config:{ssid}:{password}:")

    wifi.connect(ssid, password)
    for i in range(10):
        if wifi.isconnected():
            print("Terhubung ke WiFi:", wifi.ifconfig())
            print("Terhubung ke WiFi:", wifi.ifconfig()[0])
        
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
    ap.config(essid=ssid, password=password)
    print("AP Mode active:", ap.ifconfig())

# Fungsi untuk sinkronisasi waktu menggunakan NTP
def sync_time():
    try:
        ntptime.settime()
        print("Time synchronized ")
    except Exception as e:
        print("Failed to sync time:", e)

# Fungsi Web Server
def start_webserver():
    addr = socket.getaddrinfo('0.0.0.0', 1234)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Web server running at:', addr)

    while True:
        s.settimeout(10)  # Timeout 10 detik
        try:
            cl, addr = s.accept()
        except OSError as e:
            print("Timeout pada accept()", e)
            continue
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
        elif '/d6' in request:
            control_device("Heater")
            response = {"message": "Heater turned on"}
        elif '/d7' in request:
            control_device("Fan")
            response = {"message": "Fan turned on"}
        elif '/d8' in request:
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
        
        print('Response:', response_json)
        
        cl.sendall('HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n'.encode())
        cl.sendall(response_json.encode())
        
        cl.close()

# Program Utama
if __name__ == "__main__":
    read_sensor()
    
    # Call the function to scan all I2C addresses
    scan_all_i2c_addresses()

    # scan_all_i2c_addresses()
    lcd = I2cLcd(i2c, I2C_ADDR, 4, 20)
    lcd.clear()

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
        setup_ap_mode()
    else:
        sync_time()

    wifi = network.WLAN(network.STA_IF)
    isShowSSID = False
    ipAddress = f"{wifi.ifconfig()[0]}"

    timer = Timer(-1)
    timer.init(period=30000, mode=Timer.PERIODIC, callback=periodic_read)
    start_webserver()
    print("Web server started at:", ipAddress)