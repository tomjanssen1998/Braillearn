import Globals as g
import pyttsx3
import multiprocessing
import importlib
import time
import Constant as c
import RPi.GPIO as GPIO
from pygame import mixer #for playing mp3 sounds
#   randrange
import random 
# m a i n ()
# ===========================
# Main function
#
def main():
    initializeAudio()
    print('Done initializing audio')
    initializeGPIO()
    print('Done initializing GPIO')
    #initializeTTS()
    
    runTutorial()
    
    taskFile = 'Tasks.Task1'
    
    #Infinite loop: only stop main program when RPi is shut down
    while True:
        #Dynamically load tasks when switching levels
        tasks = importlib.import_module(taskFile)
        abort = False
        
        #Randomize order of quiz if desired
        quiz = tasks.quiz.copy()
        if tasks.randomizeOrder:
            random.shuffle(quiz)

        print(quiz)

        #loop though question of quiz
        for question in quiz:
            answer = []

            if abort:       #Stop current quiz (to go to different level)
                break

            #Ask question to user
            if tasks.quizMode < 3: #If the quiz is for single letters:
                string = "Please write the letter: " + question
            else:
                string = "Please write the word: " + question
                
            #Prepare_TTS(string)
            print(string)

            #loop through letters of question one by one
            for count, letter in enumerate(question):
                
                if abort:   #Stop current quiz (to go to different level)
                    break
                
                completed = False
                
                while not completed:
                    if tasks.readEveryLetter:
                        string = "The next letter is: " + letter
                        print(string + "': " + str(g.T2B[letter]))
                        #Prepare_TTS(string)
                    else:
                        print(letter + ' : ' + str(g.T2B[letter])) #For testing purposes only

                    #Display requested letter if required
                    if tasks.quizMode == 1 or tasks.quizMode == 3:
                        print("Activating read braille cell") #For debugging purposes
                        #actuate braille read cell
                        out_val = g.T2B[letter]
                        for dot in range(5,-1,-1):
                            if out_val >= 2**dot:
                                out_val -= 2**dot
                                #activate braille dot 'dot'

                        

                    waitForBreak() # Wait for user inputs
                    
                    for dot in range(0,6):
                        #deactivate braille dot 'dot'
                        pass

                    if g.checkBtnState('LVLUP'):
                        g.resetBtnStates()
                        if g.task < g.taskCount:
                            g.task += 1
                            taskFile = 'Tasks.Task' + str(g.task)
                            abort = True
                            print('Moving to task ' + str(g.task))
                            break
                    
                    if g.checkBtnState('LVLDOWN'):
                        g.resetBtnStates()
                        if g.task > 1:
                            g.task -= 1
                            taskFile = 'Tasks.Task' + str(g.task)
                            abort = True
                            print('Moving to task ' + str(g.task))
                            break
                            
                    if g.checkBtnState('NXT'):
                        g.resetBtnStates()
                        if g.lastBinInput != 0:
                            try:
                                answer[count] = g.B2T[g.lastBinInput]
                            except:
                                try:
                                    answer.append(g.B2T[g.lastBinInput])
                                except:
                                    pass
                            print("Answer: " + str(answer))
                            
                            if tasks.feedbackPerLetter:
                                if g.lastBinInput == g.T2B[letter]: # Check if answer is correct
                                    print("Letter correct!")
                                    completed = True
                                else:
                                    print("Incorrect")
                                    if tasks.repeatUntilCorrect:
                                        if tasks.repeatImmediately:
                                            completed = False
                                        else:
                                            question.append(letter)
                                            completed = True
                                    else:
                                        completed = True
                            else:
                                completed = True
                        else:
                            completed = False

                    if g.checkBtnState('RST'):
                        g.resetBtnStates()


            if not tasks.feedbackPerLetter:
                answer = ''.join(answer)
                if question == answer:
                    print("Question answered correctly!")
                elif tasks.repeatUntilCorrect:
                    if tasks.repeatImmediately:
                        print("That is incorrect, try again!")
                        quiz.insert(question,count+1)
                    else:
                        print("That is incorrect, try again later!")
                        quiz.append(question)
                else:
                    print("That is incorrect!")
            else:
                print('Word done!')
        print('Level complete!')


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
    if (audio_name == 'Incorrect' or audio_name == 'Correct' or audio_name == 'Correct_Short'):
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
    
    g.globalState = -1 # Tutorial part 1 - Introduction
    playAudio('Tutorial1', 0)
    
    waitForTutorial()
    
    time.sleep(c.TUTORIAL_SLEEP_TIME1)
    g.globalState = -2 # Tutorial part 2 - Buttons
    playAudio('Tutorial2', 0)
        
    skipped = waitForTutorial()    
    if (not skipped):
        time.sleep(c.TUTORIAL_SLEEP_TIME1)
        waitForBtnPress('RST')
        time.sleep(c.TUTORIAL_SLEEP_TIME2)
        waitForBtnPress('NXT')
        time.sleep(c.TUTORIAL_SLEEP_TIME2)
        waitForBtnPress('LVLUP')
        time.sleep(c.TUTORIAL_SLEEP_TIME2)
        waitForBtnPress('LVLDOWN')
    
    time.sleep(c.TUTORIAL_SLEEP_TIME1)
    g.globalState = -3 # Tutorial part 3 - Braille inputs
    playAudio('Tutorial3-1', 0)
    
    skipped = waitForTutorial()
    if (not skipped):
        time.sleep(c.TUTORIAL_SLEEP_TIME1)
        waitForAllBraille()

    time.sleep(c.TUTORIAL_SLEEP_TIME1)
    playAudio('Tutorial3-2', 0)
    
    waitForTutorial()

    time.sleep(c.TUTORIAL_SLEEP_TIME1)
    g.globalState = -4 # Tutorial part 4 - Concluding
    playAudio('Tutorial4', 0)
    
    while True:
        time.sleep(0.01)
        if(g.checkBtnState('RST')):
            g.resetBtnStates()
            stopAudio()
            runTutorial()
        elif(g.checkBtnState('NXT')):
            g.resetBtnStates()
            stopAudio()
            break   
        elif(g.checkBtnState('LVLUP')):
            g.resetBtnStates()
            stopAudio()
            break
            #ToDo: Handle level modes
        elif(g.checkBtnState('LVLDOWN')):
            g.resetBtnStates()
            stopAudio()
            break
            #ToDo: Handle level modes
        
    print("done")

# w a i t F o r A l l B r a i l l e()
# ===============================
# Waits for all braille inputs to be pushed down
#
def waitForAllBraille():
    # ToDo: Set all braille input pins in up position
    g.pausedPosition = 0.0 # Reset pause position variable
    
    playAudio('TutorialBRAILLE', 0)
    prevInput = currInput = 0
    
    while True:

        time.sleep(0.01)
        currInput = g.binInput
        
        if (currInput == g.T2B['all']): # all braille pins are down
            break
        
        if (prevInput != currInput): # braille pin was pressed but not yet all pins are down
            prevInput = currInput
            pauseAudio()
            
            playAudio('Correct_Short', 0)
            waitForAudio()
            
            unpauseAudio()
    
    stopAudio() # when user has pressed target button, we can stop button-specific instruction
    
    g.brailleState = [0,0,0,0,0,0] # reset Braille input
    g.binInput = 0
    g.lastBinInput = 0
    
    print("All braille cells pressed")
    playAudio('Correct', 0)
    waitForAudio()

        

# w a i t F o r B t n P r e s s ()
# ===============================
# Waits for the user to press a certain button
#
def waitForBtnPress(button_name):
    g.resetBtnStates()
    g.pausedPosition = 0.0 # Reset pause position variable
    
    playAudio('Tutorial' + button_name, 0)
    
    is_pressed = g.checkBtnState(button_name)
    while (not is_pressed):
        if (g.numberOfBtnPresses() > 0):
            
            print("Incorrect button pressed")
            pauseAudio() # Pause currently playing
            
            playAudio('Incorrect', 0)
            waitForAudio()
            
            unpauseAudio() # Resume currently playing
            g.resetBtnStates()
        
        time.sleep(0.01)
        is_pressed = g.checkBtnState(button_name)
    
    stopAudio() # when user has pressed target button, we can stop button-specific instruction
    
    print("Correct button pressed")
    playAudio('Correct', 0)
    waitForAudio()
    
    g.setBtnState(button_name, False)
        
    
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
        if (g.checkBtnState('NXT')):
            g.setBtnState('NXT', False)
            stopAudio()
            return True
    return False
    

# w a i t F o r B r e a k ()
# ===============================
# Only leaves loop when next-button or reset-button input occurs
#
def waitForBreak():
    g.resetBtnStates()
    
    while True :
        time.sleep(0.01) #Precautionary: Don't know if this is needed, but thought is that this delay gives the interrupt time to change variable
        if (g.checkBtnState('NXT') or g.checkBtnState('RST')):
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
    
    #For Raspberry Pi 3B:
    #GPIO.setmode(GPIO.BOARD)
    
    # Input braille cell
    for pin in range(len(c.BRAILLE_INPUT_PIN)):
        GPIO.setup(c.BRAILLE_INPUT_PIN[pin], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Control buttons
    for pin in range(len(c.FUNCTION_PIN)):
        GPIO.setup(c.FUNCTION_PIN[pin], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Setup callback
    
    GPIO.add_event_detect(c.BRAILLE_INPUT_PIN[0], GPIO.RISING, callback=g.callback0, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.BRAILLE_INPUT_PIN[1], GPIO.RISING, callback=g.callback1, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.BRAILLE_INPUT_PIN[2], GPIO.RISING, callback=g.callback2, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.BRAILLE_INPUT_PIN[3], GPIO.RISING, callback=g.callback3, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.BRAILLE_INPUT_PIN[4], GPIO.RISING, callback=g.callback4, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.BRAILLE_INPUT_PIN[5], GPIO.RISING, callback=g.callback5, bouncetime=c.BOUNCE_TIME)

    GPIO.add_event_detect(c.FUNCTION_PIN[0], GPIO.RISING, callback=g.callbackNXT, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.FUNCTION_PIN[1], GPIO.RISING, callback=g.callbackRST, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.FUNCTION_PIN[2], GPIO.RISING, callback=g.callbackLVLUP, bouncetime=c.BOUNCE_TIME)
    GPIO.add_event_detect(c.FUNCTION_PIN[3], GPIO.RISING, callback=g.callbackLVLDOWN, bouncetime=c.BOUNCE_TIME)    
        
# Check whether this file is the file that is executed first
# This part should be at the bottom to ensure all called methods are defined before calling them
if __name__ == '__main__':
    main() 
