import smbus
import board
import busio
import RPi.GPIO as GPIO
import py_lis3mdl
import time
import adafruit_vl53l0x

ESC1_M1 = 19
ESC1_M2 = 26
ESC2_M1 = 20
ESC2_M2 = 21

prev_direction = "X"

min_distance = 50
safe_distance = 50
distance_var = 0
target_orientation = 0
motor_speed = 0.1 #0-1

# Initialize I2C bus and multiplexer
bus = smbus.SMBus(1)  # Use bus 1 for Raspberry Pi 4
TCAADDR = 0x70

# Initialize TOF sensors
i2c = busio.I2C(board.SCL, board.SDA)


# Function to select multiplexer channel
def tcaselect(channel):
    bus.write_byte(TCAADDR, 1 << channel)
    time.sleep(0.1)

# Initialize IMU sensor
tcaselect(4)
IMU = py_lis3mdl.LIS3MDL()
IMU.mode_continuous()

GPIO.setmode(GPIO.BCM)

GPIO.setup(ESC1_M1, GPIO.OUT)
GPIO.setup(ESC1_M2, GPIO.OUT)
GPIO.setup(ESC2_M1, GPIO.OUT)
GPIO.setup(ESC2_M2, GPIO.OUT)

ESC1_M1_pwm = GPIO.PWM(ESC1_M1, 50)
ESC1_M2_pwm = GPIO.PWM(ESC1_M2, 50)
ESC2_M1_pwm = GPIO.PWM(ESC2_M1, 50)
ESC2_M2_pwm = GPIO.PWM(ESC2_M2, 50)

ESC1_M1_pwm.start(0)
ESC1_M2_pwm.start(0)
ESC2_M1_pwm.start(0)
ESC2_M2_pwm.start(0)