from Dicts import *

# Global states:
# -3 = Tutorial part 3
# -2 = Tutorial part 2
# -1 = Tutorial part 1
#  0 = Default
#  1 = Game mode 1
#  To be continued
globalState = 0
currentAudio = ''
pausedAudio = ''
pausedPosition = 0.0 # At what position of audio do we pause

buttonState = [0,0,0,0] # In order: [RST, NXT, LVLUP, LVLDOWN]
brailleState = [0,0,0,0,0,0]
binInput = 0
lastBinInput = 0

#Global callbacks to call when buttons are pressed

def callback0(channel):
    global binInput
    global brailleState
    if brailleState[0] == 0:
        binInput += 1
        brailleState[0] = 1
    print(brailleState)

def callback1(channel):
    global binInput
    global brailleState
    if brailleState[1] == 0:
        binInput += 2
        brailleState[1] = 1
    print(brailleState)

def callback2(channel):
    global binInput
    global brailleState
    if brailleState[2] == 0:
        binInput += 4
        brailleState[2] = 1
    print(brailleState)

def callback3(channel):
    global binInput
    global brailleState
    if brailleState[3] == 0:
        binInput += 8
        brailleState[3] = 1
    print(brailleState)

def callback4(channel):
    global binInput
    global brailleState
    if brailleState[4] == 0:
        binInput += 16
        brailleState[4] = 1
    print(brailleState)

def callback5(channel):
    global binInput
    global brailleState
    if brailleState[5] == 0:
        binInput += 32
        brailleState[5] = 1
    print(brailleState)

def callbackRST(channel):
    global binInput
    global brailleState
    global buttonState
    brailleState = [0,0,0,0,0,0]
    binInput = 0
    buttonState[0] = 1

def callbackNXT(channel):
    global binInput
    global brailleState
    global lastBinInput
    global buttonState
    lastBinInput = binInput
    brailleState = [0,0,0,0,0,0]
    binInput = 0
    buttonState[1] = 1
        
def callbackLVLUP(channel):
    global buttonState
    buttonState[2] = 1

def callbackLVLDOWN(channel):
    global buttonState
    buttonState[3] = 1

# c h e c k S t a t e (button_name)
# ===============================
# Returns state of button 'button_name'
#
def checkState(button_name):
    state = False
    
    if (button_name == 'RST'):
       state = buttonState[0]
    elif (button_name == 'NXT'):
        state = buttonState[1]
    elif (button_name == 'LVLUP'):
        state = buttonState[2]
    elif (button_name == 'LVLDOWN'):
        state = buttonState[3]
        
    return state

# s e t S t a t e (button_name)
# ===============================
# Returns state of button 'button_name'
#
def setState(button_name, state):
    global buttonState
    
    if (button_name == 'RST'):
       buttonState[0] = state
    elif (button_name == 'NXT'):
        buttonState[1] = state 
    elif (button_name == 'LVLUP'):
        buttonState[2] = state 
    elif (button_name == 'LVLDOWN'):
        buttonState[3] = state
        
# n u m b e r O f P r e s s e s ()
# ===============================
# Returns number of buttons which have been pressed (and not reset)
#
def numberOfPresses():
    presses = 0
    for i in buttonState:
        if (i == True):
            presses += 1
    return presses

# r e s e t B u t t o n S t a t e s ()
# ===============================
# Resets all button states to 0
#
def resetButtonStates():
    global buttonState
    buttonState = [0,0,0,0]