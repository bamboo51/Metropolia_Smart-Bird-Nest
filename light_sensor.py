import smbus2
import time

# Get I2C bus
bus = smbus2.SMBus(1)

# BH1750 Address
bh1750_address = 0x23

# BH1750 Command: Continuously H-Resolution Mode
CONT_H_RES_MODE = 0x10

def read_light():
    bus.write_byte(bh1750_address, CONT_H_RES_MODE)
    time.sleep(0.2)

    # read light data
    data = bus.read_i2c_block_data(bh1750_address, CONT_H_RES_MODE, 2)

    # convert the data
    light_level = (data[0]<<8) | data[1]
    light_level = light_level / 1.2  # Convert to lux

    return light_level

while True:
    light_level = read_light()
    print(f"Light level: {light_level:.2f} lux")
    time.sleep(1)