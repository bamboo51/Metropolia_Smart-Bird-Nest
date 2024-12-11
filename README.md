# Smart Bird’s Nest  

A compact and eco-friendly IoT-based bird monitoring system designed to study birds’ behavior in their natural habitats without causing disturbances. This project integrates sensors, a Raspberry Pi, and AI-based bird species recognition to provide real-time insights into bird activities, environmental data, and species identification.  

---

## Features  
- **Non-Intrusive Monitoring**: Fits BirdLife Suomi Ry's smallest birdhouse dimensions to minimize disturbances.  
- **Real-Time Data Collection**: Streams audio, video, and environmental data such as temperature, humidity, motion, and light levels.  
- **AI Bird Species Recognition**: Utilizes BirdNet AI to classify bird species from audio recordings.  
- **Eco-Friendly Power**: Operates on solar energy for sustainable use.  
- **Educational and Conservation Tool**: Supports wildlife research, conservation, and student learning about nature.  

---

## Hardware Components  
- **Raspberry Pi 4B**: Core of the system for data processing and communication.  
- **Motion Sensor (HC-SR505)**: Detects movements inside the bird’s nest.  
- **Light Sensor (Adafruit BH1750)**: Monitors light levels to toggle IR LEDs for night vision.  
- **Temperature and Humidity Sensor (DHT22)**: Tracks environmental conditions.  
- **Camera Module (Raspberry Pi Camera Module 2 NoIR)**: Captures high-resolution images and videos with infrared capabilities.  
- **Microphone (MI-305)**: Records audio for bird species recognition.  
- **Solar Panel and Battery System**: Provides sustainable power supply.  

---

## Software Stack  
- **Programming Language**: Python  
- **Web Framework**: Flask  
- **Video Streaming**: MJPEG-based real-time streaming via HTTP.  
- **AI Model**: BirdNet for bird species recognition.  
- **Database**: SQLite3 for storing recognized bird species data.  

---

## System Architecture  
1. **Data Collection**: Sensors gather environmental data, and the camera/microphone captures video and audio when motion is detected.  
2. **Data Processing**: Raspberry Pi processes sensor readings and streams data through the Flask server.  
3. **AI Recognition**: BirdNet analyzes recorded audio to classify bird species with confidence levels.  
4. **Data Storage**: Captured images and bird species data are stored in an SQLite3 database.  

---

## Installation and Setup  

### Hardware Setup  
1. Connect sensors and modules to the Raspberry Pi using GPIO pins and communication interfaces (e.g., I2C, USB, CSI).  
2. Securely mount the hardware inside the birdhouse.  
3. Connect the solar panel, charging module, and battery for power.  

### Software Installation  
1. Clone the repository:  
   ```bash  
   git clone https://github.com/username/smart-bird-nest.git  
   cd smart-bird-nest  
2. Install dependencies:
   ```bash
    pip install -r requirements.txt
3. Run the main function:
   ```bash
   python main.py
4. Access the web interface at http://<raspberry_pi_ip>:5000.

--

## Usage
- Real-Time Streaming: View live video and sensor data on the streaming page.
- Bird Detection Logs: Access the records page for the latest bird sightings, including images and audio.
- Sensor Data: Retrieve environmental readings via JSON routes for integration with other systems.

--

## Future Enhancements
- Optimize solar power and battery efficiency for uninterrupted operation.
- Enable remote control and monitoring without Wi-Fi for deployment in remote areas.
- Develop a cloud-based platform to support multiple devices and expand scalability.
- Conduct extensive field testing in various environmental conditions.
