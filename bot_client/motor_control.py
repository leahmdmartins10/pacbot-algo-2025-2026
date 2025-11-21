from setup import *

#dictionary to convert directions to TOF numbers
DIR_to_TOF = {
    'N': 0,
    'S': 1,
    'E': 2,
    'W': 3
}

#makes motors go forward
def motor_fwd(direction, speed=0.1):
    if direction != "X":
        print(f"Moving {direction} at {speed} speed")
    if direction == 'N':
        ESC2_M1_pwm.ChangeDutyCycle(2.5*speed + 7.5)
        ESC2_M2_pwm.ChangeDutyCycle(7)
        ESC1_M1_pwm.ChangeDutyCycle(0)
        ESC1_M2_pwm.ChangeDutyCycle(0)
    elif direction == 'S':
        ESC2_M1_pwm.ChangeDutyCycle(-2.5*speed + 7)
        ESC2_M2_pwm.ChangeDutyCycle(7)
        ESC1_M1_pwm.ChangeDutyCycle(0)
        ESC1_M2_pwm.ChangeDutyCycle(0)
    elif direction == 'E':
        ESC1_M1_pwm.ChangeDutyCycle(-2.5*speed + 7)
        ESC1_M2_pwm.ChangeDutyCycle(7)
        ESC2_M1_pwm.ChangeDutyCycle(0)
        ESC2_M2_pwm.ChangeDutyCycle(0)
    elif direction == 'W':
        ESC1_M1_pwm.ChangeDutyCycle(2.5*speed + 7.5)
        ESC1_M2_pwm.ChangeDutyCycle(7)
        ESC2_M1_pwm.ChangeDutyCycle(0)
        ESC2_M2_pwm.ChangeDutyCycle(0)
    elif direction == 'X':
        ESC1_M1_pwm.ChangeDutyCycle(0)
        ESC1_M2_pwm.ChangeDutyCycle(0)
        ESC2_M1_pwm.ChangeDutyCycle(0)
        ESC2_M2_pwm.ChangeDutyCycle(0)

#makes motors spin
def motor_spin(difference):
    if difference < 0:
        print("Rotating CW")
        ESC1_M1_pwm.ChangeDutyCycle(7)
        ESC1_M2_pwm.ChangeDutyCycle(7.75)
        ESC2_M1_pwm.ChangeDutyCycle(7)
        ESC2_M2_pwm.ChangeDutyCycle(7.75)
    else:
        print("Rotating CCW")
        ESC1_M1_pwm.ChangeDutyCycle(7)
        ESC1_M2_pwm.ChangeDutyCycle(7.25)
        ESC2_M1_pwm.ChangeDutyCycle(7)
        ESC2_M2_pwm.ChangeDutyCycle(7.25)

#returns distance from a particular TOF sensor
def get_distance(direction):
    global prev_direction, TOF
    if prev_direction != direction:
        tcaselect(DIR_to_TOF[direction])
        prev_direction = direction
    TOF = adafruit_vl53l0x.VL53L0X(i2c)
    return TOF.range

#returns how much safe space is left
def get_free_space(direction):
    distance = get_distance(direction)
    return distance - min_distance

#moves robot until distance is not safe
def move_robot(direction):
    # check_orientation(target_orientation)
    if(get_free_space(direction) > safe_distance):
        motor_fwd(direction, motor_speed)
    # elif (get_free_space(direction) > 0):
    #     motor_fwd(direction, get_free_space(direction)/safe_distance)
    else:    
        motor_fwd('X', 0)

#set target orientation
def set_orientation():
    input("Press Enter to set target orientation")
    target_orientation = IMU.get_bearing_raw()

#rotate robot w imu if needed
def check_orientation(target):
    try:
        diff = target - IMU.get_bearing_raw()
        while abs(diff) > 0.05 * target:
            motor_spin(diff)
            diff = target - IMU.get_bearing_raw()
        return True
    except OSError as e:
                    print(f"Error reading sensor data: {e}")
                