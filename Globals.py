from Dicts import *

buttonState = [0,0,0,0,0,0]
binInput = 0
lastBinInput = 0
RST = False
NXT = False

#Global callbacks to call when buttons are pressed

def callback0(channel):
	global binInput
	global buttonState
	if buttonState[0] == 0:
		binInput += 1
		buttonState[0] = 1

def callback1(channel):
	global binInput
	global buttonState
	if buttonState[1] == 0:
		binInput += 2
		buttonState[1] = 1

def callback2(channel):
	global binInput
	global buttonState
	if buttonState[2] == 0:
		binInput += 4
		buttonState[2] = 1

def callback3(channel):
	global binInput
	global buttonState
	if buttonState[3] == 0:
		binInput += 8
		buttonState[3] = 1

def callback4(channel):
	global binInput
	global buttonState
	if buttonState[4] == 0:
		binInput += 16
		buttonState[4] = 1

def callback5(channel):
	global binInput
	global buttonState
	if buttonState[5] == 0:
		binInput += 32
		buttonState[5] = 1

def callbackRST(channel):
	global binInput
	global buttonState
	global RST
	buttonState = [0,0,0,0,0,0]
	binInput = 0
	RST = True

def callbackNXT(channel):
	global binInput
	global buttonState
	global NXT
	global lastBinInput
	lastBinInput = binInput
	buttonState = [0,0,0,0,0,0]
	binInput = 0
	NXT = True
