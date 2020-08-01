####################################
# Pydalboard Main File (TP2)
# Creator: Kieran Walsh
# Andrew ID: kawalsh
####################################

#Main file: controls the animations and top-level design/features of the
#application

import audioFunctions
import effectsSettings
import otherScreens
import pyo
import sys
import threading
import time
from tkinter import *

####################################
# General EffectBox
####################################

#General Template for Effect/Audio Box
class EffectBox(object):
    #Initializes all of the values needed to draw the EffectBox
    def __init__(self, cx, cy, width, height, numBox, color="gray90"):
        self.cx = cx
        self.cy = cy
        self.topLeftText = ""
        self.centerText = ""
        self.color = color
        self.numBox = numBox
        
        self.width = width
        self.height = height
        self.halfWidth = self.width//2
        self.halfHeight = self.height//2
        
        self.activated = False
        self.controls = []
        
        self.powerBtnLeftBound = self.width//10
        self.powerBtnRightBound = 2*(self.width//10)
        self.btnUpperBound = self.cy-self.halfHeight//2
        self.btnLowerBound = self.cy+self.halfHeight//2

    #Draws the various items needed when drawing an EffectBox
    def draw(self, canvas, data):
        #Draw the EffectBox
        self.boxZeroX = data.offsetWidth
        self.boxZeroY = data.offsetHeight + self.height*(self.numBox-1)
        self.topLeftX = self.boxZeroX*2 + 2*(len(self.topLeftText)-10)
        self.topLeftY = self.boxZeroY+self.height//10
        
        #Draw the foundation of the box
        canvas.create_rectangle(self.cx-self.halfWidth, self.cy-self.halfHeight, 
                    self.cx+self.halfWidth, self.cy+self.halfHeight, 
                                                            fill=self.color)
        #Draw the labels for the boxes
        canvas.create_text(self.cx, self.cy, text=self.centerText, 
                                                    font="Arial 20 italic")
        canvas.create_text(self.topLeftX, self.topLeftY, text=self.topLeftText, 
                                                        font="Arial 15 italic")
        
####################################
# BlankBox
####################################

#Template for BlankBox for creating new audio tracks
class BlankBox(EffectBox):
    def __init__(self, cx, cy, width, height, numBox):
        super().__init__(cx, cy, width, height, numBox)
        self.centerText = "Add New Track"
        self.userAudioTrack = audioFunctions.Track(self.numBox)
        
    def checkForClick(self, data, x, y):
        if (self.cx-self.halfWidth <= x <= self.cx+self.halfWidth and
            self.cy-self.halfHeight <= y <= self.cy+self.halfHeight):
            return True
  
####################################
# UserAudioBox
####################################

#Class for the user's "Audio Box" - this is where the user will record and
#playback audio, as well as witch into "Live" mode
class UserAudioBox(EffectBox):
    def __init__(self, cx, cy, width, height, numBox, color):
        #Similar to EffectBox with a few changed properties
        super().__init__(cx, cy, width, height, numBox, color)
        self.activated = True
        self.centerText = "Idle"
        self.topLeftText = "User Audio"
        self.recBtnLeftBound = self.cx+self.halfWidth*0.3
        self.recBtnText = self.cx+self.halfWidth*0.4
        
        #Sets dimensions for objects that will be drawn later
        self.recBtnRightBound = self.cx+self.halfWidth*0.5
        self.playBtnLeftBound = self.recBtnRightBound
        self.playBtnText = self.cx+self.halfWidth*0.6
        self.playBtnRightBound = self.cx+self.halfWidth*0.7
        self.liveBtnLeftBound = self.playBtnRightBound
        self.liveBtnText = self.cx+self.halfWidth*0.8
        self.liveBtnRightBound = self.cx+self.halfWidth*0.9
        
        self.fxBtnLeftBound = self.cx-self.halfWidth*0.9
        self.fxBtnText = self.cx-self.halfWidth*0.8
        self.fxBtnRightBound = self.cx-self.halfWidth*0.7
        
        self.loopBtnLeftBound = self.fxBtnRightBound
        self.loopBtnText = self.cx-self.halfWidth*0.6
        self.loopBtnRightBound = self.cx-self.halfWidth*0.5
        
        self.hasDistortion = False
        self.hasChorus = False
        self.hasPhaser = False
        self.muted = False
        
        self.effectsActivated = [self.hasDistortion, self.hasChorus, 
                                                self.hasPhaser, self.muted]
        
        #Creates an audio track unless the current object is an
        #InsertedAudioBox (if so, this will be done later)
        self.trackNumber = numBox-1
        if not isinstance(self, InsertedAudioBox):
            self.userAudioTrack = audioFunctions.Track(self.trackNumber)
        self.wire = None

    #Draws a box/button with the specified dimensions
    def drawBox(self, canvas, leftBound, rightBound, textSpot, boxText):
        canvas.create_rectangle(leftBound, self.btnUpperBound, 
                    rightBound, self.btnLowerBound, 
                                                        fill="light yellow")
        canvas.create_text(textSpot, self.cy, text=boxText,
        font="Arial 20 italic")
    
    #Draws the various aspects of the UserAudioBox
    def draw(self, canvas, data):
        super().draw(canvas, data)
        #Draw buttons
        self.drawBox(canvas, self.recBtnLeftBound, self.recBtnRightBound, 
                                                    self.recBtnText, "Rec")
        self.drawBox(canvas, self.playBtnLeftBound, self.playBtnRightBound, 
                                                    self.playBtnText, "Play")
        self.drawBox(canvas, self.liveBtnLeftBound, self.liveBtnRightBound,
                                                    self.liveBtnText, "Live")
        self.drawBox(canvas, self.fxBtnLeftBound, self.fxBtnRightBound,
                                                    self.fxBtnText, "FX")
        self.drawBox(canvas, self.loopBtnLeftBound, self.loopBtnRightBound,
                                                    self.loopBtnText, "Loop")
        self.drawStatusBar(canvas, data)
        self.drawXButton(canvas, data)
        
    #Draws the Status Bar
    def drawStatusBar(self, canvas, data):
        canvas.create_rectangle(self.cx-self.halfWidth//2.5, self.btnUpperBound, 
                    self.cx+self.halfWidth//5, self.btnLowerBound,
                                                        fill="light yellow")
        canvas.create_text(self.width//2, self.cy, 
                        text="Status: "+self.centerText, font="Arial 20 italic")
                            
    #Draws the X button in the top-right corner
    def drawXButton(self, canvas, data):
        self.leftX, self.rightX = (self.cx+self.width//2*(9.25/10), 
                                                    self.cx+self.width//2)
        self.topX, self.bottomX = (self.cy-self.height//2, 
                                                    self.cy-self.height//4)
        canvas.create_rectangle(self.leftX, self.topX, self.rightX, 
                                                    self.bottomX, fill="red3")
        canvas.create_line(self.leftX+2, self.topX+2, self.rightX-2, 
                                        self.bottomX-2, fill="white", width=3)
        canvas.create_line(self.leftX+2, self.bottomX-2, self.rightX-2,
                                            self.topX+2, fill="white", width=3)
       
    #Return True if the user clicks the X button
    def checkForXClick(self, x, y):
        if (self.leftX <= x <= self.rightX) and self.topX <= y <= self.bottomX:
            return True
               
####################################
# UAB ButtonClicked
####################################
    
    #Handles the click of a button on the UserAudioBox
    def buttonClicked(self, x, y):
        #Record Button
        if (self.recBtnLeftBound <= x <= self.recBtnRightBound and
            self.btnUpperBound <= y <= self.btnLowerBound):
            self.recordClick()
        #Play Button
        elif (self.playBtnLeftBound <= x <= self.playBtnRightBound and
            self.btnUpperBound <= y <= self.btnLowerBound):
            self.playClick()
        #Live Button
        elif (self.liveBtnLeftBound <= x <= self.liveBtnRightBound and
            self.btnUpperBound <= y <= self.btnLowerBound):
            self.liveClick()
        #Loop Button
        elif (self.loopBtnLeftBound <= x <= self.loopBtnRightBound and
            self.btnUpperBound <= y <= self.btnLowerBound):
            self.loopClick()
        #FX Button
        elif (self.fxBtnLeftBound <= x <= self.fxBtnRightBound and
            self.btnUpperBound <= y <= self.btnLowerBound):
            self.drawToplevel()

    #Handles the event of the user clicking "Record"
    def recordClick(self):
        if isinstance(self, UserAudioBox):
            if self.userAudioTrack.recording == False:
                self.userAudioTrack.record()
                self.centerText = "Recording"
            else: 
                self.userAudioTrack.stopRecording()
                self.centerText = "Idle"

    #Handles the event of the user clicking "Play"
    def playClick(self):
        if self.userAudioTrack.isPlaying == False:
            self.userAudioTrack.wireEnabled = False
            self.userAudioTrack.loop = False
            self.userAudioTrack.isPlaying = True
            self.userAudioTrack.playbackPyo(False, self.effectsActivated)
            self.centerText = "Playback"
        else: self.stopPlayback()

    #Handles the event of the user clicking "Live"
    def liveClick(self):
        if self.userAudioTrack.wireEnabled == False:
            self.userAudioTrack.wireEnabled = True
            self.userAudioTrack.loop = False
            self.userAudioTrack.isPlaying = False
            self.wire = self.userAudioTrack.wireAudio(self.effectsActivated)
            self.centerText = "Live Mode"
        else: self.stopLive()

    #Handles the event of the user clicking "Loop"
    def loopClick(self):
        if self.userAudioTrack.loop == False:
            self.userAudioTrack.wireEnabled = False
            self.userAudioTrack.loop = True
            self.userAudioTrack.isPlaying = True
            self.userAudioTrack.playbackPyo(True, self.effectsActivated)
            self.centerText = "Looping"
        else: self.stopPlayback()
        
    #Stops the Live Mode process
    def stopLive(self):
        self.userAudioTrack.trackEffectsManager.soundPlayer.stop()
        self.userAudioTrack.trackEffectsManager.currentStream.stop()
        self.userAudioTrack.trackEffectsManager.previousStream.stop()
        self.userAudioTrack.trackEffectsManager.currentStream = None
        self.userAudioTrack.trackEffectsManager.previousStream = None
        self.userAudioTrack.wireEnabled = False
        self.wire = None
        self.userAudioTrack.isIdle = True
        self.centerText = "Idle"
      
    #Stops the playback process
    def stopPlayback(self):
        self.userAudioTrack.loop = False
        self.userAudioTrack.isPlaying = False
        self.userAudioTrack.trackEffectsManager.soundPlayer.stop()
        self.wire = None
        self.centerText = "Idle"

####################################
####################################
   
   #Draws the FX Console, a Toplevel widget with radio buttons, which controls
   #an audio tracks activated effects (distortion, chorus, phaser)
    def drawToplevel(self):
        self.fxToplevel = Toplevel()
        self.fxToplevel.title("FX Console")
        #Stores the state of the radio buttons - its default values are
        #whether the effects are already activated or not
        self.distOn = IntVar(value=self.hasDistortion)
        self.chorusOn = IntVar(value=self.hasChorus)
        self.phaserOn = IntVar(value=self.hasPhaser)
        self.muteOn = IntVar(value=self.muted)
        Label(self.fxToplevel, text="Audio Track FX Console").grid(row=0)
        
        distButton = Checkbutton(self.fxToplevel, text="Distortion", 
            variable=self.distOn).grid(row=1, sticky=W)
        chorusButton = Checkbutton(self.fxToplevel, text="Chorus", 
            variable=self.chorusOn).grid(row=2, sticky=W)
        phaserButton = Checkbutton(self.fxToplevel, text="Phaser", 
            variable=self.phaserOn).grid(row=3, sticky=W)
        # muteButton = Checkbutton(self.fxToplevel, text="Mute", 
        #     variable=self.muteOn).grid(row=4, sticky=W)
            
        Button(self.fxToplevel, text="OK", command=self.sendEffects).grid(row=4)
        Label(self.fxToplevel, text=" "*50).grid(row=5)

    #Gets the state of the radio buttons in the FX Console and stores those
    #states in the given audio track's settings
    def sendEffects(self):
        self.hasDistortion = self.distOn.get()
        self.hasChorus = self.chorusOn.get()
        self.hasPhaser = self.phaserOn.get()
        self.muted = self.muteOn.get()
        self.effectsActivated = [self.hasDistortion, self.hasChorus, 
                                            self.hasPhaser, self.muted]
        self.fxToplevel.withdraw()
 
####################################
# Transport
####################################

#Creates a class for the Transport, the "track" on the bottom of the interface
#that has controls which apply to the entire project
class Transport(UserAudioBox):
    #Initializes the Box with important properties
    def __init__(self, cx, cy, width, height, numBox, color):
        #Similar to UserAudioBox with a few changed properties
        super().__init__(cx, cy, width, height, numBox, color)
        self.topLeftText = "Transport"
        self.centerText = ""
        
        #Sets up the coordinates for the control boxes to be drawn

        self.insertBtnLeftBound = self.cx-self.halfWidth*0.9
        self.insertBtnText = self.cx-self.halfWidth*0.8
        self.insertBtnRightBound = self.cx-self.halfWidth*0.7
        
        self.playBtnLeftBound = self.cx-self.halfWidth*0.2
        self.playBtnText = self.cx
        self.playBtnRightBound = self.cx+self.halfWidth*0.2
        
        self.stopBtnLeftBound = self.cx+self.halfWidth*0.2
        self.stopBtnText = self.cx+self.halfWidth*0.4
        self.stopBtnRightBound = self.cx+self.halfWidth*0.6
        
        self.loopBtnLeftBound = self.cx-self.halfWidth*0.6
        self.loopBtnText = self.cx-self.halfWidth*0.4
        self.loopBtnRightBound = self.cx-self.halfWidth*0.2
        
    #Draws the box itself and its controls
    def draw(self, canvas, data):
        EffectBox.draw(self, canvas, data)
        self.drawBox(canvas, self.insertBtnLeftBound, self.insertBtnRightBound, 
                            self.insertBtnText, "Insert")
        self.drawBox(canvas, self.playBtnLeftBound, self.playBtnRightBound, 
                            self.playBtnText, "Play")
        self.drawBox(canvas, self.stopBtnLeftBound, self.stopBtnRightBound, 
                            self.stopBtnText, "Stop")
        self.drawBox(canvas, self.loopBtnLeftBound, self.loopBtnRightBound, 
                            self.loopBtnText, "Loop") 
                               
    #Checks to see if any of the box's control buttons were clicked and handles
    #that event
    def checkForClick(self, data, x, y):
        #Insert Button
        if (self.insertBtnLeftBound <= x <= self.insertBtnRightBound and
            self.btnUpperBound <= y <= self.btnLowerBound):
                emptyBoxesLeft = False
                for effectBox in data.effectBoxes:
                   if isinstance(effectBox, BlankBox):
                        emptyBoxesLeft = True
                if emptyBoxesLeft == True: self.getInsertedFilename(data)
        #Loop Button
        elif (self.loopBtnLeftBound <= x <= self.loopBtnRightBound and
            self.btnUpperBound <= y <= self.btnLowerBound):
                self.loopAll(data)
        #Play Button
        elif (self.playBtnLeftBound <= x <= self.playBtnRightBound and
            self.btnUpperBound <= y <= self.btnLowerBound):
                self.playAll(data)
        #Stop Button
        elif (self.stopBtnLeftBound <= x <= self.stopBtnRightBound and
            self.btnUpperBound <= y <= self.btnLowerBound):
                self.stopAll(data)
    
    #Draws a Toplevel tkinter widget to accept the name of the user's desired
    #import file
    def getInsertedFilename(self, data):
        self.fileToplevel = Toplevel()
        self.nameEntry = StringVar()
        self.fileToplevel.title("Import File")
        Label(self.fileToplevel, 
                    text="Enter the name of your imported file:").grid(row=0)
        #Takes in the user's entry
        self.textBox = Entry(self.fileToplevel, 
                    textvariable=self.nameEntry).grid(row=2)
        #When the button is clicked, then finalize and "send" the data
        Button(self.fileToplevel, text='OK', 
                    command=(lambda: self.sendName(data))).grid(row=3)

    #Gets the filename from getInsertedFilename and creates a new audio track
    #from that data
    def sendName(self, data):
        filename = self.nameEntry.get()
        #Creates new InsertedAudioBox
        for box in range(len(data.effectBoxes)):
            if isinstance(data.effectBoxes[box], BlankBox):
                boxIndex = box + 1
                break
        data.effectBoxes[boxIndex-1] = createNewBox(data, "Insert", boxIndex,
                                                                name=filename)
        self.fileToplevel.withdraw()
       
    #Plays every audio track in the project at the same time
    def playAll(self, data):
        for effectBox in data.effectBoxes:
            if not isinstance(effectBox, BlankBox):
                effectBox.userAudioTrack.playbackPyo(False, 
                                                    effectBox.effectsActivated)
                effectBox.centerText = "Playback"

    #Stops every audio track in the project at the same time
    def stopAll(self, data):
        for effectBox in data.effectBoxes:
            if not isinstance(effectBox, BlankBox):
                try: effectBox.stopPlayback()
                except: print("Playback could not be stopped")
                try: effectBox.stopLive()
                except: print("Live mode could not be stopped")
                if effectBox.userAudioTrack.recording == True:
                    effectBox.userAudioTrack.stopRecording()
                
    def loopAll(self, data):
        for effectBox in data.effectBoxes:
            if not isinstance(effectBox, BlankBox):
                effectBox.userAudioTrack.playbackPyo(True, 
                                                    effectBox.effectsActivated)
                effectBox.centerText = "Looping"
                
####################################
# InsertedAudioBox
####################################

#Creates a class for a local audio track that was imported by the user
class InsertedAudioBox (UserAudioBox):
    #Initializes the Box with important properties
    def __init__(self, cx, cy, width, height, numBox, color, filename):
        super().__init__(cx, cy, width, height, numBox, color)
        self.topLeftText = " Imported Audio"
        self.centerText = "Idle"
        
        self.fxBtnLeftBound = self.cx-self.halfWidth*0.9
        self.fxBtnText = self.cx-self.halfWidth*0.8
        self.fxBtnRightBound = self.cx-self.halfWidth*0.7
        
        self.loopBtnLeftBound = self.fxBtnRightBound
        self.loopBtnText = self.cx-self.halfWidth*0.6
        self.loopBtnRightBound = self.cx-self.halfWidth*0.5
        
        self.playBtnLeftBound = self.cx+self.halfWidth*0.7
        self.playBtnText = self.cx+self.halfWidth*0.8
        self.playBtnRightBound = self.cx+self.halfWidth*0.9
        
        #Sets the filename of the track to be referenced later and also
        #sets up its designated audio track
############
        self.name = filename
        self.userAudioTrack = audioFunctions.Track(self.trackNumber, 
                                                        filename=self.name)
    
    #Draws the InsertedAudioBox
    def draw(self, canvas, data):
        EffectBox.draw(self, canvas, data)
        super().drawStatusBar(canvas, data)
        super().drawXButton(canvas, data)
        self.drawBox(canvas, self.playBtnLeftBound, self.playBtnRightBound,
                                                    self.playBtnText, "Play")
        self.drawBox(canvas, self.fxBtnLeftBound, self.fxBtnRightBound,
                                                    self.fxBtnText, "FX")
        self.drawBox(canvas, self.loopBtnLeftBound, self.loopBtnRightBound,
                                                    self.loopBtnText, "Loop")
                                                    
    
####################################
# Miscellaneous
####################################
        
#Creates a new EffectBox of the required type in the required place
def createNewBox(data, typeOfBox, boxPos, name=None):
    if typeOfBox == "Transport":
        transportNum = 6
        numBox = transportNum
    else: numBox = boxPos
    width = data.boxWidth
    height = data.boxHeight
    boxCX = data.width//2
    boxCY = data.offsetHeight + (numBox - 1/2)*height
    
    #Creates a new EffectsBox based on specified type
    if typeOfBox == "Blank":
        return BlankBox(boxCX, boxCY, width, height, numBox)
    elif typeOfBox == "User":
        return UserAudioBox(boxCX, boxCY, width, height, numBox, 
                                    data.boxColors[numBox-1])
    elif typeOfBox == "Transport":
        return Transport(boxCX, boxCY, width, height, numBox, "gray")
    elif typeOfBox == "Insert":
        return InsertedAudioBox(boxCX, boxCY, width, height, numBox, 
                    data.boxColors[numBox-1], name)

def drawMain(canvas, data):
    #Draw background rectangles
    canvas.create_rectangle(0, 0, data.width-1, data.height-1, fill="white")
    canvas.create_rectangle(data.offsetWidth, data.offsetHeight, 
                    19*data.offsetWidth, 19*data.offsetHeight, fill="gray90")
    #Draw title in the top left
    labelCX, labelCY = data.width//6.5, data.height//40
    canvas.create_text(labelCX, labelCY,
                                text="Pydalboard (TP3)", font="Arial 20 italic")
    #Draw each EffectBox
    for effectBox in data.effectBoxes:
        effectBox.draw(canvas, data)
    data.transportBox.draw(canvas, data)
    
def mainMousePress(event, data):
    #Checks the onscreen effectBoxes to see if they were clicked
    for effectBox in data.effectBoxes:
        #If the given EffectsBox is a UserAudioBox, check for clicks at its
        #controls. Otherwise, check for a click for the X button
        if isinstance(effectBox, UserAudioBox):
            effectBox.buttonClicked(event.x, event.y)
            if effectBox.checkForXClick(event.x, event.y):
                boxIndex = data.effectBoxes.index(effectBox)
                data.effectBoxes[boxIndex] = (createNewBox(data, "Blank",
                                                                boxIndex+1))
                
        #Add a new UserAudioBox when a BlankBox is clicked
        elif isinstance(effectBox, BlankBox):
            if effectBox.checkForClick(data, event.x, event.y):
                boxIndex = data.effectBoxes.index(effectBox)
                data.effectBoxes[boxIndex] = (createNewBox(data, "User", 
                                                                    boxIndex+1))
                    
        #If the box is an Inserted Audio Box, check its specific buttons for
        #clicks and also check to see if its X was clicked
        elif isinstance(effectBox, InsertedAudioBox):
            effectBox.checkForClick(event.x, event.y)
            if effectBox.checkForXClick(event.x, event.y):  
                boxIndex = data.effectBoxes.index(effectBox)
                data.effectBoxes[boxIndex] = (createNewBox(data, "Blank",
                                                                boxIndex+1))
    #Check for any clicks on the Transport
    data.transportBox.checkForClick(data, event.x, event.y)
    
####################################
# Animation Framework - Base structure found on 15-112 website (link below)
####################################

#Initializes the program with all the necessary buttons
def init(data):
    #Data for creating effects boxes and other graphical elements
    data.offsetWidth = data.width//20
    data.offsetHeight = data.height//20
    data.numBoxes = 6
    boxCX = data.width//2
    data.boxWidth = (data.width-2*(data.offsetWidth))
    data.boxHeight = (data.height-2*(data.offsetHeight))//data.numBoxes
    data.titleOffset = data.height//6
    data.currentWire = None
    data.currentlyUsedBoxes = 0
    data.boxColors = ["SlateGray1", "SkyBlue1", "dodger blue", "RoyalBlue1", 
                                                                "RoyalBlue4"]
                                                                    
    #Creating all of the BlankBoxes that will be shown on screen at startup
    data.effectBoxes = []
    for i in range(data.numBoxes-1):
        blankBox = createNewBox(data, "Blank", i+1) 
        data.effectBoxes.append(blankBox)
    data.transportBox = createNewBox(data, "Transport", data.numBoxes)                         
    
    #Values for switching modes
    data.mode = "splash"
    data.mainStarted = False
    
#Handles when a user clicks the mouse
def mousePressed(event, data):
    if data.mode == "splash": 
        otherScreens.splashMousePressed(data, event.x, event.y)
    elif data.mode == "main": 
        mainMousePress(event, data)
    elif data.mode == "help": 
        otherScreens.helpMousePressed(data, event.x, event.y)

#Handles when the user presses a certain key
def keyPressed(event, data):
    if event.keysym == "h": 
        if data.mode == "help":
            if data.mainStarted == False: data.mode = "splash"
            if data.mainStarted == True: data.mode = "main"
        else: data.mode = "help"

#Handles events occurring at specific time intervals
def timerFired(data):
    pass

#Continuously redraws the application state
def redrawAll(canvas, data):
    if data.mode == "splash":
        otherScreens.drawSplash(canvas, data)
    elif data.mode == "main":
        drawMain(canvas, data)
    elif data.mode == "help":
        otherScreens.drawHelp(canvas, data)
        
####################################
#Animation run() function - Found on 15-112 website: 
#http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")
    sys.exit()

run(800, 600)