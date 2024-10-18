# C++ Source File

## Build and Run Instructions
### 1. Install Required Libraries:

* Install **Poco**:
```bash
sudo apt-get install libpoco-dev
```

* Install OpenCV:
```bash
sudo apt-get install libopencv-dev
```

* Install wiringPi:
```bash
sudo apt-get install wiringpi
```

### 2. Build the Project

Run the following command in the directory
```bash
make
```

### 3. Run the Program

Start the program
```bash
./bird_nest_streamer
```

### 4. Access the Stream

Open a web browser and go to: `http://<raspberry_pi_ip>:8080`

You should now be able to view the live camera feed from your Raspberry Pi and see motion detection logs in the terminal