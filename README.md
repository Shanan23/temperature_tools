# Smart Room Controller with Fuzzy Logic

This project demonstrates a smart room control system using NodeMCU with temperature and humidity sensors, a relay-controlled heater, fan, and USB humidifier. The system uses fuzzy logic to determine the optimal actions based on sensor readings. It also includes a web server to monitor and control devices via HTTP endpoints.

## Features
- **Temperature and Humidity Monitoring**: Uses DHT11 to measure the environment.
- **Fuzzy Logic Control**: Makes decisions to activate heater, fan, or humidifier based on sensor data.
- **Web Server**: Provides endpoints for real-time monitoring and device control.
- **History Storage**: Maintains the last 5 sensor readings with timestamps.
- **NTP Time Sync**: Ensures timestamps are accurate by syncing with NTP servers.

## Hardware Requirements
- NodeMCU ESP8266
- DHT11 Sensor
- Relay Module
  - Heater connected to Pin D6 (GPIO12)
  - Fan connected to Pin D7 (GPIO13)
  - Humidifier connected to Pin D8 (GPIO15)
- USB Humidifier
- Heater Device
- Fan Device
- Power Supply

## Software Requirements
- MicroPython firmware for NodeMCU
- Python Libraries:
  - `dht`
  - `machine`
  - `time`
  - `network`
  - `socket`
  - `ujson`
  - `ntptime`

## Circuit Diagram
1. Connect the DHT11 sensor's data pin to GPIO14 (D5).
2. Connect the relay module's control pins to GPIO12 (D6), GPIO13 (D7), and GPIO15 (D8) respectively.
3. Ensure common ground between the NodeMCU and other components.

## How It Works
1. The system reads temperature and humidity from the DHT11 sensor.
2. Fuzzy logic evaluates the sensor data to determine the appropriate action:
   - Turn on the heater if the room is cold and dry.
   - Turn on the fan if the room is hot and humid.
   - Turn on the humidifier if the air is dry.
3. Sensor data and actions are logged with timestamps.
4. A web server exposes the following endpoints:
   - `/sensor`: Returns the last 5 sensor readings.
   - `/heater/on`: Activates the heater.
   - `/fan/on`: Activates the fan.
   - `/humidifier/on`: Activates the humidifier.
   - `/off`: Deactivates all devices.

## Installation
1. Flash MicroPython onto your NodeMCU.
2. Upload the script to the board using an IDE like Thonny.
3. Modify the `ssid` and `password` variables to match your Wi-Fi credentials.
4. Run the script.

## Usage
1. Power on the NodeMCU.
2. Access the web server using the NodeMCU's IP address (shown in the serial monitor after successful Wi-Fi connection).
3. Use a browser or tools like Postman to interact with the endpoints.

## Example Response
### `/sensor` Endpoint Response:
```json
{
  "Kelembaban": 75,
  "Suhu": 27,
  "History": [
    {"Suhu": 25, "Kelembaban": 55, "Timestamp": "2024-12-25 14:32:10"},
    {"Suhu": 24, "Kelembaban": 53, "Timestamp": "2024-12-25 14:35:15"},
    {"Suhu": 23, "Kelembaban": 50, "Timestamp": "2024-12-25 14:38:20"},
    {"Suhu": 26, "Kelembaban": 57, "Timestamp": "2024-12-25 14:41:25"},
    {"Suhu": 27, "Kelembaban": 59, "Timestamp": "2024-12-25 14:44:30"}
  ]
}
```

## Future Enhancements
- Add support for more sensors like CO2 or motion detectors.
- Implement MQTT for real-time updates.
- Add a mobile-friendly web interface.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- MicroPython documentation and community for helpful resources.
- OpenAI for assistance with code structuring and fuzzy logic implementation.

