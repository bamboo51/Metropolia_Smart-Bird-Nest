#include "motion_detect.h"
#include <wiringPi.h>
#include <iostream>
#include <thread>
#include <chrono>

// GPIO pins
#define PIR_PIN 0
#define LED_PIN 2

extern bool is_streaming;

void motionDetection(void){
    int no_motion_duration = 0;
    const int motion_timeout = 1;

    while(true){
        int motion_detected = digitalRead(PIR_PIN);

        if(motion_detected){
            std::out<< "Motion detected! Starting stream..."<<std::endl;
            if(!is_streaming){
                is_streaming = true;
            }
            digitalWrite(LED_PIN, HIGH);
            no_motion_duration = 0;
        }else{
            if(is_streaming){
                no_motion_duration++;
                if(no_motion_duration >= motion_timeout){
                    std::cout<<"No motion detected. Stopping stream..."<<std::endl;
                    is_streaming = false;
            }
            digitalWrite(LED_PIN, LOW);
        }

        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
}