import dht
from machine import I2C, Pin
import time
import network
import socket
import ujson  # Menggunakan ujson untuk MicroPython
import ntptime

# Konfigurasi sensor DHT11 dan pin I2C
sensor = dht.DHT11(Pin(14))  # Pin D5 pada NodeMCU (GPIO14)
i2c = I2C(scl=Pin(5), sda=Pin(4))  # Pin I2C (SCL, SDA)

# Konfigurasi pin relay untuk kontrol perangkat
heater_relay = Pin(12, Pin.OUT)      # Relay untuk pemanas
fan_relay = Pin(13, Pin.OUT)         # Relay untuk kipas
humidifier_relay = Pin(15, Pin.OUT)  # Relay untuk humidifier

# Array untuk menyimpan data historis
history = []

# Fungsi untuk membaca data suhu dan kelembaban
def read_sensor():
    try:
        sensor.measure()
        time.sleep(2)  # Tambahkan sedikit waktu antara pembacaan
        temp = sensor.temperature()  # Suhu dalam Celcius
        humidity = sensor.humidity()  # Kelembaban dalam persentase

        # Dapatkan waktu saat ini dari timestamp
        timestamp = time.time()
        local_time = time.localtime(timestamp)
        formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            local_time[0], local_time[1], local_time[2], local_time[3], local_time[4], local_time[5]
        )

        # Simpan data historis dengan timestamp terformat
        history.append({"Suhu": temp, "Kelembaban": humidity, "Timestamp": formatted_time})

        # Batasi panjang history maksimal (contoh: 5 data terakhir)
        if len(history) > 5:
            history.pop(0)

        return temp, humidity
    except Exception as e:
        print("Error reading sensor:", e)
        return None, None

# Fungsi Fuzzyfication untuk suhu dan kelembaban
def fuzzyfication(temp, humidity):
    # Suhu Fuzzyfication
    if temp <= 20:
        temp_fuzzy = {'Dingin': 1, 'Normal': 0, 'Panas': 0}
    elif temp <= 30:
        temp_fuzzy = {'Dingin': (30 - temp) / 10, 'Normal': (temp - 20) / 10, 'Panas': 0}
    else:
        temp_fuzzy = {'Dingin': 0, 'Normal': (40 - temp) / 10, 'Panas': (temp - 30) / 10}

    # Kelembaban Fuzzyfication
    if humidity <= 40:
        humidity_fuzzy = {'Kering': 1, 'Normal': 0, 'Lembab': 0}
    elif humidity <= 60:
        humidity_fuzzy = {'Kering': (60 - humidity) / 20, 'Normal': (humidity - 40) / 20, 'Lembab': 0}
    else:
        humidity_fuzzy = {'Kering': 0, 'Normal': (80 - humidity) / 20, 'Lembab': (humidity - 60) / 20}

    return temp_fuzzy, humidity_fuzzy

# Fungsi untuk mengevaluasi aturan fuzzy dan melakukan defuzzification
def evaluate_rules(temp_fuzzy, humidity_fuzzy):
    # Evaluasi aturan berdasarkan derajat keanggotaan fuzzy
    if temp_fuzzy['Dingin'] > 0 and humidity_fuzzy['Kering'] > 0:
        action = "Turn on Heater"
    elif temp_fuzzy['Panas'] > 0 and humidity_fuzzy['Lembab'] > 0:
        action = "Turn on Fan"
    elif humidity_fuzzy['Lembab'] > 0:
        action = "Turn on Humidifier"
    elif temp_fuzzy['Normal'] > 0 and humidity_fuzzy['Normal'] > 0:
        action = "Do nothing"
    else:
        action = "Check System"

    return action

# Fungsi untuk mengontrol perangkat
def control_device(action):
    if action == "Turn on Heater":
        heater_relay.on()
        fan_relay.off()
        humidifier_relay.off()
    elif action == "Turn on Fan":
        heater_relay.off()
        fan_relay.on()
        humidifier_relay.off()
    elif action == "Turn on Humidifier":
        heater_relay.off()
        fan_relay.off()
        humidifier_relay.on()
    else:
        heater_relay.off()
        fan_relay.off()
        humidifier_relay.off()

# Menyiapkan koneksi Wi-Fi
ssid = "ShananFamily"
password = "ShaninHanan23"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)

# Menghubungkan ke Wi-Fi
wifi.connect(ssid, password)

# Menunggu hingga koneksi Wi-Fi berhasil
while not wifi.isconnected():
    print("Menghubungkan ke Wi-Fi...")
    time.sleep(1)
print("Koneksi Wi-Fi berhasil")
print("Alamat IP: ", wifi.ifconfig())

def sync_time():
    try:
        ntptime.settime()  # Sinkronisasi waktu dari server NTP
        print("Waktu berhasil disinkronisasi")
    except Exception as e:
        print("Gagal menyinkronkan waktu:", e)

# Panggil fungsi ini setelah koneksi Wi-Fi berhasil
sync_time()


# Fungsi untuk membuat web server
def start_webserver():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Listening on', addr)

    while True:
        cl, addr = s.accept()
        print('Client connected from', addr)
        request = cl.recv(1024)
        request = str(request)
        print('Request:', request)

        # Endpoint untuk membaca suhu dan kelembaban
        if '/sensor' in request:
            temp, humidity = read_sensor()

            if temp is not None and humidity is not None:
                response = {
                    "Suhu": temp,
                    "Kelembaban": humidity,
                    "History": history  # Tambahkan history ke respons
                }
                # Mengubah dictionary ke JSON string
                response_json = ujson.dumps(response)
            else:
                response_json = ujson.dumps({"error": "Unable to read sensor data"})

        # Endpoint untuk mengendalikan pemanas, kipas, atau humidifier
        elif '/heater/on' in request:
            control_device("Turn on Heater")
            response_json = ujson.dumps({"message": "Pemanas dinyalakan!"})
        elif '/fan/on' in request:
            control_device("Turn on Fan")
            response_json = ujson.dumps({"message": "Kipas dinyalakan!"})
        elif '/humidifier/on' in request:
            control_device("Turn on Humidifier")
            response_json = ujson.dumps({"message": "Humidifier dinyalakan!"})
        elif '/off' in request:
            control_device("Off")
            response_json = ujson.dumps({"message": "Perangkat dimatikan!"})
        else:
            response_json = ujson.dumps({"error": "Endpoint tidak ditemukan!"})


        print('Response:', response_json)
        # Kirim respon HTTP
        cl.send('HTTP/1.1 200 OK\r\n')
        cl.send('Content-Type: application/json\r\n')  # Mengubah content type menjadi JSON
        cl.send('\r\n')
        cl.send(response_json)
        cl.close()

# Mulai web server
start_webserver()
