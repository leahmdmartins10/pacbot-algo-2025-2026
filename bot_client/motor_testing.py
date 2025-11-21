#TODO
#going to motor testing with raspberry pi
#ESC1 = 19,26
#ESC2 = 20,21

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

motor_speed = 0.5 #0-1

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

def motor_fwd(direction, speed):
    print(f"Moving {direction} at {speed} speed")
    if direction == 'N':
        ESC2_M1_pwm.ChangeDutyCycle(2.5*speed + 7.5)
        ESC2_M2_pwm.ChangeDutyCycle(7.5)
    elif direction == 'S':
        ESC2_M1_pwm.ChangeDutyCycle(-2.5*speed + 7.5)
        ESC2_M2_pwm.ChangeDutyCycle(7.5)
    elif direction == 'E':
        ESC1_M1_pwm.ChangeDutyCycle(2.5*speed + 7.5)
        ESC1_M2_pwm.ChangeDutyCycle(7.5)
    elif direction == 'W':
        ESC1_M1_pwm.ChangeDutyCycle(-2.5*speed + 7.5)
        ESC1_M2_pwm.ChangeDutyCycle(7.5)
    elif direction == 'X':
        ESC1_M1_pwm.ChangeDutyCycle(0)
        ESC1_M2_pwm.ChangeDutyCycle(0)
        ESC2_M1_pwm.ChangeDutyCycle(0)
        ESC2_M2_pwm.ChangeDutyCycle(0)

