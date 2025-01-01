import socket
import ujson  # Gunakan json jika menggunakan CPython
from sensor import read_sensor
from control import control_device

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

        # Menambahkan endpoint '/tools' dengan deskripsi alat yang digunakan
        if '/tools' in request:
            # Daftar alat yang digunakan beserta deskripsinya
            tools = [
                {
                    "name": "NodeMCU",
                    "description": "Platform berbasis ESP8266 yang digunakan untuk menghubungkan sensor dan perangkat ke jaringan Wi-Fi. Mengendalikan sensor dan relay melalui pemrograman di Lua atau MicroPython."
                },
                {
                    "name": "4-Relay Module",
                    "description": "Modul relay dengan 4 saluran yang digunakan untuk mengontrol perangkat seperti heater, fan, dan humidifier. Setiap saluran relay dapat menghidupkan atau mematikan perangkat secara individual berdasarkan perintah dari NodeMCU."
                },
                {
                    "name": "Fan",
                    "description": "Kipas angin digunakan untuk mengatur suhu lingkungan. Kipas ini dikendalikan melalui relay dan berfungsi untuk mendinginkan ruangan jika suhu terlalu tinggi."
                },
                {
                    "name": "Heater",
                    "description": "Pemanas (heater) digunakan untuk menaikkan suhu ruangan. Pemanas ini dikendalikan melalui relay dan dinyalakan jika suhu terlalu rendah."
                },
                {
                    "name": "Humidifier",
                    "description": "Humidifier digunakan untuk menambah kelembaban udara di ruangan. Humidifier ini dikendalikan melalui relay dan dinyalakan jika kelembaban terlalu rendah."
                },
                {
                    "name": "Adaptor 12V",
                    "description": "Adaptor 12V digunakan untuk menyediakan daya listrik yang diperlukan oleh NodeMCU, relay, dan perangkat lainnya. Adaptor ini mengonversi daya dari sumber listrik (misalnya dari stopkontak) menjadi tegangan yang sesuai untuk menjalankan sistem."
                }
            ]
            response = {"tools": tools}
        elif '/sensor' in request:
            temp, humidity, control_intensity, history = read_sensor()
            response = {
                "Suhu": temp,
                "Kelembaban": humidity,
                "Kontrol": control_intensity,
                "History": history
            } if temp else {"error": "Unable to read sensor"}
        elif '/relay1' in request:
            control_device(100)
            response = {"message": "Heater turned on"}
        elif '/relay2' in request:
            control_device(200)
            response = {"message": "Fan turned on"}
        elif '/relay3' in request:
            control_device(300)
            response = {"message": "Humidifier turned on"}
        elif '/off' in request:
            control_device(0)
            response = {"message": "Devices turned off"}
        else:
            response = {"error": "Invalid endpoint"}

        # Convert response dictionary to JSON string
        response_json = ujson.dumps(response)

        # Send HTTP response
        cl.send('HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n')
        cl.sendall(response_json)  # Send JSON string
        cl.close()