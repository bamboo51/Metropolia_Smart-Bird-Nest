#include "sensor.h"
#include "streamer.h"
#include <thread>
#include <iostream>

int main() {
    // Set up GPIO
    setupGPIO();

    // Start the motion detection thread
    std::thread motionThread(monitorMotion);
    motionThread.detach();  // Run it in the background

    // Start the web server for video streaming
    int port = 8080;  // Port to run the web server
    startWebServer(port);  // Start the web server to stream video

    return 0;
}
