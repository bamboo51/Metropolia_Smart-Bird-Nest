#ifndef SENSOR_H
#define SENSOR_H

void setupGPIO();
bool detectMotion();
void controlLED(bool state);

#endif