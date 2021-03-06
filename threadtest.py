#!/usr/bin/python

import thread
import time
from socketIO_client import SocketIO, LoggingNamespace

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

#GYROSCOPE!






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
		socketIO.emit('DRONErequest', 'request data')
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


socketIO = SocketIO('http://avela.ddns.net', 3000, LoggingNamespace)
socketIO.emit('DRONErequest', 'boot')
socketIO.on('IOanswer', on_drone_server_response)
socketIO.wait(seconds=1)
	
try:
	thread.start_new_thread( get_status, () )
	thread.start_new_thread( motor_control, () )
except:
	print "Error: unable to start thread"

while True:
	pass
