# mc-system
![Static Budge](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![Static Budge](https://img.shields.io/badge/C-00599C?style=for-the-badge&logo=c&logoColor=white)
![Static Budge](https://img.shields.io/badge/Arduino-00979D?style=for-the-badge&logo=Arduino&logoColor=white)
![Static Budge](https://img.shields.io/badge/Qt-41CD52?style=for-the-badge&logo=qt&logoColor=white)


## Available Languages
- [English](README.md)
- [Русский](README.ru.md)

##  Description
A hardware-software system has been developed for monitoring the microclimate of industrial premises with a function for notifying personnel via employees’ wearable electronic devices. The device displays the current environmental parameters of the production facility (temperature, relative humidity, pressure, hydrocarbon concentration), compares them with the predefined maximum and minimum values set in the software, and automatically sends notifications in case of deviations. The initial network configuration is implemented through an access point, while further interaction is carried out via the MQTT protocol.

  <img src="docs/images/photo_2025-12-15_14-28-53.jpg" width=400>

## How the system works
  <img src="docs/images/topology.jpg" width=400>
  
__System deployment is carried out in several sequential stages:__
1. __Deployment of network and measurement infrastructure in the premises__ The system administrator installs a wireless router in the target facility, integrated into the enterprise’s local network. A sensor device is connected to this network and configured via a web interface: the IP address and MQTT broker port are specified, a room identifier is assigned, and the telemetry transmission interval is set.

2. __Preparation of personnel’s wearable electronic devices.__ Employees are provided with personal wearable electronic devices (watches), which are preconfigured by the system administrator. In their web interface, the parameters for connecting to the facility’s wireless network (SSID and password), the MQTT broker address and port, as well as the room identifier corresponding to the employee’s workplace are defined.

3. __Connection and configuration of the dispatcher workstation.__ The dispatcher’s computer, responsible for monitoring system performance, is also integrated into the enterprise’s network. At this workstation, the MQTT broker service is launched if necessary, or a connection is established to an already deployed broker, ensuring centralized data collection from all system nodes.

4. __Commissioning of the system.__ The system is put into operation after successful configuration and integration of all components.
   
## MQTT message transferring
<img src="docs/images/mqtt.png" width=400>
After a successful connection is established, data exchange between sensors, wearable electronic devices, and the desktop application is carried out through MQTT topics.

Sensors publish temperature, relative humidity, and pressure readings to topics generated based on the room name:

__room_name/sensors/temperature__

__room_name/sensors/humidity__

__room_name/sensors/pressure__

Wearable electronic devices receive personal messages through a topic linked to their identifier:

__clock_id/messages__

The structure of such messages includes three mandatory fields:

- sender (name of the sender)

- title (message title)

- message (message text)

The transmission format uses the ^ character as a delimiter between fields, ensuring correct string parsing on the device.

At first startup, the smartwatch sends a JSON packet with its information to the service topic connections, including chipId, clockId, IP address, and connection status.
Additionally, two special topics extend the functionality of the developed hardware‑software system:

__room_name/alarm__ – used to notify about critical deviations in microclimate parameters. When values exceed defined limits, an ALARM message is sent to all watches registered in the specified room. Upon receiving such a message, the watch triggers acoustic and vibration signals to warn the user of danger.

__datetime__ – used for publishing the current time, updated in real time. This ensures synchronization of displayed data and accuracy of system timestamps.

## Wearable electronic devices (smartwatches) for personnel
  <img src="docs/images/watches.png" width=400>
  A compact OLED display is used to present essential information and enable user interaction with the device.
The software part of the device is implemented as a multi‑window interface, with each window displaying unique information. A battery charge indicator is permanently shown in the upper‑right corner of the screen.  

**Main windows include:**
- **System clock and date display**  
- **Room information window** showing the zone name and sensor readings (temperature, relative humidity, hydrocarbon concentration)  
- **Administration messages window** for delivering operational notifications  

**Network integration:**  
These electronic devices are designed to be integrated into the enterprise’s corporate network. On first startup, the device initiates the creation of an access point with a unique identifier. Information about this access point, along with the IP address of the web interface, is displayed on the built‑in screen. This interface is used for initial configuration and setting connection parameters.  

After completing the initial setup, the device operates within the enterprise’s local network and is accessible via the IP address specified during initialization. To obtain information about the current network address, a special mechanism is provided: by double‑pressing the action button, the corresponding IP address is displayed on the screen.  

---
  
### Watches scheme
  <img src="docs/schemes/Schematic_BZHCH_CLOCK_2025-10-13.png" width=400>
  
  The clock device is based on an ESP8266 microcontroller with an integrated WiFi module. The microcontroller is supported by basic circuitry consisting of resistors. A control button is provided for device operation and menu navigation, along with a dedicated power switch.


 
## Sensors designed to measure microclimate parameters
  <img src="docs/images/photo_2025-12-15_14-34-00.jpg" width=400>
  
The most critical parameters to be monitored in industrial premises are temperature, relative humidity, and gas concentration.

For measuring temperature and relative humidity, __the DHT22__ sensor was used. This is a digital sensor with a single‑wire interface, which simplifies connection and reduces hardware requirements. It provides temperature measurements in the range from –40 to +80 °C with an accuracy of ±0.5 °C, and relative humidity measurements from 0 to 100 % with an accuracy of ±2 %. These characteristics make it suitable for use in workshops, warehouses, and laboratories. Built‑in calibration and a digital output signal increase noise immunity, while low power consumption allows the sensor to be applied in autonomous monitoring systems. Integration with the Arduino platform is achieved through ready‑made libraries, ensuring ease of programming and data exchange.

To monitor the gas composition of the air, a semiconductor sensor of __the MQ‑5 series__ was used, which is sensitive to methane, natural gas, and LPG. Its operating principle is based on changes in the resistance of a tin dioxide (SnO₂) sensing layer when interacting with gas molecules. In this project, the digital output was used, enabling detection of gas presence in a binary manner.
  
### Sensors scheme
<img src="docs/schemes/Schematic_BZHCH_SENSOR_2025-10-13.png" width=400>

The sensor device is built around an ATMega328U microcontroller, supported by basic circuitry consisting of capacitors and resistors. It integrates several modules for monitoring the microclimate and detecting gases in the air: a DHT22 sensor for measuring temperature and humidity, and an MQ-5 sensor for detecting hydrocarbon compounds.

Device interaction—including data retrieval, network configuration, and adjustment of the message transmission interval—is carried out via Ethernet, enabling the sensor to be identified and accessed within the network.

## Desktop application
  <img src="docs/images/app.jpg" width=400>
  Here’s the full English translation of your text in a clear technical style:

---
The desktop application performs functions of **data visualization, parameter configuration, and alert management**.  
The software module provides access to up‑to‑date information on the state of the microclimate and offers tools for setting threshold values and sending notifications to employees’ wearable electronic devices.

**Data storage:**  
To save user settings, the application uses a file‑based storage system:  
- `rooms.txt` contains mappings of room IP addresses to their names.  
- `users.txt` contains mappings of employee IP addresses to their names.  

**Interface structure:**  
The application interface is organized into several main functional sections:

1. **Microclimate monitoring.**  
   The main window displays current readings from sensors installed in production facilities. Each row contains information about the room name, temperature, relative humidity, and gas concentration, providing a clear real‑time overview of microclimate conditions.

2. **Adding rooms and personnel.**  
   The system supports expansion by adding new objects. When adding a room, the user enters its IP address and name. Personnel registration is performed similarly, with IP address and name specified, allowing wearable devices to be linked to specific users.

3. **Threshold configuration.**  
  The user can set acceptable ranges for monitored microclimate parameters, including minimum and maximum values for temperature and relative humidity. These thresholds are used for automatic analysis of incoming data and for generating alerts when parameters exceed defined limits.

4. **Employee notifications.**  
   The application implements the function of sending text messages to wearable devices (watches) linked to registered personnel IP addresses. The user selects a recipient from a dropdown list and enters the message text, which is then delivered to the corresponding device. This ensures prompt notification of personnel about critical changes in the production microclimate or other events.

**Additional functions:**  
- **Room deletion** removes the room from the list and deletes the corresponding entry in `rooms.txt`, excluding outdated monitoring zones.  
- **Employee deletion** removes the entry in `users.txt` (IP address and name), and the wearable device is excluded from the list of message recipients.  

**Technology:**  
The developed software is adapted for cross‑platform operation, with potential extension to other operating systems. Python was chosen as the programming language due to its extensive libraries for networking and data processing.

---
  


## Credits
|   Name   |   Role   | 
|----------|----------|
| [Alexsander Golov](https://github.com/lamerous)    | Software and Hardware Developer   | 
| [Solonovich Violetta](https://github.com/viosolo)    | Application Software Developer   | 

## 📄 License
This project is licensed under the [MIT license](LICENSE).
