import pigpio
import sensors.DHT22 as DHT22
import time

class TemperatureSensor:
    def __init__(self):
        self.pi = pigpio.pi()
        self.dht22 = DHT22.sensor(self.pi, 22)

    def read_sensor(self):
        self.dht22.trigger()
        humidity = '%.2f' % (self.dht22.humidity())
        temperature = '%.2f' % (self.dht22.temperature())
        return (humidity, temperature)
    
    def monitor(self):
        while True:
            humidity, temperature = self.read_sensor()
            print("Humidity is: " + humidity + "%")
            print("Temperature is: " + temperature + "C")
            time.sleep(10)
