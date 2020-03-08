from Dicts import *

buttonState = [0,0,0,0,0,0]
binInput = 0
lastBinInput = 0
pressedRST = False
pressedNXT = False
waitingForCellInput = False

#Global callbacks to call when buttons are pressed

def callback0(channel):
    global binInput
    global buttonState
    if buttonState[0] == 0:
        binInput += 1
        buttonState[0] = 1
    print(buttonState)

def callback1(channel):
    global binInput
    global buttonState
    if buttonState[1] == 0:
        binInput += 2
        buttonState[1] = 1
    print(buttonState)

def callback2(channel):
    global binInput
    global buttonState
    if buttonState[2] == 0:
        binInput += 4
        buttonState[2] = 1
    print(buttonState)

def callback3(channel):
    global binInput
    global buttonState
    if buttonState[3] == 0:
        binInput += 8
        buttonState[3] = 1
    print(buttonState)

def callback4(channel):
    global binInput
    global buttonState
    if buttonState[4] == 0:
        binInput += 16
        buttonState[4] = 1
    print(buttonState)

def callback5(channel):
    global binInput
    global buttonState
    if buttonState[5] == 0:
        binInput += 32
        buttonState[5] = 1
    print(buttonState)

def callbackRST(channel):
    global binInput
    global buttonState
    global pressedRST
    buttonState = [0,0,0,0,0,0]
    binInput = 0
    pressedRST = True

def callbackNXT(channel):
    global binInput
    global buttonState
    global pressedNXT
    global lastBinInput
    lastBinInput = binInput
    buttonState = [0,0,0,0,0,0]
    binInput = 0
    pressedNXT = True
        