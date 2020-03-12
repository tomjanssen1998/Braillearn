import Globals as g
import pyttsx3
import multiprocessing
import importlib
import time
import Constant as c
import RPi.GPIO as GPIO
from pygame import mixer #for playing mp3 sounds
from random import randrange

# m a i n ()
# ===========================
# Main function
#
def main():
    initializeAudio()
    initializeGPIO()
    #initializeTTS()
    
    runTutorial()
    
    #Dynamically load tasks when switching levels
    tasks = importlib.import_module("Tasks.Task1")

    #loop through letters of quiz one by one
    for letter in tasks.quiz:
        print("write the symbol for '" + letter + "': " + str(g.T2B[letter]))
        string = "write the symbol for: " + letter
        
        #Read the task out loud
        #prepareTTS(string)

        waitForBreak() # Wait for user inputs
        
        if g.checkState('NXT'):
                g.setState('NXT', False)
                if g.lastBinInput == g.T2B[letter]: # Check if answer is correct
                    print("Correct!")
                    #break
                else:
                    print("Incorrect")

        if g.checkState('RST'):
                g.setState('RST', False)


# i n i t i a l i z e A u d i o ():
# ===============================
# intialize mixer for playing audio
#
def initializeAudio():
    mixer.init(44100, -16, 2, 10240) # make this last one (buffer size) bigger if underrun error occurs
    mixer.music.set_volume(c.AUDIO_VOLUME)

# p l a y A u d i o (audio_name):
# ===============================
# plays audio file (mp3) referred to by audio_name
# position refers to position of the audio file where we start playing (seconds)
#
def playAudio(audio_name, position):
    if (audio_name == 'Incorrect' or audio_name == 'Correct'):
        r = randrange(2)
        if (r == 0):
            to_load = 'Sounds/' + audio_name + '1.mp3'
        else:
            to_load = 'Sounds/' + audio_name + '2.mp3'
    else:
        to_load = 'Sounds/' + audio_name + '.mp3'
    
    g.currentAudio = audio_name # currently playing audio
    mixer.music.load(to_load)
    mixer.music.play(0, position) # 0 indicates it plays 1 time
    print("playing: " + audio_name + " at pos: " + str(mixer.music.get_pos()))

# s t o p A u d i o ():
# ===============================
# Stops currently playing audio (if something is playing)
#
def stopAudio():
    if (mixer.music.get_busy() == True):
        mixer.music.stop() # Stop audio

# p a u s e A u d i o ()
# ===============================
# Pauses currently playing audio to be able to play another audio file

def pauseAudio():
    g.pausedAudio = ''
    if (mixer.music.get_busy() == True):
        g.pausedAudio = g.currentAudio
        mixer.music.pause()
        g.pausedPosition += float(mixer.music.get_pos() / 1000) # float division: convert milliseconds to seconds
        print("paused: audio: " + str(g.pausedAudio) + " position: " + str(g.pausedPosition))
        mixer.music.stop() # Stop audio
        
# u n p a u s e A u d i o ()
# ===============================
# Resumes previously playing audio at current position

def unpauseAudio():
    stopAudio() # Only stops audio if something is playing
    
    if (g.pausedAudio != ''): # Only resume if there was something playing before the pause
        playAudio(g.pausedAudio, g.pausedPosition)
    

# r u n T u t o r i a l ()
# ===============================
# run through tutorial of Braillearn
#
def runTutorial():
    
    g.globalState = -1 # Tutorial part 1
    playAudio('Tutorial1', 0)
    
    waitForTutorial()
    time.sleep(c.TUTORIAL_SLEEP_TIME1)
    
    g.globalState = -2 # Tutorial part 2
    playAudio('Tutorial2', 0)
        
    skipped = waitForTutorial()    
    if (not skipped):
        time.sleep(c.TUTORIAL_SLEEP_TIME1)
        waitForPress('RST')
        time.sleep(c.TUTORIAL_SLEEP_TIME2)
        waitForPress('NXT')
        time.sleep(c.TUTORIAL_SLEEP_TIME2)
        waitForPress('LVLUP')
        time.sleep(c.TUTORIAL_SLEEP_TIME2)
        waitForPress('LVLDOWN')
    
    g.globalState = -3 # Tutorial part 3
    time.sleep(c.TUTORIAL_SLEEP_TIME1)
    playAudio('Tutorial3', 0)
    
    while True:
        time.sleep(0.01)
        if(g.checkState('RST')):
            g.resetButtonStates()
            stopAudio()
            runTutorial()
        elif(g.checkState('NXT')):
            g.resetButtonStates()
            stopAudio()
            break   
        elif(g.checkState('LVLUP')):
            g.resetButtonStates()
            stopAudio()
            break
            #ToDo: Handle level modes
        elif(g.checkState('LVLDOWN')):
            g.resetButtonStates()
            stopAudio()
            break
            #ToDo: Handle level modes
        
    print("done")    

# w a i t F o r P r e s s ()
# ===============================
# Waits for the user to press a certain button
#
def waitForPress(button_name):
    g.resetButtonStates()
    g.pausedPosition = 0.0 # Reset pause position variable
    
    playAudio('Tutorial' + button_name, 0)
    
    is_pressed = g.checkState(button_name)
    while (not is_pressed):
        if (g.numberOfPresses() > 0):
            
            print("Incorrect button pressed")
            pauseAudio() # Pause currently playing
            
            playAudio('Incorrect', 0)
            waitForAudio()
            
            unpauseAudio() # Resume currently playing
            g.resetButtonStates()
        
        time.sleep(0.01)
        is_pressed = g.checkState(button_name)
    
    stopAudio() # when user has pressed target button, we can stop button-specific instruction
    
    print("Correct button pressed")
    playAudio('Correct', 0)
    waitForAudio()
    
    g.setState(button_name, False)
        
    
# w a i t F o r A u d i o ()
# ===============================
# Waits for current audio file to finish
#
def waitForAudio():
    is_playing = True
    while (is_playing) :
        time.sleep(0.01)
        is_playing = mixer.music.get_busy()
    

# w a i t F o r T u t o r i a l ()
# ===============================
# Remains in loop until current audio file has finished playing or next button has been pressed
# Returns True if skip button was pressed, False otherwise
#
def waitForTutorial():
    is_playing = True
    while (is_playing) :
        time.sleep(0.01)
        is_playing = mixer.music.get_busy()
        if (g.checkState('NXT')):
            g.setState('NXT', False)
            stopAudio()
            return True
    return False
    

# w a i t F o r B r e a k ()
# ===============================
# Only leaves loop when next-button or reset-button input occurs
#
def waitForBreak():
    g.resetButtonStates()
    
    while True :
        time.sleep(0.01) #Precautionary: Don't know if this is needed, but thought is that this delay gives the interrupt time to change variable
        if (g.checkState('NXT') or g.checkState('RST')):
            break

# i n i t i a l i z e T T S ()
# ===============================
# initialize text-to-speech library
#
def initializeTTS():
    #global engine # So that we use the global 'engine' variable instead of creating a local one
    engine = pyttsx3.init()
    engine.setProperty('rate', 140)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[11].id)

    # === Voices ===
    # 10 = default
    # 11 = english
    # 16 = english-us
    # 49 = Nederlands

# r e a d T e x t (text)
# ===============================
# uses text-to-speech to read out the text given as input
#
def readText(text):
    print("Start reading")
    ab = pyttsx3.init()
    ab.setProperty('rate', 140)
    voices = ab.getProperty('voices')
    ab.setProperty('voice', voices[11].id)
    ab.say("this") # Since we are not modifying 'engine' here but reading it, we don't need to put 'global engine' inside the method
    ab.say("is")
    ab.say("a")
    ab.say("test")
    ab.say("Welcome to Braillearn this is a cool program that let's you learn braille without difficulties. To start learning press the next button") 
    ab.runAndWait()
    print("Finished reading")
    return

# p r e p a r e T T S (text)
# ===============================
# Creates a thread which runs the 'readText(text)' method with text given as input
#
def prepareTTS(text):
    global voice_thread 
    voice_thread = multiprocessing.Process(target = readText, args=(text,))
    voice_thread.start()

# i n i t i a l i z e G P I O ()
# ===============================
# initialize all GPIO pins used
#
def initializeGPIO():
    GPIO.setmode(GPIO.BCM) #referring to the pins by the "Broadcom SOC channel" numbers

    # Input braille cell
    GPIO.setup(c.BRAILLE_P1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Braille part 1
    GPIO.setup(c.BRAILLE_P2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Braille part 2
    GPIO.setup(c.BRAILLE_P3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Braille part 3
    GPIO.setup(c.BRAILLE_P4_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Braille part 4
    GPIO.setup(c.BRAILLE_P5_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Braille part 5
    GPIO.setup(c.BRAILLE_P6_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Braille part 6

    # Control buttons
    GPIO.setup(c.NEXT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Next button
    GPIO.setup(c.RESET_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Reset button
    GPIO.setup(c.INDICATOR_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Level indicator up
    GPIO.setup(c.INDICATOR_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Level indicator down

    # Setup callbacks
    GPIO.add_event_detect(c.BRAILLE_P1_PIN, GPIO.RISING, callback=g.callback0, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.BRAILLE_P2_PIN, GPIO.RISING, callback=g.callback1, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.BRAILLE_P3_PIN, GPIO.RISING, callback=g.callback2, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.BRAILLE_P4_PIN, GPIO.RISING, callback=g.callback3, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.BRAILLE_P5_PIN, GPIO.RISING, callback=g.callback4, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.BRAILLE_P6_PIN, GPIO.RISING, callback=g.callback5, bouncetime=c.BOUNCE_TIME)

    GPIO.add_event_detect(c.NEXT_PIN, GPIO.RISING, callback=g.callbackNXT, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.RESET_PIN, GPIO.RISING, callback=g.callbackRST, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.INDICATOR_UP, GPIO.RISING, callback=g.callbackLVLUP, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.INDICATOR_DOWN, GPIO.RISING, callback=g.callbackLVLDOWN, bouncetime=c.BOUNCE_TIME)    


                
# Check whether this file is the file that is executed first
# This part should be at the bottom to ensure all called methods are defined before calling them
if __name__ == '__main__':
    main() 
