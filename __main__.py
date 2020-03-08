import Globals as g
import pyttsx3
import multiprocessing
import importlib
import time
import Constant as c
import RPi.GPIO as GPIO

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
GPIO.add_event_detect(c.INDICATOR_UP, GPIO.RISING, callback=Test, bouncetime=c.BOUNCE_TIME)
GPIO.add_event_detect(c.INDICATOR_DOWN, GPIO.RISING, callback=Test, bouncetime=c.BOUNCE_TIME)

"""
engine = pyttsx3.init()
engine.setProperty('rate', 140)
engine.setProperty('voice', voices[49].id) #nederlands
engine.say("Hallo, dit is een test voor ons programma.")
engine.say("Dit is hoe deze library nederlands doet spreken")
engine.say("Ik weet niet zeker of dit goed genoeg is")
engine.runAndWait()
engine.stop()
"""

def Read_text(text):
    engine.say(text)
    engine.runAndWait()
    return

def Prepare_TTS(text):
    p = multiprocessing.Process(target = Read_text, args=(text,))
    p.start()

# w a i t F o r B r e a k ()
# ===========================
# Only leaves loop when next-button or reset-button input occurs
#
def waitForBreak():
    while True :
        time.sleep(0.01) #Precautionary: Don't know if this is needed, but thought is that this delay gives the interrupt time to change variable
        if (g.pressedNXT or g.pressedRST):
            break

#check whether this file is the file that is executed first
if __name__ == '__main__':


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
