import socket
import ujson
from device_control import relay  # Import the relay function
from sensor_handler import read_sensor

def start_webserver():
    global last_temp, last_humidity  # Declare global variables to store last readings
    addr = socket.getaddrinfo('0.0.0.0', 1234)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Web server running at:', addr)  # Log server start

    while True:
        s.settimeout(10)  # Increased timeout to 60 seconds
        try:
            cl, addr = s.accept()
        except OSError as e:
            print("Server is still running, waiting for connections...")  # Additional log for clarity
            continue
        request = cl.recv(1024).decode()  # Receive request data
        print('Request:', request)

        # Handle request
        if '/turn_on_heater' in request:
            relay('heater', 'on')  # Turn on the heater
            response = {"status": "Heater turned on"}
        elif '/turn_on_fan' in request:
            relay('fan', 'on')  # Turn on the fan
            response = {"status": "Fan turned on"}
        elif '/turn_on_humidifier' in request:
            relay('humidifier', 'on')  # Turn on the humidifier
            response = {"status": "Humidifier turned on"}
        elif '/turn_off_all' in request:  # New endpoint to turn off all relays
            relay('heater', 'off')  # Turn off the heater
            relay('fan', 'off')  # Turn off the fan
            relay('humidifier', 'off')  # Turn off the humidifier
            response = {"status": "All relays turned off"}
        elif '/wifi' in request and 'ssid=' in request and 'password=' in request:
            try:
                ssid = request.split("ssid=")[1].split("&")[0]
                password = request.split("password=")[1].split(" ")[0]
                with open("config.txt", "w") as f:
                    f.write(f"[WIFI]\nssid={ssid}\npassword={password}\n")
                response = {"message": "WiFi config saved. Restart device to connect."}
            except Exception as e:
                response = {"error": "Invalid WiFi config"}
        elif '/timer' in request and 'period=' in request:
            try:
                period = int(request.split("period=")[1].split(" ")[0])
                with open("config.txt", "a") as f:
                    f.write(f"[TIMER]\nperiod={period}\n")
                response = {"message": f"Timer period updated to {period}ms"}
            except Exception as e:
                response = {"error": "Invalid timer period"}
        elif '/read_sensor' in request:
            temp, humidity = read_sensor()
            if temp is not None:
                response = {"suhu": temp, "kelembaban": humidity}
            else:
                response = {"error": "Failed to read sensor data"}
        elif '/tools' in request:  # New endpoint to get tools information
            response = {
                "tools": [
                    {"name": "Heater", "description": "Used for heating"},
                    {"name": "Fan", "description": "Used for cooling"},
                    {"name": "Humidifier", "description": "Used for adding moisture"}
                ]
            }
        else:
            response = {"error": "Invalid endpoint"}  # Default response for invalid endpoints

        response_json = ujson.dumps(response)  # Convert response to JSON
        
        print('Response:', response_json)
        
        cl.sendall('HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n'.encode())
        cl.sendall(response_json.encode())
        
        cl.close()
