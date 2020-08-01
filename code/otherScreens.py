####################################
# otherScreens.py (TP3)
# Creator: Kieran Walsh
# Andrew ID: kawalsh
####################################

#This file handles the drawing and event handling of the secondary windows,
#the splash screen and the help screen

#Draws the template of the secondary windows
def draw(canvas, data):
    canvas.create_rectangle(0, 0, data.width-1, data.height-1, fill="white")
    canvas.create_rectangle(data.offsetWidth, data.offsetHeight, 
                19*data.offsetWidth, 19*data.offsetHeight, fill="slateGray1")
    marginOffsetY = 10      
    #Draws the gradient on top of the window  
    for i in range(len(data.boxColors)):
        marginOffsetX = (data.width-2*data.offsetWidth)//5
        canvas.create_rectangle(data.offsetWidth+marginOffsetX*i, 
                    data.offsetHeight, data.offsetWidth+marginOffsetX*(i+1), 
                    data.offsetHeight+marginOffsetY, fill=data.boxColors[i])

#Draws one of the buttons used to navigate these secondary windows
def drawButton(canvas, data, cy, btnText):
    data.cx = data.width//2
    data.btnHalfX = data.width//5
    data.btnHalfY = data.width//25
    canvas.create_rectangle(data.cx-data.btnHalfX, cy-data.btnHalfY,
        data.cx+data.btnHalfX, cy+data.btnHalfY, fill="RoyalBlue4")
    canvas.create_text(data.cx, cy, text=btnText, fill="white", 
                                            font="Arial 40 bold italic")

####################################
# Splash screen
####################################
    
#Draws the specific features of the splash screen
def drawSplash(canvas, data):
    data.cyStart = data.height*(7.25/10)
    data.cyHelp = data.height*(8.5/10)
    pedalOffsetW = 40
    pedalOffsetH = 70
    pedalHeight = data.height*(9/20)
    centerXs = [data.width*(1/4), data.width*(3/8), data.width*(1/2), 
                                            data.width*(5/8), data.width*(3/4)]
    
    draw(canvas, data)
    canvas.create_text(data.width//2, data.titleOffset, text="Pydalboard",
        fill="RoyalBlue4", font="Arial " + str(data.width//15) + " bold italic")
    drawButton(canvas, data, data.cyStart,"Start")
    drawButton(canvas, data, data.cyHelp, "Help")
    
    #Draws the pedalboard graphic
    canvas.create_line(data.offsetWidth, pedalHeight, 
            data.width-data.offsetWidth, pedalHeight, width=10, fill="black")
    for i in range(len(data.boxColors)):
        canvas.create_rectangle(centerXs[i]-pedalOffsetW, 
                            pedalHeight-pedalOffsetH, centerXs[i]+pedalOffsetW, 
                            pedalHeight+pedalOffsetH, fill=data.boxColors[i])
                            

#Handles the event of mousePressed while the splash screen is the current mode
def splashMousePressed(data, x, y):
    #Start Button
    if (data.cx-data.btnHalfX <= x <= data.cx+data.btnHalfX and
        data.cyStart-data.btnHalfY <= y <= data.cyStart+data.btnHalfY):
            data.mode = "main"
            data.mainStarted = True
    #Help Button
    elif (data.cx-data.btnHalfX <= x <= data.cx+data.btnHalfX and
        data.cyHelp-data.btnHalfY <= y <= data.cyHelp+data.btnHalfY):
            data.mode = "help"

####################################
# Help screen
####################################

#Returns the text to be used on the Help screen
def getHelpText():
    helpText = \
'''
Pydalboard lets you record and import audio files, play them back, loop them,
and layer them to make your own songs!

NOTE: For best experience use with headphones!! Most features do not require
headphones, but some features, such as Live Mode, may not work properly without
headphones.

Some key features and functions of audio tracks:
    Rec - Record a new audio track
    Play - Play back the current audio track
    Live - Listen to yourself play in real time with FX
    Loop - Continuously loop your audio track
    FX - Add Distortion, Chorus, and Phaser pedals to your track
^Click the button to begin the process, and then again to end it.
    
Key features/functions of the "Transport" Track:
    Insert - Import an existing audio file into your project*
    Loop - Loop all tracks at the same time
    Play - Play all tracks at the same time
    Stop - Stop all tracks
    Save - Export your project as a new audio file

Notes on importing files: (.wav) files only. When prompted, the user must
supply the correct directory and filename of their audio file or that track
will be loaded as empty. It is easiest to move your audio file to the same
directory as the source Python files.

You can refer to this screen at any time by pressing the 'h' key.


'''
    return helpText

#Draws the specific features of the Help window
def drawHelp(canvas, data):
    draw(canvas, data)
    data.cyBackBtn = data.height*(8.5/10)
    helpText = getHelpText()

    canvas.create_text(data.width//2, data.height*(1/7), text="Help",
        fill="RoyalBlue4", font="Arial " + str(data.width//15) + " bold italic")
    canvas.create_text(data.width//2, data.height//2, text=helpText,
        fill="RoyalBlue4", font="Arial " + str(data.width//70) + " bold italic")
    drawButton(canvas, data, data.cyBackBtn, "Back")
    
#Handles the event of mousePressed while Help is the current mode
def helpMousePressed(data, x, y):
    #Back Button
    if (data.cx-data.btnHalfX <= x <= data.cx+data.btnHalfX and
        data.cyBackBtn-data.btnHalfY <= y <= data.cyBackBtn+data.btnHalfY):
            if data.mainStarted: data.mode = "main"
            else: data.mode = "splash"