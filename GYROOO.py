#!/usr/bin/python

import thread
import time
import smbus
import math
from socketIO_client import SocketIO, LoggingNamespace

# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect$

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

accelX = 0
accelY = 0
accelZ = 0
xRot = 0
yRot = 0

# GYROSCOPE! ##############################################

def read_byte(adr):
    global address
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

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

def gyroscope():
	while True:
		init_gyro()
		check_accelerometer()
		time.sleep(0.1)
##########################################################################
		
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
	
def get_status():
	while True:
		gyro_response()
		global gyroResponse
		socketIO.emit('DRONErequest', gyroResponse)
		socketIO.on('IOanswer', on_drone_server_response)
		socketIO.wait(seconds=0.1)
		print(data)
		global keymap
		keymap = data[0]
		keymapper(keymap)
		print('DIR: ' , left , right , forward , backward , 'ROT: ' , cClockwise , clockwise ,'ALT: ', up , down)
		time.sleep(0.1)
	
def motor_control():
	while True:
		print("proooom!")
		time.sleep(0.1)



# Create two threads as follows

init_gyro()
socketIO = SocketIO('http://avela.ddns.net', 3000, LoggingNamespace)
socketIO.emit('DRONErequest', 'boot')
socketIO.on('IOanswer', on_drone_server_response)
socketIO.wait(seconds=1)

	
try:
	thread.start_new_thread( get_status, () )
	thread.start_new_thread( motor_control, () )
	thread.start_new_thread( gyroscope, () )
except:
	print "Error: unable to start thread"

while True:
	pass
