#Quiz options
repeatUntilCorrect = True  # Repeats questions if answered incorrectly
repeatImmediately = False  # Whether to repeat immediately or when all other questions are asked
randomizeOrder = False     # Whether to ask questions in a random order or as they are given

feedbackPerLetter = False  # Whether to provide feedback for every letter or for every question

#Quiz content
quiz = ['g', 'h', 'i']





# Sanity checks to ensure way of questioning makes sense
# ========================================================

# If quiz contains words, errors must be repeated immediately and until correct if feedback is provided per letter

if len(max(quiz, key=len)) > 1 and feedbackPerLetter: 
	repeatUntilCorrect = True
	repeatImmediately = True