
# **Smart IoT Control System with Fuzzy Logic - Setup and API Documentation**

## **Overview**
This project uses NodeMCU (ESP8266) to control devices (heater, fan, humidifier) based on fuzzy logic applied to temperature and humidity readings. It includes Wi-Fi configuration (via AP mode or existing configuration) and provides a web-based API for remote control and monitoring.

---

## **Setup Instructions**

### **1. Initial Power On**
1. **First Boot Behavior**:
   - If no Wi-Fi configuration file (`wifi_config.json`) exists, the device will automatically switch to Access Point (AP) mode.
   - AP Credentials:
     - SSID: `NodeMCU_AP`
     - Password: `12345678`
   - Connect your PC or mobile device to this network.

2. **Access the Configuration Page**:
   - Open a browser and navigate to `http://192.168.4.1` to access the web interface for Wi-Fi configuration.

---

### **2. Configuring Wi-Fi**
1. Use the endpoint `/wifi` to configure Wi-Fi. 
   - Submit `SSID` and `Password` via the query string. For example:
     ```
     http://192.168.4.1:1234/wifi?ssid=YourSSID&password=YourPassword
     ```
2. Upon successful configuration:
   - The Wi-Fi credentials are saved in `wifi_config.json`.
   - Restart the device to connect to the configured Wi-Fi network.

---

### **3. Reset Wi-Fi Configuration**
To reset the Wi-Fi configuration and return to AP mode:
- Access the endpoint `/reset`:
  ```
  http://<device_ip>/reset
  ```
- The device will delete the `wifi_config.json` file and restart in AP mode.

---

### **4. Sync Time**
The system syncs time using NTP to GMT+7 (WIB). Ensure the device is connected to the internet for accurate time synchronization.

---

### **5. Periodic Sensor Readings**
Sensor readings (temperature and humidity) are automatically captured every 5 minutes and stored in the device's history (last 5 readings).

---

## **API Endpoints**

### **1. Sensor Data**
- **Endpoint**: `/sensor`
- **Method**: `GET`
- **Description**: Retrieves the current temperature, humidity, and the history of recent readings.
- **Response**:
  ```json
  {
    "Suhu": 28,
    "Kelembaban": 65,
    "History": [
      {"Suhu": 27, "Kelembaban": 63, "Timestamp": "2024-12-29 08:10:00"},
      {"Suhu": 28, "Kelembaban": 65, "Timestamp": "2024-12-29 08:15:00"}
    ]
  }
  ```

---

### **2. Control Devices**
#### **2.1 Turn On Heater**
- **Endpoint**: `/heater/on`
- **Method**: `GET`
- **Description**: Turns on the heater and turns off other devices.
- **Response**:
  ```json
  {
    "message": "Heater turned on"
  }
  ```

#### **2.2 Turn On Fan**
- **Endpoint**: `/fan/on`
- **Method**: `GET`
- **Description**: Turns on the fan and turns off other devices.
- **Response**:
  ```json
  {
    "message": "Fan turned on"
  }
  ```

#### **2.3 Turn On Humidifier**
- **Endpoint**: `/humidifier/on`
- **Method**: `GET`
- **Description**: Turns on the humidifier and turns off other devices.
- **Response**:
  ```json
  {
    "message": "Humidifier turned on"
  }
  ```

#### **2.4 Turn Off All Devices**
- **Endpoint**: `/off`
- **Method**: `GET`
- **Description**: Turns off all connected devices.
- **Response**:
  ```json
  {
    "message": "Devices turned off"
  }
  ```

---

### **3. Wi-Fi Configuration**
#### **3.1 Configure Wi-Fi**
- **Endpoint**: `/wifi`
- **Method**: `GET`
- **Description**: Configures the Wi-Fi credentials for the device.
- **Parameters**:
  - `ssid`: The name of the Wi-Fi network.
  - `password`: The password for the Wi-Fi network.
- **Example**:
  ```
  http://192.168.4.1/wifi?ssid=YourSSID&password=YourPassword
  ```
- **Response**:
  ```json
  {
    "message": "WiFi config saved. Restart device to connect."
  }
  ```

#### **3.2 Reset Wi-Fi**
- **Endpoint**: `/reset`
- **Method**: `GET`
- **Description**: Deletes the current Wi-Fi configuration and switches to AP mode.
- **Response**:
  ```json
  {
    "message": "WiFi config reset. AP mode activated."
  }
  ```

---

### **4. Time Synchronization**
- The time is automatically synchronized with NTP upon boot.
- The system adjusts to GMT+7 (WIB).

---

## **Debugging Tips**
1. **Device not accessible**:
   - Ensure the device is in AP mode and you are connected to `NodeMCU_AP`.
   - Check the device's IP address (default is `192.168.4.1` in AP mode).

2. **Wi-Fi connection fails**:
   - Reconfigure Wi-Fi via the `/wifi` endpoint in AP mode.
   - Check SSID and password for correctness.

3. **Sensors not working**:
   - Ensure the DHT sensor is properly connected to the designated GPIO pins.

---

## **Flow Summary**
1. **First-Time Setup**:
   - Connect to AP, configure Wi-Fi via `/wifi`.
2. **Normal Operation**:
   - Device connects to configured Wi-Fi and operates in STA mode.
   - Access `/sensor` and control devices via endpoints.
3. **Reconfiguration**:
   - Reset Wi-Fi with `/reset` to return to AP mode for reconfiguration. 

---

Feel free to modify or extend this README as your project evolves! 🚀
