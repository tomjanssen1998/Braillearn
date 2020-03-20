from pygame import mixer #for playing mp3 sounds
import random # randrange
import Constant as c
import time

currentAudio = ''
pausedAudio = ''
pausedPosition = 0.0 # At what position of audio do we pause


#i n i t i a l i z e A u d i o ():
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
    global currentAudio
    
    if (audio_name == 'Incorrect' or audio_name == 'Correct' or audio_name == 'Correct_Short'):
        r = random.randrange(2)
        if (r == 0):
            to_load = 'Sounds/' + audio_name + '1.mp3'
        else:
            to_load = 'Sounds/' + audio_name + '2.mp3'
    else:
        to_load = 'Sounds/' + audio_name + '.mp3'
    
    currentAudio = audio_name # currently playing audio
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
    global pausedAudio
    global currentAudio
    global pausedPosition
    
    pausedAudio = ''
    if (mixer.music.get_busy() == True):
        pausedAudio = currentAudio
        mixer.music.pause()
        pausedPosition += float(mixer.music.get_pos() / 1000) # float division: convert milliseconds to seconds
        print("paused: audio: " + str(pausedAudio) + " position: " + str(pausedPosition))
        mixer.music.stop() # Stop audio
      
      
# u n p a u s e A u d i o ()
# ===============================
# Resumes previously playing audio at current position

def unpauseAudio():
    global pausedAudio
    global pausedPosition
    
    stopAudio() # Only stops audio if something is playing
    
    if (pausedAudio != ''): # Only resume if there was something playing before the pause
        playAudio(pausedAudio, pausedPosition)
  
  
# w a i t F o r A u d i o ()
# ===============================
# Waits for current audio file to finish
#
def waitForAudio():
    is_playing = True
    while (is_playing) :
        time.sleep(0.01)
        is_playing = mixer.music.get_busy()