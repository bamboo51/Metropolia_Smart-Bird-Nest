import smbus2
import RPi.GPIO as GPIO
import time

class LightSensor:
    def __init__(self, bus_number=1, sensor_address=0x23):
        self.bus = smbus2.SMBus(bus_number)
        self.sensor_address = sensor_address
        self.led_pin = 13
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.led_pin, GPIO.OUT)

    def read_light(self):
        try:
            self.bus.write_byte(self.sensor_address, 0x10)
            time.sleep(0.2)
            data = self.bus.read_i2c_block_data(self.sensor_address, 0x10, 2)
            light_level = ((data[0] << 8) | data[1]) / 1.2
            return light_level
        except Exception as e:
            print(f"Error reading light sensor: {e}")
            return None
        
    def monitor_light(self):
        while True:
            light_level = self.read_light()
            if light_level is not None:
                if light_level < 20:
                    GPIO.output(self.led_pin, GPIO.LOW)
                else:
                    GPIO.output(self.led_pin, GPIO.HIGH)
            time.sleep(10)