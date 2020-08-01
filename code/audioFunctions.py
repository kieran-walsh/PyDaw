####################################
# audioFunctions.py (TP2)
# Creator: Kieran Walsh
# Andrew ID: kawalsh
####################################

#This file is a collection of functions and properties needed to record,
#playback, loop, wire, and otherwise manipulate audio.

from tkinter import *
import pyaudio
import wave
import threading
import sys
import pyo
import effectsSettings

#Creates a new audio track for each corresponding track shown on the graphical
#Interface; this is where recording, playback, and wiring happen
class Track(object):
    
    #Some constants needed to record and playback audio
    #Found from PyAudio documentation: 
    #https://people.csail.mit.edu/hubert/pyaudio/
    def __init__(self, trackNumber, filename=None):
        self.audioFormat = pyaudio.paInt16
        self.channels = 2
        self.rate = 44100
        self.width = 2
        self.chunk = 1024
        self.audio = pyaudio.PyAudio()
        
        #Used when importing a local audio file
        if filename != None: self.name = filename
        else: self.name = "Temp/" + "temp" + str(trackNumber) + ".wav"
        
        #Global variables used in the recording process
        self.recording = False
        self.frames = []
        
        #Global variables used in the playback process
        self.waveFileData = []
        self.loop = False
        self.isPlaying = False
        self.trackEffectsManager = effectsSettings.EffectsManager(self.name)
        self.wireEnabled = False
        self.isIdle = True
        
####################################
# Recording
####################################    
    
    #Handles the actual recording of the audio, with the 
    #opening/closing of streams
    def recordBackend(self):
        self.recording = True
        #Prepares the stream for recording
        stream = self.audio.open(format=self.audioFormat, 
                            channels=self.channels, rate=self.rate, input=True,
                            frames_per_buffer=self.chunk, start=False)
                        
        #Begins recording and continues to record until the "recording" flag
        #is set to False
        stream.start_stream()
        print("recording...")
        while self.recording == True:
            data = stream.read(self.chunk)
            self.frames.append(data)
        print("finished recording")
        
        # stop Recording
        stream.stop_stream()
        stream.close()
        print("(Recording) Stream closed.")
    
    #Wrapper function for the recordBackend() that runs that process in a
    #separate thread
    def record(self):
        recordClip = threading.Thread(target=self.recordBackend)
        recordClip.start()
        
    #Uses the global recording variable to stop the recording process and then
    #saves the recording to a .wav file
    def stopRecording(self):
        self.recording = False
        self.save()
    
    #Saves the recording to a .wav file
    #Found from PyAudio documentation: 
    #https://people.csail.mit.edu/hubert/pyaudio/
    def save(self):
        wf = wave.open(self.name, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.audioFormat))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        self.frames = []
        wf.close()
    
####################################
# Playback
####################################
        
    #Rewinds the wave file for next instance of playback and stops the stream
    def stopAudio(self, stream):
        self.isPlaying = False
        self.loop = False
        self.trackEffectsManager.server.stop()

    #Playing back audio with effects pedals and loop settings
    def playPyo(self, loop, effects):
        #Tries to create a SFPlayer with the given audio name (used when
        #importing local files) - if it can't, it will catch the error
        try: self.trackEffectsManager.createNewSFPlayer(self.name, 
                                                            loopTrack=loop)
        except: print("Audio Error: invalid audio")
        self.trackEffectsManager.manageEffects(effects)
        print(self.name)
        
    #Starts a separate thread for playback of a recording (used for playback)
    def playbackPyo(self, loop, effects):
        playbackPyoThread = threading.Thread(target=self.playPyo(loop, effects))
        playbackPyoThread.start()

####################################
# Wiring (Real-time playback)
####################################
    
    #Sets the stream as the continuous input from the microphone, adds effects
    #to it, and then outputs it
    def wireAudio(self, effects):
        self.trackEffectsManager.currentStream = pyo.Input()
        self.trackEffectsManager.manageEffects(effects)
        return self.trackEffectsManager.currentStream.out()
