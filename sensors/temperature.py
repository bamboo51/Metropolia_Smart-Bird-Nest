import pigpio
import DHT22
from time import sleep
import os

# Initiate GPIO for pigpio
pi = pigpio.pi()
# Setup the sensor
dht22 = DHT22.sensor(pi, 22) # use the actual GPIO pin name
dht22.trigger()

# We want our sleep time to be above 2 seconds.
sleepTime = 3
os.system("sudo pigpiod")

def readDHT22():
    # Get a new reading
    dht22.trigger()
    # Save our values
    humidity  = '%.2f' % (dht22.humidity())
    temp = '%.2f' % (dht22.temperature())
    return (humidity, temp)

while True:
    humidity, temperature = readDHT22()
    print("Humidity is: " + humidity + "%")
    print("Temperature is: " + temperature + "C")
    sleep(sleepTime)