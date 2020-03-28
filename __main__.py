import Globals as g
import pyttsx3
import multiprocessing
import importlib
import time
import Constant as c
import Audio as a
import RPi.GPIO as GPIO
import random # randrange

READ_PINS = []

# m a i n ()
# ===========================
# Main function
#
def main():
    
    a.initializeAudio()
    print('Done initializing audio')
    initializeGPIO()
    print('Done initializing GPIO')
    
    g.globalState = 0
    #runTutorial() # Tutorial of device
    
    g.globalState = 1
    runTask('Tasks.Task1') # Run first task
    
    #Infinite loop: only stop main program when RPi is shut down
    while True: # After finishing/aborting a task we end up here
        if g.checkBtnState('LVLUP'):
            handleIndicatorsLocally('LVLUP')
        if g.checkBtnState('LVLDOWN'):
            handleIndicatorsLocally('LVLDOWN')


# r u n T a s k (task_file)
# ===============================
# runs the task 'task_file'
#
def runTask(task_file):
       
    g.taskRunning = True
    tasks = importlib.import_module(task_file)  #Dynamically load task
    g.abort = False
        
    #Randomize order of quiz if desired
    quiz = tasks.quiz.copy()
    if tasks.randomizeOrder:
        random.shuffle(quiz)

    print(quiz)

    #loop though question of quiz
    for question in quiz:
        answer = []

        if g.abort:       #Stop current quiz (to go to different level)
            print('Level cancelled')
            g.taskRunning = False
            break

        #Ask question to user
        if tasks.quizMode < 3: #If the quiz is for single letters:
            a.playAudio('/Program/pleaseletter', 0)
            a.waitForAudio()
            a.playAudio('/Program/' + question, 0)
            a.waitForAudio()
            string = "Please write the letter: " + question
        else:
            a.playAudio('/Program/pleaseword', 0)
            a.waitForAudio()
            a.playAudio('/Program/' + question, 0)
            a.waitForAudio()
            string = "Please write the word: " + question
                
        time.sleep(c.PROGRAM_SLEEP_TIME1)
        print(string)

        #loop through letters of question one by one
        for count, letter in enumerate(question):
                
            if g.abort:   #Stop current quiz (to go to different level)
                break
                
            completed = False
                
            while not completed:
                if tasks.readEveryLetter:
                    if (tasks.quizMode > 2): # working with words
                        if (count == 0):
                            a.playAudio('/Program/letterfirstis', 0)
                        elif (count == (len(question)-1)):
                            a.playAudio('/Program/letterfinalis', 0)
                        else:
                            a.playAudio('/Program/letternextis', 0)
                                
                    a.waitForAudio()
                    a.playAudio('/Program/' + letter, 0)
                    a.waitForAudio()
                    time.sleep(c.PROGRAM_SLEEP_TIME1)
                        
                    string = "The next letter is: " + letter
                    print(string + "': " + str(g.T2B[letter]))
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
                            READ_PINS[dot].ChangeDutyCycle(60)
                            #activate braille dot 'dot'
                        else:
                            READ_PINS[dot].ChangeDutyCycle(0)
                        
                    if (c.INFORM_USER_LEFT_BRAILLE_IS_ACTIVE):
                        a.playAudio('/Program/demo', 0)
                        a.waitForAudio()

                waitForBreak() # Wait for user inputs
                    
                for dot in range(0,6):
                    #deactivate braille dot 'dot'
                    READ_PINS[dot].ChangeDutyCycle(0)
                    
                if g.abort: # As replacement of previous level-indicator code here
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
                                a.playAudio('correct_short', 0)
                                a.waitForAudio()
                                    
                                print("Letter correct!")
                                completed = True
                            else:
                                a.playAudio('incorrect_short', 0)
                                a.waitForAudio()
                                    
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

        if (not g.abort): # don't give such feedback when going to other task
            if not tasks.feedbackPerLetter:
                answer = ''.join(answer)
                if question == answer:
                    a.playAudio('correct', 0)
                    a.waitForAudio()    
                        
                    print("Question answered correctly!")
                elif tasks.repeatUntilCorrect:
                    if tasks.repeatImmediately:
                        a.playAudio('incorrect_repeatImmediately', 0)
                        a.waitForAudio()
                            
                        print("That is incorrect, try again!")
                        quiz.insert(question,count+1)
                    else:
                        a.playAudio('incorrect_repeatLater', 0)
                        a.waitForAudio()
                            
                        print("That is incorrect, try again later!")
                        quiz.append(question)
                else:
                    a.playAudio('incorrect', 0)
                    a.waitForAudio()
                        
                    print("That is incorrect!")
            else:
                time.sleep(c.PROGRAM_SLEEP_TIME1)
                a.playAudio('/Program/wordcomplete', 0)
                a.waitForAudio()
                print('Word done!')
          
    if (not g.abort): # don't give such feedback when going to other task
        time.sleep(c.PROGRAM_SLEEP_TIME2)
        a.playAudio('/Program/taskcomplete', 0)
        a.waitForAudio()
        g.taskRunning = False
        print('Level complete!')    
        for dot in range(len(READ_PINS)):
            READ_PINS[dot].ChangeDutyCycle(0)

# h a n d l e I n d i c a t o r s L o c a l l y (indicator)
# ===============================
# called when a level-indicator press is detected and moves program to a new task
#
def handleIndicatorsLocally(indicator):
    g.resetBtnStates()
    if (indicator == 'LVLUP'):
        if g.task < g.taskCount:
            g.task += 1
        else:
            g.task = 1 # Start at the front again
    elif (indicator == 'LVLDOWN'):
        if g.task > 1:
            g.task -= 1
        else:
            g.task = g.taskCount
            
    g.taskFile = 'Tasks.Task' + str(g.task)
    print('Moving to task ' + str(g.task))
                        
    a.playAudio('/Program/task', 0)
    a.waitForAudio()
    a.playAudio('/Program/' + str(g.task), 0)
    time.sleep(c.PROGRAM_SLEEP_TIME1)
    
    runTask(g.taskFile) # run the new task


# r u n T u t o r i a l ()
# ===============================
# run through tutorial of Braillearn
#
def runTutorial():
    
    # Tutorial part 1 - Introduction
    a.playAudio('/Tutorial/part1', 0)
    
    waitForTutorial()
    
    time.sleep(c.TUTORIAL_SLEEP_TIME1)
    # Tutorial part 2 - Buttons
    a.playAudio('/Tutorial/part2', 0)
        
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
    # Tutorial part 3 - Braille inputs
    a.playAudio('/Tutorial/part3.1', 0)
    
    skipped = waitForTutorial()
    if (not skipped):
        time.sleep(c.TUTORIAL_SLEEP_TIME1)
        waitForAllBraille()

    time.sleep(c.TUTORIAL_SLEEP_TIME1)
    a.playAudio('/Tutorial/part3.2', 0)
    
    waitForTutorial()

    time.sleep(c.TUTORIAL_SLEEP_TIME1)
    # Tutorial part 4 - Learning modes
    a.playAudio('/Tutorial/part4', 0)
    
    waitForTutorial()
    
    time.sleep(c.TUTORIAL_SLEEP_TIME1)
    # Tutorial part 5 - Concluding
    a.playAudio('/Tutorial/part5', 0)
    
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
    time.sleep(c.TUTORIAL_SLEEP_TIME1) # sleep small moment before running main program


# w a i t F o r A l l B r a i l l e()
# ===============================
# Waits for all braille inputs to be pushed down
#
def waitForAllBraille():
    # ToDo: Set all braille input pins in up position
    a.pausedPosition = 0.0 # Reset pause position variable
    
    a.playAudio('/Tutorail/part3.1_BRAILLE', 0)
    prevInput = currInput = 0
    
    while True:

        time.sleep(0.01)
        currInput = g.binInput
        
        if (currInput == g.T2B['all']): # all braille pins are down
            break
        
        if (prevInput != currInput): # braille pin was pressed but not yet all pins are down
            prevInput = currInput
            a.pauseAudio()
            
            a.playAudio('correct_short', 0)
            a.waitForAudio()
            
            a.unpauseAudio()
    
    a.stopAudio() # when user has pressed target button, we can stop button-specific instruction
    
    g.brailleState = [0,0,0,0,0,0] # reset Braille input
    g.binInput = 0
    g.lastBinInput = 0
    
    print("All braille cells pressed")
    a.playAudio('correct', 0)
    a.waitForAudio()


# w a i t F o r B t n P r e s s ()
# ===============================
# Waits for the user to press a certain button
#
def waitForBtnPress(button_name):
    g.resetBtnStates()
    a.pausedPosition = 0.0 # Reset pause position variable
    
    a.playAudio('/Tutorial/part2_' + button_name, 0)
    
    is_pressed = g.checkBtnState(button_name)
    while (not is_pressed):
        if (g.numberOfBtnPresses() > 0): # we know it must be incorrect since we are still in the while loop
            
            print("Incorrect button pressed")
            a.pauseAudio() # Pause currently playing
            
            a.playAudio('incorrect', 0)
            a.waitForAudio()
            
            a.unpauseAudio() # Resume currently playing
            g.resetBtnStates()
        
        time.sleep(0.01)
        is_pressed = g.checkBtnState(button_name)
    
    a.stopAudio() # when user has pressed target button, we can stop button-specific instruction
    
    print("Correct button pressed")
    a.playAudio('correct', 0)
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
    #g.resetBtnStates() DIDTHIS TEMPORARY
    
    while True :
        time.sleep(0.01) #Precautionary: Don't know if this is needed, but thought is that this delay gives the interrupt time to change variable
        if (g.checkBtnState('NXT') or g.checkBtnState('RST') or g.checkBtnState('LVLUP') or g.checkBtnState('LVLDOWN')):
            break
        

# i n i t i a l i z e G P I O ()
# ===============================
# initialize all GPIO pins used
#
def initializeGPIO():
    global READ_PINS
    GPIO.setmode(GPIO.BCM) #referring to the pins by the "Broadcom SOC channel" numbers
    
    #For Raspberry Pi 3B:
    #GPIO.setmode(GPIO.BOARD)
    
    # Input braille cell
    for pin in range(len(c.BRAILLE_INPUT_PIN)):
        GPIO.setup(c.BRAILLE_INPUT_PIN[pin], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Control buttons
    for pin in range(len(c.FUNCTION_PIN)):
        GPIO.setup(c.FUNCTION_PIN[pin], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    for pin in range(len(c.BRAILLE_READ_PAD)):
        GPIO.setup(c.BRAILLE_READ_PAD[pin], GPIO.OUT)
        READ_PINS.append(GPIO.PWM(c.BRAILLE_READ_PAD[pin],40000))
        READ_PINS[pin].start(0)
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
