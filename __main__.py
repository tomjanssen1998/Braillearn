import Globals as g
import pyttsx3
import multiprocessing
import importlib
import time
import Constant as c
import RPi.GPIO as GPIO

global engine # Engine used for TTS


# m a i n ()
# ===========================
# Main function
#
def main():
    initializeGPIO()
    initializeTTS()
    
    #Dynamically load tasks when switching levels
    tasks = importlib.import_module("Tasks.Task1")

    #loop through letters of quiz one by one
    for letter in tasks.quiz:
        print("write the symbol for '" + letter + "': " + str(g.T2B[letter]))
        #string = "write the symbol for: " + letter
        
        #Read the task out loud
        #Prepare_TTS(string)

        waitForBreak() # Wait for user inputs
        
        if g.pressedNXT:
                g.pressedNXT = False
                if g.lastBinInput == g.T2B[letter]: # Check if answer is correct
                    print("Correct!")
                    #break
                else:
                    print("Incorrect")

        if g.pressedRST:
                g.pressedRST = False


   

# w a i t F o r B r e a k ()
# ===============================
# Only leaves loop when next-button or reset-button input occurs
#
def waitForBreak():
    while True :
        time.sleep(0.01) #Precautionary: Don't know if this is needed, but thought is that this delay gives the interrupt time to change variable
        if (g.pressedNXT or g.pressedRST):
            break

# i n i t i a l i z e T T S ()
# ===============================
# initialize text-to-speech library
#
def initializeTTS():
    global engine # So that we use the global 'engine' variable instead of creating a local one
    engine = pyttsx3.init()
    engine.setProperty('rate', 140)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[49].id)

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
    engine.say(text) # Since we are not modifying 'engine' here but reading it, we don't need to put 'global engine' inside the method
    engine.runAndWait()
    return

# p r e p a r e T T S (text)
# ===============================
# Creates a thread which runs the 'readText(text)' method with text given as input
#
def prepareTTS(text):
    p = multiprocessing.Process(target = readText, args=(text,))
    p.start()

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
