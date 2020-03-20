import Globals as g
import pyttsx3
import multiprocessing
import importlib
import time
import Constant as c
import Audio as a
import RPi.GPIO as GPIO
import random # randrange

# m a i n ()
# ===========================
# Main function
#
def main():
    a.initializeAudio()
    print('Done initializing audio')
    initializeGPIO()
    print('Done initializing GPIO')
    
    runTutorial() # Tutorial of device
    
    runProgram() # Main program of device


# r u n P r o g r a m ()
# ===============================
# run the main braillearn program
#
def runProgram():
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
                        else:
                            g.task = 1 # Start at the front again
                        taskFile = 'Tasks.Task' + str(g.task)
                        abort = True
                        print('Moving to task ' + str(g.task))
                        break
                    
                    if g.checkBtnState('LVLDOWN'):
                        g.resetBtnStates()
                        if g.task > 1:
                            g.task -= 1
                        else:
                            g.task = g.taskCount
                        taskFile = 'Tasks.Task' + str(g.task)
                        abort = True
                        print('Moving to task ' + str(g.task))
                        break
                            
                    if g.checkBtnState('NXT'):
                        g.resetBtnStates()
                        if g.lastBinInput != 0: # Something is filled in
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


# r u n T u t o r i a l ()
# ===============================
# run through tutorial of Braillearn
#
def runTutorial():
    
    g.globalState = -1 # Tutorial part 1 - Introduction
    a.playAudio('Tutorial1', 0)
    
    waitForTutorial()
    
    time.sleep(c.TUTORIAL_SLEEP_TIME1)
    g.globalState = -2 # Tutorial part 2 - Buttons
    a.playAudio('Tutorial2', 0)
        
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
    a.playAudio('Tutorial3-1', 0)
    
    skipped = waitForTutorial()
    if (not skipped):
        time.sleep(c.TUTORIAL_SLEEP_TIME1)
        waitForAllBraille()

    time.sleep(c.TUTORIAL_SLEEP_TIME1)
    a.playAudio('Tutorial3-2', 0)
    
    waitForTutorial()

    time.sleep(c.TUTORIAL_SLEEP_TIME1)
    g.globalState = -4 # Tutorial part 4 - Concluding
    a.playAudio('Tutorial4', 0)
    
    while True:
        time.sleep(0.01)
        if(g.checkBtnState('RST')):
            g.resetBtnStates()
            a.stopAudio()
            runTutorial()
        elif(g.checkBtnState('NXT')):
            g.resetBtnStates()
            a.stopAudio()
            break   
        
    print("Tutorial done")


# w a i t F o r A l l B r a i l l e()
# ===============================
# Waits for all braille inputs to be pushed down
#
def waitForAllBraille():
    # ToDo: Set all braille input pins in up position
    a.pausedPosition = 0.0 # Reset pause position variable
    
    a.playAudio('TutorialBRAILLE', 0)
    prevInput = currInput = 0
    
    while True:

        time.sleep(0.01)
        currInput = g.binInput
        
        if (currInput == g.T2B['all']): # all braille pins are down
            break
        
        if (prevInput != currInput): # braille pin was pressed but not yet all pins are down
            prevInput = currInput
            a.pauseAudio()
            
            a.playAudio('Correct_Short', 0)
            a.waitForAudio()
            
            a.unpauseAudio()
    
    a.stopAudio() # when user has pressed target button, we can stop button-specific instruction
    
    g.brailleState = [0,0,0,0,0,0] # reset Braille input
    g.binInput = 0
    g.lastBinInput = 0
    
    print("All braille cells pressed")
    a.playAudio('Correct', 0)
    a.waitForAudio()


# w a i t F o r B t n P r e s s ()
# ===============================
# Waits for the user to press a certain button
#
def waitForBtnPress(button_name):
    g.resetBtnStates()
    a.pausedPosition = 0.0 # Reset pause position variable
    
    a.playAudio('Tutorial' + button_name, 0)
    
    is_pressed = g.checkBtnState(button_name)
    while (not is_pressed):
        if (g.numberOfBtnPresses() > 0): # we know it must be incorrect since we are still in the while loop
            
            print("Incorrect button pressed")
            a.pauseAudio() # Pause currently playing
            
            a.playAudio('Incorrect', 0)
            a.waitForAudio()
            
            a.unpauseAudio() # Resume currently playing
            g.resetBtnStates()
        
        time.sleep(0.01)
        is_pressed = g.checkBtnState(button_name)
    
    a.stopAudio() # when user has pressed target button, we can stop button-specific instruction
    
    print("Correct button pressed")
    a.playAudio('Correct', 0)
    a.waitForAudio()
    
    g.setBtnState(button_name, False)
    
        
# w a i t F o r T u t o r i a l ()
# ===============================
# Remains in loop until current audio file has finished playing or next button has been pressed
# Returns True if skip button was pressed, False otherwise
#
def waitForTutorial():
    is_playing = True
    while (is_playing) :
        time.sleep(0.01)
        is_playing = a.mixer.music.get_busy()
        if (g.checkBtnState('NXT')):
            g.setBtnState('NXT', False)
            a.stopAudio()
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
