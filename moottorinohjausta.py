#!/usr/bin/env python

# servo_key.py
# 21-12-2015
# Miika Avela

import time
import curses
import atexit
import smbus

import pigpio 

drone = pigpio.pi()

MOTOR1 = 4					# Pin07 GPIO 04
MOTOR2 = 17					# Pin11 GPIO 17
MOTOR3 = 27					# Pin13	GPIO 27
MOTOR4 = 22					# Pin15 GPIO 22

motor1_pulsewidth = 0
motor2_pulsewidth = 0
motor3_pulsewidth = 0
motor4_pulsewidth = 0

MIN_PW = 1000
MAX_PW = 2000


def motorcontrol(m1, m2, m3, m4):
	drone.set_servo_pulsewidth(MOTOR1, motor1_pulsewidth += m1)
	drone.set_servo_pulsewidth(MOTOR2, motor2_pulsewidth += m2)
	drone.set_servo_pulsewidth(MOTOR3, motor3_pulsewidth += m3)
	drone.set_servo_pulsewidth(MOTOR4, motor4_pulsewidth += m4)


   

pulsewidth = MIN_PW

pi.set_servo_pulsewidth(SERVO, pulsewidth)


while True:
	time.sleep(0.01)
		// Gyro
	motorcontrol(ASD,ASD,ASD,ASD)
	  
	  
	  
