#!/usr/bin/python

import thread
import time
import smbus
import math
import pigpio
import subprocess #tarvihkoo ollenkaan? varmista
import netifaces as ni # To receive host IP
from socketIO_client import SocketIO, LoggingNamespace
# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect$
drone = pigpio.pi()

data = '00000000'
left = '0'
right = '0'
forward = '0'
backward = '0'
cClockwise = '0'
clockwise = '0'
up = '0'
down = '0'
keymap = '00000000'
gyroResponse = ''

#Gyro variables
accelX = 0
accelY = 0
accelZ = 0
xRot = 0
yRot = 0

#Motor variables
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

# GYROSCOPE! ##############################################

def read_byte(adr):
    global address
    return bus.read_byte_data(address, adr)

def read_word(adr):
    try:
    	global address
    	high = bus.read_byte_data(address, adr)
    	time.sleep(0.01)
    	low = bus.read_byte_data(address, adr+1)
    	time.sleep(0.01)
    	val = (high << 8) + low
	return val

    except IOError:
	print "GYRO ERROR, ADDRESS " ,adr
	return 0


def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

def init_gyro():
# Now wake the 6050 up as it starts in sleep mode
	bus.write_byte_data(address, power_mgmt_1, 0)

def check_gyro():	
	gyro_xout = read_word_2c(0x43)
	gyro_yout = read_word_2c(0x45)
	gyro_zout = read_word_2c(0x47)
	#return('gyro_xout':gyro_xout / 131, 'gyro_yout':gyro_yout / 131, 'gyro_zout':gyro_zout / 131)

def check_accelerometer():	
	accel_xout = read_word_2c(0x3b)
	time.sleep(0.001)
	accel_yout = read_word_2c(0x3d)
	time.sleep(0.001)
	accel_zout = read_word_2c(0x3f)
	time.sleep(0.001)	

	global accelX
	accelX = accel_xout / 16384.0
	accel_xout_scaled = accel_xout / 16384.0
	global accelY
	accelY = accel_yout / 16384.0
	accel_yout_scaled = accel_yout / 16384.0
	global accelZ
	accelZ = accel_zout / 16384.0
	accel_zout_scaled = accel_zout / 16384.0
	global yRot
	yRot = get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
	x_rotation = get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
	global xRot
	xRot = get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
	y_rotation = get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
	
	#return('accel_xout':accel_xout, 'accel_xout_scaled':accel_xout_scaled, 'accel_yout':accel_yout, 'accel_yout_scaled':accel_yout_scaled, 'accel_zout':accel_zout, 'accel_zout_scaled':accel_zout_scaled, 'x_rotation':x_rotation, 'y_rotation':y_rotation)

def gyro_response():
	global xRot
	str(xRot)
	global yRot
	str(yRot)
	global accelZ
	str(accelZ)
	global gyroResponse
	gyroResponse = xRot , yRot, accelZ


##########################################################################
	
	
# MOTOR FUNCTIONS #######################################################
def motor_init():
	global motor1_pulsewidth
	global motor2_pulsewidth
	global motor3_pulsewidth
	global motor4_pulsewidth
	motor1_pulsewidth = 1000
	motor2_pulsewidth = 1000
	motor3_pulsewidth = 1000
	motor4_pulsewidth = 1000
	drone.set_servo_pulsewidth(MOTOR1, 1000)
	drone.set_servo_pulsewidth(MOTOR2, 1000)
	drone.set_servo_pulsewidth(MOTOR3, 1000)
	drone.set_servo_pulsewidth(MOTOR4, 1000)

def motorcontrol(m1, m2, m3, m4):
	global motor1_pulsewidth
	global motor2_pulsewidth
	global motor3_pulsewidth
	global motor4_pulsewidth
	motor1_pulsewidth = motor1_pulsewidth + m1
	motor2_pulsewidth = motor2_pulsewidth + m2
	motor3_pulsewidth = motor3_pulsewidth + m3
	motor4_pulsewidth = motor4_pulsewidth + m4
	if motor1_pulsewidth <= 2000 | motor1_pulsewidth >= 1000:
		drone.set_servo_pulsewidth(MOTOR1, motor1_pulsewidth)
	if motor2_pulsewidth <= 2000 | motor2_pulsewidth >= 1000:
		drone.set_servo_pulsewidth(MOTOR2, motor2_pulsewidth)
	if motor3_pulsewidth <= 2000 | motor3_pulsewidth >= 1000:
		drone.set_servo_pulsewidth(MOTOR3, motor3_pulsewidth)
	if motor4_pulsewidth <= 2000 | motor4_pulsewidth >= 1000:
		drone.set_servo_pulsewidth(MOTOR4, motor4_pulsewidth)
		

#########################################################################	
def set_global(args):
	global data
	data = args

def on_drone_server_response(*args):
	set_global(args)
	
def keymapper(args):
	global left
	left = keymap[0]
	global right
	right = keymap[1]
	global forward
	forward = keymap[2]
	global backward
	backward = keymap[3]
	global cClockwise
	cClockwise = keymap[4]
	global clockwise
	clockwise = keymap[5]
	global up
	up = keymap[6]
	global down
	down = keymap[7]

# THREADS ##############################################################

#Communication thread, sends gyro information, receives control commands, assigns commands to global variables	
def get_status():
	while True:
		global gyroresponce
		socketIO.emit('DRONErequest', gyroResponse)
		socketIO.on('IOanswer', on_drone_server_response)
		socketIO.wait(seconds=0.15)
#		print(data)
		global keymap
		keymap = data[0].encode('ascii')
		keymapper(keymap)
#		print('DIR: ' , left , right , forward , backward , 'ROT: ' , cClockwise , clockwise ,'ALT: ', up , down)
		time.sleep(0.05)
	
#Motor control thread, Reads the global control variables, Changes the wanted "0" angle variable	
def motor_control():
	global up
	global down
	motor_init()
	while True:
		if up == '1':
			motorcontrol(10,10,10,10)
		if down == '1':
			motorcontrol(-10,-10,-10,-10)

		
		time.sleep(0.1)

#Gyroscope thread, reads the gyroscope angles 
def gyroscope():
	while True:
		check_accelerometer()
		time.sleep(0.1)
		gyro_response()
		time.sleep(0.001)

########################################################################

#INITIALIZATION ########################################################

ni.ifaddresses('eth0')
drone_ip = ni.ifaddresses('eth0')[2][0]['addr']
print drone_ip  # should print your IP

init_gyro()
time.sleep(0.01)
  															#Initializes the gyroscope
socketIO = SocketIO('http://avela.ddns.net', 3000, LoggingNamespace)	#Initializes the connection to avela.ddns.net
socketIO.emit('DRONErequest', drone_ip)
socketIO.on('IOanswer', on_drone_server_response)
socketIO.wait(seconds=1)

#Creates the threads, Prints error if failure on creating the threads
try:
	thread.start_new_thread( get_status, () )
	thread.start_new_thread( motor_control, () )
	thread.start_new_thread( gyroscope, () )
except:
	print "Error: unable to start thread"

while True:
	pass
