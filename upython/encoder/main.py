from machine import Pin
import time
from speed_calc import SpeedCalculator
from simple_pid import SimplePID

A_PHASE = Pin(0, Pin.IN, Pin.PULL_UP) # White
B_PHASE = Pin(1, Pin.IN, Pin.PULL_UP) # Green
RESET =Pin(6, Pin.IN, Pin.PULL_UP)

STEPS = 400
STEPS_PER_CM = 170
TARGET_SPEED = 1.0
OFFSET_SPEED = 0.15
SAMPLE_TIME = 300 # ms wait to calculate the next speed
LOOP_TIME = 1 # waiting before recall the loop

pid = SimplePID(kp=0.5, ki=0.1, kd=0.01, dt=0.1)
speed_calc = SpeedCalculator(SAMPLE_TIME, STEPS_PER_CM)

flagA=0
flagB = 0
direction = 0
prev_r = 0
prev_position = 0
prev_speed = 0

def convert(var, input_min, input_max, output_min, output_max):
    ratio = (var - input_min) / (input_max - input_min)
    return output_min + ratio * (output_max - output_min)

def check_reset():
    global flagA, flagB, prev_r, position
    reset = RESET.value()
    if reset == 0 and reset!=prev_r:
        print("Position have been reset to 0.0")
        prev_r = reset
        flagA = 0
        flagB = 0
        position = calc_pos(flagA, flagB)
        client_osc.send("/position", position)
        client_osc2.send("/position", position)
    prev_r = reset

def check_speed(current_speed, target_speed, offset):
    min_speed=target_speed-offset
    max_speed=target_speed+offset
    return min_speed<=current_speed<=max_speed

def interrupt(pin):
    global flagA, flagB, lap, direction
    if B_PHASE.value() == 1:
        flagA += 1
        direction = "CW"
    else:
        direction = "CCW"
        flagB += 1
    # print (f'A:{flagA}\tB:{flagB}') # Check the flags
A_PHASE.irq(trigger=Pin.IRQ_RISING, handler=interrupt)

def calc_pos(flagA, flagB):
    net_steps = flagA-flagB
    position = net_steps/STEPS_PER_CM
    return round(position, 1)

while True:
    position = calc_pos(flagA, flagB)
    speed = convert(speed_calc.calc_speed(flagA, flagB), -6, 6, -2, 2)*3
    w_speed = check_speed(speed, TARGET_SPEED, OFFSET_SPEED)
    check_reset()

    if speed!=prev_speed:
        prev_speed = speed
        prev_position = position
        print(f'pos:{position}\tdirection:{direction}\tspeed:{speed}\t?target speed?:{w_speed}')
        client_osc.send("/speed", speed) # Send speed main loop to send the 0 speed
        client_osc.send("/position", int(position*10)) # to flask web server
        client_osc2.send("/position", position)

    time.sleep_ms(LOOP_TIME)
