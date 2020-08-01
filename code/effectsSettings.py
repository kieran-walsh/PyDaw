####################################
# effectsSettings.py (TP2)
# Creator: Kieran Walsh
# Andrew ID: kawalsh
####################################

#This file is a collection of functions/properties needed to digitally
#maniupulate audio - functions for playback, adding distortion, modulation, etc

import pyo

#Class that will be initialized by each new audio track so that each audio
#track has its own audio server and can play audio independently
class EffectsManager(object):
    
    #Initial objects/properties needed to manipulate audio data using Pyo
    def __init__(self, name):
        self.channels = 2
        self.rate = 44100
        self.chunk = 1024
        self.server = pyo.Server(sr=self.rate, nchnls=self.channels, 
            buffersize=self.chunk, duplex=1, audio='portaudio').boot()
        self.server.start()
        self.normalAmp = self.server.amp
        
        #Creates a new soundFilePlayer object that plays the audio file
        #designated by the "audioName" - in case the audioName is not valid,
        #An exception is raised to instead use a blank audio file
        self.audioName = name
        self.backupFile = "Temp/noAudio.wav"
        try: self.soundPlayer = pyo.SfPlayer(self.audioName)
        except: self.soundPlayer = pyo.SfPlayer(self.backupFile)
        
        #Used in the process of applying effects
        self.currentStream = self.soundPlayer
        self.previousStream = self.soundPlayer
        
        
    #Creates a new SFPlayer (soundFilePlayer) for use in audio manipulation
    #And starts the output
    def createNewSFPlayer(self, filename, loopTrack=False):
        print("New player", "loop:", loopTrack)
        self.server.start()
        self.soundPlayer = pyo.SfPlayer(filename, loop=loopTrack)
        self.currentStream = self.soundPlayer
        self.previousStream = self.soundPlayer
        self.currentStream.out()

#Overall function to manage the activated and deactivated effects pedals
    def manageEffects(self, activatedEffects):
        applied = set()
        self.previousStream = self.currentStream
        
        #Unpack the activatedEffects list to get the active effects pedals
        #Each pedal has a specific place in the list
        hasDistortion = activatedEffects[0]
        hasChorus = activatedEffects[1]
        hasPhaser = activatedEffects[2]
        muted = activatedEffects[3]

        #Checks each pedal and applies the target effect pedal if that
        #effect pedal is active and if that effect has not already been applied
        for i in range(len(activatedEffects)):
            if hasDistortion and ("Distortion" not in applied): 
                self.currentStream = applyDistortion(self.previousStream)
                self.previousStream = self.currentStream
                applied.add("Distortion")
            if hasChorus and ("Chorus" not in applied):
                self.currentStream = applyChorus(self.previousStream)
                self.previousStream = self.currentStream
                applied.add("Chorus")
            if hasPhaser and ("Phaser" not in applied):
                self.currentStream = applyPhaser(self.previousStream)
                self.previousStream = self.currentStream
                applied.add("Phaser")

####################################
# Effects Pedals Code
####################################

#Found in Pyo 0.9.1 Documetation:
#http://ajaxsoundstudio.com/pyodoc/api/classes/filters.html#phaser
def applyPhaser(stream):
    fade = pyo.Fader(fadein=.1, mul=.07).play()
    a = pyo.Sine(fade).mix(2).out()
    lf1 = pyo.Sine(freq=[.1, .15], mul=100, add=250)
    lf2 = pyo.Sine(freq=[.18, .15], mul=.4, add=1.5)
    return pyo.Phaser(stream, freq=lf1, spread=lf2, q=1, num=20, mul=.75).out(0)
  
#Found in Pyo 0.9.1 Documetation:
#http://ajaxsoundstudio.com/pyodoc/api/classes/effects.html#chorus
def applyChorus(stream):
    return pyo.Chorus(stream, depth=[1.5,1.6], feedback=0.5, bal=0.75).out()

#Found in Pyo 0.9.1 Documetation:
#http://ajaxsoundstudio.com/pyodoc/api/classes/effects.html#disto
def applyDistortion(stream):
    return pyo.Disto(stream, drive=0.75, slope=0.5, mul=1, add=0).out()