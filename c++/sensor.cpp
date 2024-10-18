#include "sensor.h"
#include <wiringPi.h>
#include <iostream>
#include <thread>
#include <chrono>

const int motionPin = 0;  // GPIO pin for motion sensor (PIR)
const int ledPin = 1;     // GPIO pin for LED

void setupGPIO() {
    wiringPiSetup();
    pinMode(motionPin, INPUT);
    pinMode(ledPin, OUTPUT);
}

// Function to detect motion using the PIR sensor
bool detectMotion() {
    return digitalRead(motionPin) == HIGH;
}

// Function to turn the LED on/off
void controlLED(bool state) {
    digitalWrite(ledPin, state ? HIGH : LOW);
}

// Thread for continuously monitoring motion
void monitorMotion() {
    while (true) {
        if (detectMotion()) {
            std::cout << "Motion detected!" << std::endl;
            controlLED(true);  // Turn on LED when motion is detected
        } else {
            controlLED(false); // Turn off LED when no motion
        }
        std::this_thread::sleep_for(std::chrono::seconds(1)); // Adjust delay
    }
}
