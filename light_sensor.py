import smbus2
import time
import RPi.GPIO as GPIO

# LED setup
LED_PIN = 13

bus = smbus2.SMBus(1) # I2C bus number
BH1750_ADDRESS = 0x23 # I2C address of BH1750
CONT_H_RES_MODE = 0x10 # Continuous High-Resolution Mode

def read_light_sensor():
    """Read light level from the BH1750 sensor"""
    try:
        # send command to the BH1750 to start measurement
        bus.write_byte(BH1750_ADDRESS, CONT_H_RES_MODE)
        time.sleep(0.2)

        # 
        # read 2 bytes of data from the sensor
        data = bus.read_i2c_block_data(BH1750_ADDRESS, CONT_H_RES_MODE, 2)

        # convert the data to lux
        light_level = (data[0]<<8) | data[1]
        light_level = light_level / 1.2 # conversion factor for lux

        return light_level
    
    except Exception as e:
        print(f"Error reading light sensor: {e}")
        return None
    
def monitor_light_sensor():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED_PIN, GPIO.OUT)

    """Continuously monitor and log the light sensor value."""
    while True:
        light_level = read_light_sensor()
        if light_level is not None:
            print(f"Light level: {light_level:.2f} lux")

            if light_level < 20:
                GPIO.output(LED_PIN, GPIO.LOW)
            else:
                GPIO.output(LED_PIN, GPIO.HIGH)
            
        time.sleep(1)