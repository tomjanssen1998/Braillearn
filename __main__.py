import Globals as g
import pyttsx3
import multiprocessing
import importlib

#Text to Speech
engine = pyttsx3.init()
engine.setProperty('rate', 140)

def Read_text(text):
	engine.say(text)
	engine.runAndWait()
	return

def Prepare_TTS(text):
	p = multiprocessing.Process(target = Read_text, args=(text,))
	p.start()



#check whether this file is the file that is executed first
if __name__ == '__main__':

	#Dynamically load tasks when switching levels
	tasks = importlib.import_module("Tasks.Task1")

	#loop through letters of quiz one by one
	for letter in tasks.quiz:
		print("write the symbol for '" + letter + "': " + str(g.T2B[letter]))
		string = "write the symbol for: " + letter

		#Read the task out loud
		Prepare_TTS(string)

		while True:
			#Will actually be implemented as interrupts
			inpt = input()
			if inpt =='q':
				break
			elif inpt == '1':
				g.callback0(0)
			elif inpt == '2':
				g.callback1(0)
			elif inpt == '3':
				g.callback2(0)
			elif inpt == '4':
				g.callback3(0)
			elif inpt == '5':
				g.callback4(0)
			elif inpt == '6':
				g.callback5(0)
			elif inpt == 'n':
				g.callbackNXT(0)
			elif inpt == 'p':
				g.callbackRST(0)

			print(g.buttonState)

			if g.NXT:
				g.NXT = False
				if g.lastBinInput == g.T2B[letter]:
					print("Correct!")
					break
				else:
					print("Incorrect")

			if g.RST:
				g.RST = False