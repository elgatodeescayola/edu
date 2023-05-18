# This program is free software: you can redistribute it and/or modifydelay
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.p
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2015 - Murilo Faria
# Version: 1.0.5

#TODO:
# playInto toggle and introLength value into INI
# useReplacementName toggle into INI
# load replacement names from INI?

#UPDATE NOTES:
# all the is_p#.wav files should now be is_p_#.wav

import os
import sys
import configparser
import ac
import acsys
import datetime
import calendar
import win32con
from time import clock, localtime, strftime
import codecs, json
import re
import random
import cProfile, pstats, io
#import pygame
import datetime
import azure.cognitiveservices.speech as speechsdk
import threading
import wave
import pyaudio
import queue
import platform
import time
from playsound import playsound



# # Inicializar el módulo de mezcla de Pygame
# pygame.init()
# pygame.mixer.init()
# filenameadelantamiento = "adelantamiento.wav"
# filenameadelantamiento = 'apps\\python\\AnnouncerBot\\adelantamiento.wav'




if platform.architecture()[0] == "64bit":
    sysdir=os.path.dirname(__file__)+'/stdlib64'
else:
    sysdir=os.path.dirname(__file__)+'/stdlib'
sys.path.insert(0, sysdir)
os.environ['PATH'] = os.environ['PATH'] + ";."

def safeText(message):
    validFilenameChars = "-_()=[]{}|/\.,:;`~'\" abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(c for c in message if c in validFilenameChars)

def ConsoleLog(message, showHeader = 1, sanitizeText = 1):
    if showHeader:
        now = clock()
        ac.console("ABot(%0.4f): %s"%(now, message))
        if sanitizeText:
            ac.log("ABot(%0.4f): %s"%(now, safeText(message)))
        else:
            ac.log("ABot(%0.4f): %s"%(now, message))
    else:
        ac.console(message)
        ac.log(safeText(message))

def profile(fnc):
    
    """A decorator that uses cProfile to profile a function"""
    
    def inner(*args, **kwargs):
        
        bSaveToLog = False
        
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats(8)
        
        #ac.console("printing lines")
        
        lines = s.getvalue().split("\n")
        if not "function calls in 0.000 seconds" in lines[0] and not "function calls in 0.001 seconds" in lines[0]: # and not "function calls in 0.002 seconds" in lines[0] :
            if len(lines) > 11:
                bSaveToLog = True
                #ConsoleLog("len(lines) = {}".format(len(lines)))
        
        for line in lines:
            if not line.strip() == "":
                if bSaveToLog:
                    ConsoleLog(line, 0)
                else:
                    ac.console(line)
            
        #print(s.getvalue())
        #ConsoleLog(s.getvalue())
        #ac.console(s.getvalue())
        return retval

    return inner

def f8(x):
    ret = "%8.3f" % x
    if ret != '   0.000':
        return ret
    return "%6dµs" % (x * 10000000)

pstats.f8 = f8


##############################################################################

import AppCom
if True: # __name__ == "__main__":
    AppCom.initialize()
    AppCom.ABot_Enabled = True
    ConsoleLog("AppCom Initialized")
else:
    ConsoleLog("AppCom NOT Initialized")
    
order = ''
oldorder = ''

##############################################################################

import ctypes
from ctypes import wintypes

#from sim_info import info
#import AnnouncerBot_sim_info
import threading
import subprocess
import shlex

import winsound
from shutil import copyfile

try: # Python 3
    from queue import Queue, Empty, Full
except ImportError:
    from queue import Queue, Empty, Full
    import queue as _  # Platform-specific: Windows

import wave
import contextlib
import traceback

###valid file name characters - for getValidFilenames
validFilenameChars = "-_() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


















#CODE TO PRESS SHIFT-CTRL-i	
#import ctypes                  #already imported
#from ctypes import wintypes    #already imported
import time

bIsMutedForIntro = False
intUnmuteCount = 0
intIntroLength = (60 + 24) * 1000 #intro video is 1:23 long

user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

# msdn.microsoft.com/en-us/library/dd375731
VK_TAB  = 0x09
VK_MENU = 0x12
VK_CTRL = 0x11
VK_SHIFT = 0x10
VK_I = 0x49
VK_D = 0x44
VK_M = 0x4D
VK_LCONTROL = 0xA2
VK_LSHIFT = 0xA0

# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize

# Functions

def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def AltTab():
    """Press Alt+Tab and hold Alt key for 2 seconds
    in order to see the overlay.
    """
    PressKey(VK_MENU)   # Alt
    PressKey(VK_TAB)    # Tab
    ReleaseKey(VK_TAB)  # Tab~
    time.sleep(2)
    ReleaseKey(VK_MENU) # Alt~



def ShiftCtrlI():
    global speechDuration #set this so there's no talking during the intro
    ConsoleLog("Pressing Ctrl+Shift+I using user32.SendInput")
    speechDuration = intIntroLength #intro video is 1:23 long
    PressKey(VK_LCONTROL)
    PressKey(VK_LSHIFT)
    PressKey(VK_I)
    time.sleep(0.05)
    ReleaseKey(VK_I)
    ReleaseKey(VK_LSHIFT)
    ReleaseKey(VK_LCONTROL)

def ShiftCtrlM():
    global bIsMutedForIntro #set this so there's no talking during the intro
    global intUnmuteCount
    
    intUnmuteCount = 0    
    bIsMutedForIntro = True
    
    ConsoleLog("Pressing Ctrl+Shift+M using user32.SendInput")
    PressKey(VK_LCONTROL)
    PressKey(VK_LSHIFT)
    PressKey(VK_M)
    time.sleep(0.05)
    ReleaseKey(VK_M)
    ReleaseKey(VK_LSHIFT)
    ReleaseKey(VK_LCONTROL)

def ShiftCtrlD():
    global bIsMutedForIntro #clear this so we know it's no longer muted
    global intUnmuteCount
    
    intUnmuteCount += 1
        
    #we want to try this multiple times
    if intUnmuteCount > 4:
        bIsMutedForIntro = False
    
    ConsoleLog("Pressing Ctrl+Shift+D using user32.SendInput")
    PressKey(VK_LCONTROL)
    PressKey(VK_LSHIFT)
    PressKey(VK_D)
    time.sleep(0.05)
    ReleaseKey(VK_D)
    ReleaseKey(VK_LSHIFT)
    ReleaseKey(VK_LCONTROL)


























#how to load all the relevant values from an ip.ini file? 72_2_195_145.ini and 71_158_91_225.ini
#raceAdmins = ["David Zahn", "Chuck Carter", "Jon Wathen", "Eiran Parsons", "Brad Merys"]    
skipDrivers = ["Esotic Streaming"] #these should be the announcers
reportedIPs = ["72.5.195.145", "71.158.91.225"]
#did not know Python will let you span lines with a dictionary definition
#nextReplacement = 0

nameLookup = {}
nickNames = {}
carNames = {}

reportables = ['NOTHING', 'TYRES', 'LAP_NUMBER', 'NATIONALITY', 'FASTEST_LAP', 'BALLAST', 'MODEL', 'START_POSITION']

replacementNames = ["Ayrton Senna", "Michael Schumacher", "Jackie Stewart", "Jim Clark", "Alain Prost", 
                    "Juan Manuel Fangio", "Mario Andretti", "Stirling Moss", "Niki Lauda", "Nigel Mansell", 
                    "Jack Brabham", "Emerson Fittipaldi", "Alberto Ascari", "Graham Hill", "Richard Petty", 
                    "Dale Earnhardt", "James Hunt", "Dan Gurney", "Jeff Gordon", "John Surtees", 
                    "Damon Hill", "Jimmie Johnson", "Bruce McLaren", "Mark Webber", "Peter Collins",
                    "Mike Hawthorn", "Ronnie Peterson", "Rubens Barrichello", "Lorenzo Bandini", "Kenneth McAlpine",
                    "Chris Amon", "Bob Anderson", "Keith Andrews", "Chuck Arnold", "Ian Ashley", 
                    "Gerry Ashmore", "Jud Larson", "Geoff Lees", "Bill Mackey", "Tony Marsh"]
                    
#AC, PLA
                    
dicNations = {"The Yellow Bee":"de Yelou bii","Austin Powers":"Austin Powers", "Gasinfinmotorsport":"Gasinfin motoresport", "LIBRE":"Equipo LIBRE", "Martini Racing Team":"Martini Reisin Tim","Orange racing team":"Oranch reisin tim","Predators":"Predators"}
#dicNations = {"PT":"Portugal","ALM":"Almería","CAD":"Cádiz","COR":"Córdoba","GRA":"Granada","HUE":"Huelva","JAE":"Jaén","MAL":"Málaga","SEV":"Sevilla","HUE":"Huesca","TER":"Teruel","ZAR":"Zaragoza","AST":"Asturias","BAL":"Balears","LAS":"Las Palmas","SAN":"Santa Cruz de Tenerife","CAN":"Cantabria","AVI":"Ávila","BUR":"Burgos","LEO":"León","PAL":"Palencia","SAL":"Salamanca","SEG":"Segovia","SOR":"Soria","VAL":"Valladolid","ZAM":"Zamora","ALB":"Albacete","CIU":"Ciudad Real","CUE":"Cuenca","GUA":"Guadalajara","TOL":"Toledo","BAR":"Barcelona","GIR":"Girona","LLE":"Lleida","TAR":"Tarragona","ALI":"Alicante","CAS":"Castellón","VAL":"Valencia","BAD":"Badajoz","CAC":"Cáceres","COR":"Coruña","LUG":"Lugo","OUR":"Ourense","PON":"Pontevedra","MAD":"Madrid","MUR":"Murcia","NAV":"Navarra","ALA":"Álava","BIZ":"Bizkaia","GIP":"Gipuzkoa","LA ":"La Rioja","CEU":"Ceuta","MEL":"Melilla" }


driversByNation = {}

dicNumbers = {"1":"primero","2":"segundo","3":"tercero","4":"cuarto","5":"quinto","6":"sexto","7":"séptimo","8":"octavo","9":"noveno","10":"décimo",
              "11":"decimoprimero","12":"decimosegundo","13":"decimotercero","14":"decimocuarto","15":"decimoquinto","16":"decimosexto","17":"decimoséptimo","18":"decimoctavo","19":"decimonoveno","20":"vigésimo",
              "21":"vigesimoprimero","22":"vigesimosegundo","23":"vigesimotercero","24":"vigesimocuarto","25":"vigesimoquinto","26":"vigesimosexto","27":"vigesimoseptimo","28":"vigesioctavo","29":"twenty_ninth","30":"thirtieth",
              "31":"thirty_first","32":"thirty_second","33":"thirty_thurd","34":"thirty_fourth","35":"thirty_fifth","36":"thirty_sixth","37":"thirty_seventh","38":"thirty_eighth","39":"thirty_ninth","40":"fortieth"}

#MAKE ALL THE NECESSARY KEYS ONCE - MAKE SURE THESE GET REINITIALISED IN EACH carId LOOP
keysCarConnected = []
keysCarActive = []
keysCarDistance = []
keysCarInPits = []
keysCarPitLap = []
keysCarOutLap = []
keysCarFirstHalfLap = []
keysCarRacing = []
keysCarBestLap = []
keysCarPoT = []
keysCarRaceTime = []
keysCarRaceLaps = []
keysCarRaceStart = []
keysCarLapCountTest = []
keysCarRaceFinished = []
keysCarRaceFinalized = []
keysCarPosition = []
keysCarCurrPosition = []
keysCarLastPosition = []
keysCarTimePositionChange = []
keysPositionCar = []
keysCarTimeGapAhead = []
keysCarTimeGapBehind = []
keysCarDistanceGapAhead = []
keysCarDistanceGapBehind = []
keysCarLapCount = []
#we don't know the LapTime for other cars
#keysCarLapTime = []
keysCarSpeedKMH = []
keysCarDriverName = []
keysCarSafeName = []
keysCarShortName = []
keysCarLastLapTime = []
keysCarSkipDriver = []
keysCarTyres = []
keysCarPerfMeter = []
keysCarName = []

#Private Keys
keysCarSavedPositions = []
keysCarReportBestLap = []

#From NationFlags directory
#Checked up to Bs
#ABW,AC,AFG,AGO,AIA,ALB,AND,ARE,ARG,ARM,ASM,ATA,ATG,AUS,AUT,AZE,BDI,BEL,BEN,BFA,BGD,BGR,BHR,BHS,BIH,BLR,BLZ,BMU,BOL,BRA,BRB,BRN,BTN,BWA,CAF,CAN,CCK,CHE,CHL,CHN,CIV,CMR,COD,COG,COK,COL,COM,CPV,CRI,CUB,CYM,CYP,CZE,DEU,DJI,DMA,DNK,DOM,DZA,ECU,EGY,ENG,ERI,ESH,ESP,EST,ETH,FIN,FJI,FRA,FRO,FSM,GAB,GBR,GEO,GGY,GHA,GIB,GIN,GMB,GNB,GNQ,GRC,GRD,GRL,GTM,GUM,GUY,HKG,HND,HRV,HTI,HUN,IDN,IMN,IND,IRL,IRN,IRQ,ISL,ISR,ITA,JAM,JEY,JOR,JPN,KAZ,KEN,KGZ,KHM,KIR,KNA,KOR,KWT,LAO,LBN,LBR,LCA,LIE,LKA,LSO,LTU,LUX,LVA,MAC,MAR,MCO,MDA,MDG,MDV,MEX,MHL,MKD,MLI,MLT,MMR,MNE,MNG,MOZ,MRT,MSR,MTQ,MUS,MWI,MYS,NAM,NCL,NER,NGA,NIC,NIR,NLD,NOR,NPL,NRU,NZL,OMN,PAK,PAN,PER,PHL,PLW,PNG,POL,PRI,PRT,PRY,PYF,QAT,ROU,RUS,RWA,SAU,SCT,SDN,SEN,SGP,SLB,SLE,SLV,SMR,SOM,SRB,STP,SUR,SVK,SVN,SWE,SWZ,SYC,SYR,TCA,TCD,TGO,THA,TJK,TKM,TLS,TON,TTO,TUN,TUR,TUV,TWN,TZA,UGA,UKR,URY,USA,UZB,VCT,VEN,VGB,VIR,VNM,VUT,WLS,WSM,YEM,ZAF,ZMB,ZWE.png
                    

#dicTyres
dicTyres = {"nagp_mclaren_mp4-4_r10_A":"on_A._tires","nagp_mclaren_mp4-4_r10_B":"on_B._tires","nagp_mclaren_mp4-4_r10_C":"on_C._tires","nagp_mclaren_mp4-4_r10_D":"on_D._tires","nagp_mclaren_mp4-4_r10_E":"on_E._tires"}
            
dicTracks = {"ks_zandvoort":"Zandvort","vir":"V I R","lilski_calabogie":"CallaBogie","ks_laguna_seca":"Laguna Sayca"}
                    
#Crew Chief Sound folders - take out all references?
#dirABSounds = "C:/Program Files (x86)/Steam/steamapps/common/assettocorsa/apps/python/AnnouncerBot/sounds/dave/"
#this path can be relative
soundsFolder = "dave"
dirABSounds = "apps/python/AnnouncerBot/sounds/%s/"%(soundsFolder)

#OPTIONS TO DISABLE SOME TALKING POINTS
#DRIVER MODE - ONLY DISCUSS WHEN DRIVERS ARE PITTING AND P2PActivations, NO HOTKEYS
#CoHost Mode - ONLY SPEAK WHEN REQUESTED, NO HOTKEYS?

qSpeech = Queue(0)
qVoice = Queue(0)
pVoice = None      
pVoiceTime = 20     #if voice.exe has been speaking for more than 20 seconds then kill it

pVoiceTimeedu = clock()
enviofraseacola = 0 #esto es un contador para que no se envie mas de una frase a la cola

qSkipLength = 12   #if queue is this long then skip some extended information
qSkipOffPace = 4   #don't flood the queue if there's a big wreck
qClockReported = 0 #clock time of the last report
qClockDelay = 10.0 #seconds to wait between additional information edu ponía 10
p2pDelay = 12.0    #seconds to wait before announcing another p2p activation
gapBattles = 0.1   #load these values from the INI?
gapFending = 0.75  #
gapFollowing = 2.5 #
gapTrailing = 5.0  #
soundsOn = 1       #toggle on or off
speechDuration = 0 #how long is current word/phrase
speechTimer = 0    #track how long since last word/phrase spoken
speechDelay = 20   #space to put between words/phrases - was 20 #edu ponía 0
focusedCar = 0     #which car has focus
key_listener = 0   #the listener for hotkeys to control speech
delayTimer = 0  
sessionStartTime = 0
sessionDelay = 6.0    #how long to wait before announcing?
#sessionDelay = 0.1    #how long to wait before announcing?
extraSessionInfo = 1  #should ABot report track info and weather at the start of each session?
sortDelay = 1.000     #how long do we have to wait before assuming sort order is correct?
perfMeterDelay = 20.0 #how long to wait before stating the next namedLocation perf meter update
repetitionDelay = 60.0 #how long to wait before repeating certain types of phrases, like being off pace or entering pits
pitsRepetitionDelay = 10.0 #what's the minimum time to drive through pit lane?
raceStartDelay = 120000.0 #how long do we wait to give extra reportable data?
positionChangeDelay = 4.75 #how long does the position change need to remain to be considered completed? edu pinía 4,75 #edu 1,75
readDriverNamesDelay = 10.0 #check for new driver names every 10 seconds?

#are we announcing all the sessions?
announcePractice = 1
announceQually = 1
announceRace = 1
announceTyreCompounds = 1


#which messages?
msgsPitting = 1    #messages about pit entry and exit?
msgsP2P = 1        #messages about p2p activation?
msgsOffpace = 1    #messages about cars off pace?

#what to call things
ballastName = "kg"

#logging level
verbose = 0

playIntro = 0      #track whether we play an intro or not
playedIntro = 0    #track whether the intro has been played or not

windowx = 105
windowy = 55       # windowx * 0.3 #4181818181818182

appWindow = 0
appWindow1 = 0

lastPOT = 0.0 # "POS0.00"
dic = {}
dicKMH = {}
dicPython = {}
uiDic = {}
uiCars = {}
trackSections = ['NONE']

deltaStringFormat = "%.2f"
alpha = 1.0
backgroundOpacity = 1.0
drawBorderVar = 1

SettingsINI = 'apps\\python\\AnnouncerBot\\AnnouncerBot.ini'
voiceCmd = ''    #equal to nothing? must come from the INI?
voiceCmdINI = '' #the string loaded from the INI

isVoiceTTS = 0

HideIcon = 1

LastStatus = 0
LastSession = -1

displayLabel = 0
displayText = 0
btnToggle = 0

#tipsLabel = 0
verticalAdjust = -1       #ADD TO INI?

trackLength = 0

#Max power rpm

timer = 0.0
recentLapTime = -1.0

colors = {
    "white"      : [255, 255, 255],
    "yellow"     : [255, 255,   0],
    "green"      : [2,   221,  20],
    "red"        : [252,  35,  35],
    "purple"     : [255,0,255],
    "aqua"       : [0,255,255],
    "violet"     : [255,150,255],
    "blue"       : [0,0,255],
    "orange"     : [255,140,0]
}

#order = ''
#oldorder = ''

#####SORTING ROUTINTES###########
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]


#####   Create Custom Class (code from RevHunter)  #####
class Label:
    def __init__(self,appWindow,text = ""):
        self.label = ac.addLabel(appWindow, "  ")
        self.labelText = text
        self.labelSize  = {"width" : 0, "height" : 0}
        self.labelPosition = {"xpos" : 0, "ypos" : 0}
        self.labelFontSize  = 12
        self.labelFontAlign = "left"
        self.labelFontColor = {"red" : 1, "green" : 1, "blue" : 1, "alpha" : 0}

    def setText(self, text):
        self.labelText = text
        ac.setText(self.label, self.labelText)
        return self

    def setSize(self, width, height):
        self.labelSize["width"] = width
        self.labelSize["height"] = height
        ac.setSize(self.label, self.labelSize["width"], self.labelSize["height"])
        return self

    def setPosition(self, xposition, yposition):
        self.labelPosition["xposition"] = xposition
        self.labelPosition["yposition"] = yposition
        ac.setPosition(self.label, self.labelPosition["xposition"],self.labelPosition["yposition"])
        return self

    def setFontSize(self, fontSize):
        self.labelFontSize = fontSize
        ac.setFontSize(self.label, self.labelFontSize)
        return self

    def setFontAlign(self, fontAlign = "left"):
        self.labelFontAlign = fontAlign
        ac.setFontAlignment(self.label, self.labelFontAlign)
        return self

    def setFontColor(self, red, green, blue, alpha):
        self.labelFontColor["red"] = red
        self.labelFontColor["green"] = green
        self.labelFontColor["blue"] = blue
        self.labelFontColor["alpha"] = alpha
        ac.setFontColor(self.label, self.labelFontColor["red"],self.labelFontColor["green"],self.labelFontColor["blue"],self.labelFontColor["alpha"])
        return self



def safeSoundFile(fname):
    #keepcharacters = (' ','.','_','\\','/')
    keepcharacters = (' ','.','_','-')
    
    filename = fname.replace(dirABSounds, "").replace("  ", "_").replace(" ", "_")
    
    return dirABSounds + "".join(c for c in filename if c.isalnum() or c in keepcharacters or re.match(r'\w', c)).rstrip()
    #return "".join([c for c in fname if re.match(r'\w', c)])

def checkSound(fname):
    if not isVoiceTTS:
        fname = safeSoundFile(fname)
    if isVoiceTTS:
        #we no longer have to render these
        return True
    if isVoiceTTS and not os.path.isfile(fname):  # soundsFolder == "voice"
        filename = os.path.basename(fname).replace("_", " ").replace(".wav", "")
        fname = fname.replace("/", "\\")
        FNULL = open(os.devnull, 'w')    #use this if you want to suppress output to stdout from the subprocess

        
        args = voiceCmd%(fname, filename)
        if True:
            #ConsoleLog("subprocess.call %s"%(args))
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            subprocess.call(args, startupinfo=si) #, stdout=FNULL, stderr=FNULL, shell=False)
            
    return os.path.isfile(fname)


 
        
def isVoiceSpeaking():
    global pVoice, pVoiceTime
    
    #this will tell you when it's done running.
    if not pVoice == None:
        try:
            if pVoiceTime > 0:
                #what is an appropriate delay to terminate a process? in seconds
                if clock() - pVoiceTime > 10: #EDU TIEMPOS DE ESPERA DE VOZ, ANTES PONÍA 20
                    #does this work?
                    ConsoleLog("voice.exe assumed to be stuck, killing it")
                    try:
                        #os.kill(pVoice.pid, 0)
                        pVoice.terminate()
                        
                        ConsoleLog("IS PLAYING ES TRUE")
                    except:
                        ConsoleLog("voice.exe kill attempt failed")                         
            #do the kill logic independently of checking the process
            if pVoice.poll() == None:
                
                ConsoleLog("IS PLAYING ES TRUE 2 ")
                
                
                #ConsoleLog("pVoice %d running"%(pVoice.pid))
                return True
            else:
                #ConsoleLog("pVoice %d finished"%(pVoice.pid))
                pVoice = None
                pVoiceTime = 0
                
                return False
        except:
            ConsoleLog("pVoice %d error"%(pVoice.pid))
            #pVoice = 0
    else:
        pVoiceTime = 0
        return False
    
    pVoiceTime = 0
    return False



used_voices = []
phrase_queue = queue.Queue()
def voiceSpeak(message):
    global used_voices
    global phrase_queue

    try:


        if verbose:
            ConsoleLog("voiceSpeak: %s"%(message))

        if dirABSounds in message:
            #if the message is a full file path then reformat into just the spoken phrase
            message = os.path.basename(message).replace("_", " ").replace(".wav", "")

        # Agregar la frase a la cola
        phrase_queue.put(message)

        # Reproducir la siguiente frase en la cola si no se está reproduciendo nada en este momento
        if phrase_queue.qsize() == 1:
            play_next_phrase()

    except Exception as e:
        ac.console("AnnouncerBot: can't voiceSpeak: " + message)
        ac.console(str(e))
        ac.log("AnnouncerBot: can't voiceSpeak: " + message)
        ac.log(str(e))











def play_next_phrase():
    global phrase_queue
    global speech_synthesizer
    global used_voices
    global result

    if not phrase_queue.empty():
        message = phrase_queue.get()
        try:
            #result = speech_synthesizer.speak_text_async(message)
            speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
            speech_config.speech_synthesis_voice_name='es-ES-AlvaroNeural'
            voice_index = randInRange(0, 3)
                
            if voice_index == 0:
                speech_config.speech_synthesis_voice_name='es-ES-ElviraNeural'
            elif voice_index == 1:
                speech_config.speech_synthesis_voice_name='es-ES-EliasNeural'
            elif voice_index == 2:
                speech_config.speech_synthesis_voice_name='es-ES-VeraNeural'
            else:
                speech_config.speech_synthesis_voice_name='es-ES-AlvaroNeural'

            #para que las voces no se superpongan solo puedo utilizar una de ellas, si pongo mas de una , se puperponen.
            #si activo la línea de abajo, ya no se puperpone nada, pero me quedo sin voces distintas.
            #######################################################################speech_config.speech_synthesis_voice_name='es-ES-EliasNeural'      
            speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
            result = speech_synthesizer.speak_text_async(message)
            #result = speech_synthesizer.stop_speaking_async()
            
            #############pVoice = subprocess.Popen(args, shell=True, stdout=None, stdin=None, stderr=None, close_fds=False)
            play_next_phrase()

        except Exception as e:
            ac.console("AnnouncerBot: can't play phrase: " + message)
            ac.console(str(e))
            ac.log("AnnouncerBot: can't play phrase: " + message)
            ac.log(str(e)) 
    
        







import time

# variable para almacenar el tiempo de finalización del sonido actual
soundEndTime = 0

def addSound(soundFile):
    try:
        # Ejecutar el comando "taskkill" para detener "Audiodg.exe"
        # Crear una estructura STARTUPINFO para ocultar la ventana de comandos

        if verbose:
            ConsoleLog(soundFile)
        if not speechDuration == intIntroLength:
            #don't add sounds during the intro
            if not isVoiceTTS:
                soundFile = safeSoundFile(soundFile)
            if qSpeech.qsize() == 0 or qSpeech.qsize() == 1:
                qSpeech.put(soundFile)
        else:
            ConsoleLog("Playing intro, skipping %s"%(soundFile))
    except:
        ac.console("AnnouncerBot: can't add sound: " + soundFile)
        ac.log("AnnouncerBot: can't add sound: " + soundFile)




def playSound(soundFile):
    global soundsPath, soundsOn, qClockReported

        #####EDU COMENTO POR COMPLETO ESTE BLOQUE Y ASÍ AL PRINCIPIO EN OFFLINE NO SE SUPERPONEN LOS AUDIOS, PERO ES ALGO QUE SOLO PASA CON AZURE, CON SUSSY NO OCURRÍA. HAY QUE ESTAR PENDIENTES D
        #####SI SE COME OTRAS FRASES. 

    try:

        if soundsOn and soundFile :
            qClockReported = clock()
            # # speech_config.speech_synthesis_voice_name='es-ES-DarioNeural'
            # # speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
            # # audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
            # # speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)               
            # # speech_synthesis_result = speech_synthesizer.speak_text_async(soundFile)

    except:
        ac.console("AnnouncerBot: can't play sound: " + soundFile + ".wav")
        ac.log("AnnouncerBot: can't play sound: " + soundFile + ".wav")
        








#ESTA FUNCIÓN LA REHAGO POR COMPLETO CON UN WHILE, PARA QUE NO SE SUPERPONGAN LOS MENSAJES DE AUDIO

def playNextSound():
    global speechDuration, speechTimer
    lock = threading.Lock()
    with lock:
        while qSpeech.empty() == False:
            nextSound = qSpeech.get()
            if soundsOn:
                fname = nextSound
                if isVoiceTTS:
                    message = os.path.basename(fname).replace("_", " ").replace(".wav", "")
                    while qSpeech.empty() == False:
                        fname = qSpeech.get()
                        message = message + " " + os.path.basename(fname).replace("_", " ").replace(".wav", "")
                    voiceSpeak(message)
                else:            
                    if checkSound(fname):
                        with contextlib.closing(wave.open(fname,'r')) as f:
                            frames = f.getnframes()
                            rate = f.getframerate()
                            speechDuration = ((frames / float(rate)) * 1000) + speechDelay
                            if isVoiceTTS: # soundsFolder == "voice":
                                speechDuration = speechDuration - 500
                            #ConsoleLog("%s is %d long"%(nextSound, speechDuration))
                        playSound(nextSound)
                        speechTimer = 0
                        while speechTimer < speechDuration:
                            time.sleep(0.1)
                            speechTimer = speechTimer + 100
            else:
                ConsoleLog("Sounds Off, not playing %s"%(nextSound))
        else:
            speechDuration = 0
            speechTimer = 0




# # # # # # Función que inicia el contador
# # # # # def iniciar_contador():
# # # # #     global pVoiceTimeedu
# # # # #     pVoiceTimeedu = time.time()
# # # # #     #pVoiceTimeedu = time.perf_counter()
# # # # #     return pVoiceTimeedu

# # # # # # Función que comprueba el tiempo transcurrido
# # # # # def han_transcurrido_10_segundos(pVoiceTimeedu):
    
# # # # #     if time.time() - pVoiceTimeedu > 10: #espero 10 segundos para que no se superpongan los audios
# # # # #         ConsoleLog("Han transcurrido 10 segundos")
# # # # #         return True
        

# # # # #     else:
# # # # #         ConsoleLog("No han transcurrido 10 segundos")
# # # # #         return False
        










def readPythonINISections():

    #should behaviour change when different apps are enabled?
    from os.path import expanduser
    PythonINI = expanduser("~") + "\\Documents\\Assetto Corsa\\cfg\\python.ini"
    if verbose:
        ConsoleLog("Reading %s"%(PythonINI))
    
    if True:
        #configparser
        SettingsConfig = configparser.ConfigParser()
        if os.path.isfile(PythonINI):
            SettingsConfig.read(PythonINI)
            
            #ConsoleLog("looping sections in config")
            for section in SettingsConfig.sections():
                tmpKey = "ACTIVE"
                if SettingsConfig.has_option(section, tmpKey):
                    if SettingsConfig.getint(section, tmpKey) == 1:
                        tmpKey = "APPS:%s"%(section)
                        dicPython[tmpKey] = 1
                        if verbose:
                            ConsoleLog("App enabled in Python.INI: dicPython[%s] = 1"%(tmpKey))
            
def ABotOnToggle(*args):
    
    #this should toggle the ABot on and off
    hotkey_offset()

    return 1

def makePrivateKeysLists():
    global keysCarSavedPositions, keysCarReportBestLap

    if verbose:
        ConsoleLog("Making Private keyCars lists")
        
    try:
        for carId in range(ac.getCarsCount()):
            strCarId = str(carId)
            strCarKey = "".join(["Car", strCarId])
            
            #MAKE ALL THE NECESSARY KEYS ONCE
            keysCarSavedPositions.append("".join([strCarKey, "SavedPosition"]))
            keysCarReportBestLap.append("".join([strCarKey, "ReportBestLap"]))
            
        if verbose:
            ConsoleLog("DONE Making Private keyCars lists")
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ConsoleLog(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))               

    
                
def makeKeyLists():
    global keysCarConnected, keysCarActive, keysCarDistance, keysCarInPits, keysCarPitLap, keysCarOutLap, keysCarFirstHalfLap, keysCarRacing, keysCarBestLap, keysCarPoT, keysCarRaceTime, keysCarRaceLaps
    global keysCarRaceStart, keysCarLapCountTest, keysCarRaceFinished, keysCarRaceFinalized, keysCarPosition, keysPositionCar, keysCarTimeGapAhead, keysCarTimeGapBehind, keysCarDistanceGapAhead
    global keysCarDistanceGapBehind, keysCarLapCount, keysCarSpeedKMH, keysCarDriverName, keysCarSafeName, keysCarShortName, keysCarLastLapTime, keysCarSkipDriver, keysCarTyres, keysCarPerfMeter
    global keysCarLastPosition, keysCarCurrPosition, keysCarTimePositionChange, keysCarName
    
    if verbose:
        ConsoleLog("Making keyCars lists")
        
    try:
        for carId in range(ac.getCarsCount()):
            strCarId = str(carId)
            strCarKey = "".join(["Car", strCarId])
            #MAKE ALL THE NECESSARY KEYS ONCE - MAKE SURE THESE GET REINITIALISED IN EACH carId LOOP
            keysCarConnected.append("".join([strCarKey, "Connected"]))
            keysCarActive.append("".join([strCarKey, "Active"]))
            keysCarDistance.append("".join([strCarKey, "Distance"]))
            keysCarInPits.append("".join([strCarKey, "InPits"]))
            keysCarPitLap.append("".join([strCarKey, "PitLap"]))
            keysCarOutLap.append("".join([strCarKey, "OutLap"]))
            keysCarFirstHalfLap.append("".join([strCarKey, "FirstHalfLap"]))
            keysCarRacing.append("".join([strCarKey, "Racing"]))
            keysCarBestLap.append("".join([strCarKey, "BestLapTime"]))
            keysCarPoT.append("".join([strCarKey, "PoT"]))
            keysCarRaceTime.append("".join([strCarKey, "RaceTime"]))
            keysCarRaceLaps.append("".join([strCarKey, "RaceLaps"]))
            keysCarRaceStart.append("".join([strCarKey, "RaceStart"]))
            keysCarLapCountTest.append("".join([strCarKey, "LapCountTest"]))
            keysCarRaceFinished.append("".join([strCarKey, "RaceFinished"]))
            keysCarRaceFinalized.append("".join([strCarKey, "RaceFinalized"]))

            #for each car there's a position
            keysCarPosition.append("".join([strCarKey, "Position"]))
            keysCarLastPosition.append("".join([strCarKey, "LastPosition"]))
            keysCarCurrPosition.append("".join([strCarKey, "CurrPosition"]))
            keysCarTimePositionChange.append("".join([strCarKey, "TimePositionChange"]))
            keysPositionCar.append("".join(["Position", strCarId, "Car"]))

            keysCarTimeGapAhead.append("".join([strCarKey, "TimeGapAhead"]))
            keysCarTimeGapBehind.append("".join([strCarKey, "TimeGapBehind"]))
            keysCarDistanceGapAhead.append("".join([strCarKey, "DistanceGapAhead"]))
            keysCarDistanceGapBehind.append("".join([strCarKey, "DistanceGapBehind"]))
            keysCarLapCount.append("".join([strCarKey, "LapCount"]))
            keysCarSpeedKMH.append("".join([strCarKey, "SpeedKMH"]))
            keysCarDriverName.append("".join([strCarKey, "DriverName"]))
            
            keysCarSafeName.append("".join([strCarKey, "SafeName"]))
            keysCarShortName.append("".join([strCarKey, "ShortName"]))
            
            keysCarLastLapTime.append("".join([strCarKey, "LastLapTime"]))
            keysCarSkipDriver.append("".join([strCarKey, "SkipDriver"]))
            keysCarTyres.append("".join([strCarKey, "Tyres"]))
            keysCarPerfMeter.append("".join([strCarKey, "PerfMeter"]))
            keysCarName.append("".join([strCarKey, "Name"]))
            
            
        if verbose:
            ConsoleLog("DONE Making keyCars lists")
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ConsoleLog(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))              
                
def acMain(ac_version):
    global appWindow, appWindow1, HideIcon, displayLabel, trackLength
    global displayText, btnToggle
    #iniciar_contador()
    try:

        makePrivateKeysLists()

        try:
            AppCom.checkValues(1)
            #ConsoleLog("AppCom values checked")
            makeKeyLists()
        except:
            pass

        try:
            #copy the AppCom.py to AutoCam
            src = 'apps/python/AnnouncerBot/AppCom.py'
            dst = 'apps/python/AutoCam/AppCom.py'
            copyfile(src, dst)
        except:
            pass

        try:
            #copy the AppCom.py to BCast
            src = 'apps/python/AnnouncerBot/AppCom.py'
            dst = 'apps/python/BCast/AppCom.py'
            copyfile(src, dst)
        except:
            pass

        try:
            #copy the AppCom.py to BCast
            src = 'apps/python/AnnouncerBot/AppCom.py'
            dst = 'apps/python/Broadcast App/AppCom.py'
            copyfile(src, dst)
        except:
            pass

        if True:
            ConsoleLog("Cleaning up voice.exe processes")
            os.system('wmic process where name="voice.exe" call terminate')
            #ConsoleLog("All Done")
    
        readPythonINISections()
        #loadDriverNationalitiesFromFile()
        
        serverIP = ac.getServerIP()
        serverINI = "apps\\python\\AnnouncerBot\\IP_INIs\\" + serverIP.replace(".", "_") + ".ini"
        if serverIP == "":
            serverINI = "apps\\python\\AnnouncerBot\\IP_INIs\\127_0_0_1.ini"
        
        ReadSettings(SettingsINI)
        ReadSettings(serverINI)

        ReadTrackInfo()
        ReadCarsInfo()
        ReadDriverNames()
        ReadCarNames()
        
        key_listener = threading.Thread(target=listen_key)
        key_listener.daemon = True
        key_listener.start()
        
        #backup this file to maintain a "last working copy"
        src = 'apps/python/AnnouncerBot/AnnouncerBot.py'
        dst = 'apps/python/AnnouncerBot/backup/AnnouncerBot.py'
        copyfile(src, dst)

        src = 'apps/python/AnnouncerBot/AppCom.py'
        dst = 'apps/python/AnnouncerBot/backup/AppCom.py'
        copyfile(src, dst)

        if extraSessionInfo:            
            #generate a random number between 1 and 6
            numero = random.randint(1, 6)
            

            #bIsMutedForIntro = True                
            #qSpeech.queue.clear()
            #dic.clear()                                
            #sessionStartTime = clock()


            #if numero is 1 then say "carrera patrocinada por sim tec pro"
            if numero == 1:
                addSound(dirABSounds + "Una carrera de UVE ERRE ESE patrocinada por sim tec pro.wav")
            #if numero is 2 then say "empieza la emocionante carrera"
            elif numero == 2:
                addSound(dirABSounds + "empieza una emocionante carrera de UVE ERRE ESE patrocinada por sim tec pro.wav")
            #if numero is 3 then say "la competencia comienza ahora"
            elif numero == 3:
                addSound(dirABSounds + "la competición comienza ahora. carrera de UVE ERRE ESE patrocinada por sim tec pro.wav")
            #if numero is 4 then say "los autos están listos para la carrera"
            elif numero == 4:
                addSound(dirABSounds + "los pilotos están listos para esta carrera de UVE ERRE ESE patrocinada por sim tec pro.wav")
            #if numero is 5 then say "se inicia la batalla en la pista"
            elif numero == 5:
                addSound(dirABSounds + "se inicia la batalla de pilotos en la pista por cortesía de UVE ERRE ESE Y PATROCINADA POR sim tec pro.wav")
            #if numero is 6 then say "comienza la carrera de la temporada"
            elif numero == 6:
                addSound(dirABSounds + "comienza la carrera de la temporada EN UVE ERRE ESE  de la mano de sim tec pro.wav")




###############################################################################################################

        ## EDU VENTANA DE BOX,BOX,BOX Crea una ventana de la aplicación de 800x800
        #appWindow1 = ac.newApp("BOX")
        #ac.setSize(appWindow1, 500, 200)
        
        #ac.drawBorder(appWindow1, drawBorderVar)

        ## Posiciona la ventana en el centro de la pantalla
        #ac.setPosition(appWindow1, 800, 400)

        ## Muestra la ventana
        #ac.setBackgroundColor(appWindow1, (255, 0, 0))
        #ac.setBackgroundOpacity(appWindow1, 0.0)
        
        ## Dibuja una etiqueta en la posición (100, 100) con el texto "BOX" y el color rojo
        ##ac.addLabel(appWindow1, "BOX", 100, 100, 20, (255, 0, 0))
        #ac.setVisible(appWindow1, True)



################################################################################################################
        appWindow = ac.newApp("AnnouncerBot")
        
        ac.addOnChatMessageListener(appWindow,onChatMessage)
            
        ac.setSize(appWindow, windowx, windowy)
        
        btnToggle = ac.addButton(appWindow, "On")
        ac.setPosition(btnToggle, 5, 25)
        ac.setSize(btnToggle, 95, 25)
        ac.setFontSize(btnToggle, 16)
        if verbose:
            ConsoleLog("Adding Click Listener")
        ac.addOnClickedListener(btnToggle, ABotOnToggle)        
        ConsoleLog("Added Click Listener")
        
        if verbose:
            ConsoleLog("Setting Text")
            
        if soundsOn:
            ac.setText(btnToggle, "ABot ON")
        else:
            ac.setText(btnToggle, "ABot OFF")
    
        if verbose:
            ConsoleLog("Set Text")
    
        #displayText = ac.addTextInput(appWindow,"1^10|2^9|3^8|4^7|5^6|6^5|7^4|8^3|9^2|10^1")
        #ac.setVisible(displayText, 1)
    
        if HideIcon:
            ac.setIconPosition(appWindow, 0, -9000)

        ac.setTitle(appWindow, "Announcer Bot")

        #trackSPlineLength
        trackLength = AppCom.dic["TrackSplineLength"]
        if verbose:
            ConsoleLog("Spline Length = %0.6f"%(trackLength))
        
        if trackLength == 0:
            trackLength = ac.getTrackLength(0)
            ConsoleLog("Track Length = %0.6f"%(trackLength))

        #ConsoleLog("Adding Click Listener - SKIPPED FOR TESTING")
        #ac.addOnClickedListener(displayLabel, ABotOnToggle)
        #ConsoleLog("Added Click Listener - SKIPPED FOR TESTING")
        
        if verbose:
            #ConsoleLog("looping cars to report driver names")
            for car in range(ac.getCarsCount()):
                ConsoleLog("Car %d driverName = %s"%(car, safeName(car)))
        
        return "AnnouncerBot"
    
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ac.console('ABot acMain Error (logged to file)')
        ac.log(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    
    
def timeToMinSecMsecTuple(t):
    mins = t // (60*1000)
    secs = (t - 60*1000*mins) // 1000
    msecs = (t - 60*1000*mins - secs*1000)
    return (mins, secs, msecs)

def formatTime(t):
    mins, secs, msecs = timeToMinSecMsecTuple(abs(t))
    time = "%02d:%02d.%03d" % (mins, secs, msecs)
    return time

def formatLapTime(t):
    mins, secs, msecs = timeToMinSecMsecTuple(abs(t))
    msecs = msecs / 100
    time = "%01d:%02d.%1d" % (mins, secs, msecs)
    return time

def formatLapTime3Digits(t):
    mins, secs, msecs = timeToMinSecMsecTuple(abs(t))
    #msecs = msecs / 100
    time = "%01d:%02d.%03d" % (mins, secs, msecs)
    time = "%01d:%02d:%03d" % (mins, secs, msecs)    
    return time    

def formatGap3Digits(t):
    mins, secs, msecs = timeToMinSecMsecTuple(abs(t))
    #msecs = msecs / 100
    if mins == 0:
        if secs == 0:
            time = "con%03d" % (msecs)
        else:
            time = "%d.%03d" % (secs, msecs)
            time = "%d:%03d" % (secs, msecs)
    else:
        time = "%01d:%02d.%03d" % (mins, secs, msecs)
        time = "%01d:%02d:%03d" % (mins, secs, msecs)
        
    return time    
    
def formatSplit(t):
    mins, secs, msecs = timeToMinSecMsecTuple(abs(t))

    if mins > 0:
        secs = (mins * 60) + secs

    return "%02d.%03d" % (secs, msecs)

def formatDiff(t):
    mins, secs, msecs = timeToMinSecMsecTuple(abs(t))

    if mins > 0:
        secs = (mins * 60) + secs

    if t < 0:
        pre = "-"
    else:
        pre = "+"
        
    return pre + "%01d.%03d" % (secs, msecs)

def formatDelta(t, format):
    mins, secs, msecs = timeToMinSecMsecTuple(abs(t))

    if mins > 0:
        secs = (mins * 60) + secs

    if t < 0:
        pre = "-"
    else:
        pre = "+"

    time = secs + (msecs / 1000.0)
        
    #return pre + "%01d.%02d" % (secs, msecs)
    #return pre + "%.2f" % time
    return pre + format % time

def formatDeltaNumOnly(t):
    mins, secs, msecs = timeToMinSecMsecTuple(abs(t))

    if mins > 0:
        secs = (mins * 60) + secs

    time = secs + (msecs / 1000.0)
    
    if t < 0:
        time = time * -1
    
    #return pre + "%01d.%02d" % (secs, msecs)
    return time

def formatDeltaNumOnlyHundreths(t):
    mins, secs, msecs = timeToMinSecMsecTuple(abs(t))

    if mins > 0:
        secs = (mins * 60) + secs

    time = secs + (msecs / 1000.0)
    
    if t < 0:
        time = time * -1
    
    return "%01d.%02d" % (secs, msecs)
    #return time
    
def rgb(color, a = 1.0, bg = False):
    r = color[0] / 255
    g = color[1] / 255
    b = color[2] / 255
    if bg == False:
        return r, g, b, a
    else:
        return r, g, b
    
    
def WriteSettings():
    global SettingsINI #, HideIcon, windowx, deltaStringFormat

    try:
        section = 'SETTINGS'
                
        ConsoleLog("Writing AnnouncerBot Setting to file")
                
        SettingsConfig = configparser.ConfigParser()
        if os.path.isfile(SettingsINI):
            ConsoleLog("READING %s"%(SettingsINI))
            SettingsConfig.read(SettingsINI)
        else:
            ac.console("AnnouncerBot writing new AnnouncerBot.ini")

        if not SettingsConfig.has_section(section):
            SettingsConfig.add_section(section)
        
        SettingsConfig.set(section,'HideIcon','%d' % HideIcon)
        SettingsConfig.set(section,'AppWidth','%d' % windowx)
        SettingsConfig.set(section,'AppHeight','%d' % windowy)
        SettingsConfig.set(section,'backgroundOpacity', '%0.1f' % backgroundOpacity)
        SettingsConfig.set(section,'drawBorder','%d' % drawBorderVar)
        #soundsFolder
        SettingsConfig.set(section,'soundsFolder','%s'%soundsFolder)
        #announcePractice
        SettingsConfig.set(section,'announcePractice','%d' % announcePractice)
        #announceQually
        SettingsConfig.set(section,'announceQually','%d' % announceQually)
        #announceRace
        SettingsConfig.set(section,'announceRace','%d' % announceRace)
        #announceTyreCompounds
        SettingsConfig.set(section,'announceTyreCompounds','%d' % announceTyreCompounds)
        #readDriverNamesDelay
        SettingsConfig.set(section,'readDriverNamesDelay','%0.1f' % readDriverNamesDelay)
        #ballastName
        SettingsConfig.set(section,'ballastName','%s' % ballastName)
        #verbose
        SettingsConfig.set(section,'verbose','%d' % verbose)
        #voiceCmd = apps\\python\\AnnouncerBot\\voice.exe -n "Microsoft David Desktop" --mono --khz 22 -o OUTPUTFILE TEXTTOSPEECH
        #ConsoleLog("210 voiceCmd = %s"%(voiceCmdINI))
        SettingsConfig.set(section,'voiceCmd','%s' % voiceCmdINI)
        #isVoiceTTS = 1
        SettingsConfig.set(section,'isVoiceTTS','%d' % isVoiceTTS)
        
        ConsoleLog("ADDING COMMENTS")
        with open(SettingsINI, 'w') as configfile:
            configfile.write(';Set Values to 1 to turn them on, 0 to turn them off.' + '\n')
            configfile.write(';HideIcon hides AC icon.' + '\n')
            configfile.write(';Default AppWidth is 110.  Change this value to resize the app larger/smaller.' + '\n')
            configfile.write(';Default backgroundOpacity is 1.0, but you can set it anywhere from 0.0 (transparent) to 1.0 (fully opaque).' + '\n')
            configfile.write(';drawBorder toggles drawing the app border.' + '\n')
            #soundsFolder
            configfile.write(';soundsFolder default is dave. if you make a new sounds folder change this value.' + '\n')
            configfile.write(';replacementNames = Ayrton Senna|Michael Schumacher|Jackie Stewart|Jim Clark|Alain Prost|Juan Manuel Fangio|Mario Andretti|Stirling Moss|Niki Lauda|Nigel Mansell|Jack Brabham|Emerson Fittipaldi|Alberto Ascari|Graham Hill|Richard Petty|Dale Earnhardt|James Hunt|Dan Gurney|Jeff Gordon|John Surtees|Damon Hill|Jimmie Johnson|Bruce McLaren|Mark Webber|Peter Collins|Mike Hawthorn|Ronnie Peterson|Rubens Barrichello|Lorenzo Bandini|Kenneth McAlpine|Chris Amon|Bob Anderson|Keith Andrews|Chuck Arnold|Ian Ashley|Gerry Ashmore|Jud Larson|Geoff Lees|Bill Mackey|Tony Marsh' + '\n')
            configfile.write(';replacementNames = Player 1|Player 2|Player 3|Player 4|Player 5|Player 6|Player 7|Player 8|Player 9|Player 10|Player 11|Player 12|Player 13|Player 14|Player 15|Player 16|Player 17|Player 18|Player 19|Player 20|Player 21|Player 22|Player 23|Player 24|Player 25|Player 26|Player 27|Player 28|Player 29|Player 30|Player 31|Player 32|Player 33|Player 34|Player 35|Player 36|Player 37|Player 38|Player 39|Player 40' + '\n')
            configfile.write(';soundsfolder = voice' + '\n')
            configfile.write(';voiceCmd = apps\\python\\AnnouncerBot\\voice.exe -n "Microsoft David Desktop" --mono --khz 22 -o OUTPUTFILE TEXTTOSPEECH' + '\n')
            configfile.write(';isVoiceTTS = 1' + '\n')
            configfile.write(';OPTIONAL for TTS namelookup = Bjoern Hehmann^Bjorn Hayman|Kevin Lechmanski^Kevin LechManski' + '\n')
            configfile.write(';OPTIONAL ballastname = _keilos' + '\n')
            configfile.write(';verbose = 0 - controls the logging level, for debug purposes only' + '\n')
            configfile.write(';readDriverNamesDelay = 10.0 - how often to check driverNames.txt for new names.  Set to 0.0 to skip checking.' + '\n')
            
            configfile.write(';' + '\n')
            configfile.write(';all of the reportables are optional and can be removed from the list to be skipped, or duplicated to increase frequency' + '\n')
            configfile.write(';reportables = NOTHING|TYRES|LAP_NUMBER|NATIONALITY|FASTEST_LAP|BALLAST|MODEL|START_POSITION' + '\n')
            configfile.write(';Example of three NOTHING options along with TYRES, NATIONALITY, and BALLAST' + '\n')
            configfile.write(';reportables = NOTHING|NOTHING|NOTHING|TYRES|NATIONALITY|BALLAST' + '\n')
            
            ConsoleLog("WRITING: %s"%(SettingsINI))
            SettingsConfig.write(configfile)
            ConsoleLog("WRITTEN")

        ConsoleLog("DONE WRITING INI")
        return 1        

    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ac.console('WriteSettings Error (logged to file)')
        ac.log(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            
def getValidFileName(filename):
    return "".join(c for c in filename if c in validFilenameChars)

def safeName(car):
    #can we trust the name straight from AC?
    if True:
        return ac.getDriverName(car).replace("|", " ").replace("^", " ")
    else: #or do we need to sanitize it?
        validFilenameChars = "-_() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return "".join(c for c in ac.getDriverName(car) if c in validFilenameChars)

        
def ReadDriverNames():
    global nickNames
    
    try:
        #ConsoleLog("Checking ReadDriverNames")
    
        Name_File = 'apps\\python\\AnnouncerBot\\driverNames.txt'
        
        serverIP = ac.getServerIP()
        Name_File_IP = "apps\\python\\AnnouncerBot\\IP_INIs\\driverNames_" + serverIP.replace(".", "_") + ".txt"
        if os.path.isfile(Name_File_IP):
            Name_File = Name_File_IP
        
        if os.path.isfile(Name_File):
            bLoadDriverNames = True
            tmpKey = "DriverNamesModifiedTime"
            if tmpKey in uiDic:
                if uiDic[tmpKey] == "%0.4f"%os.path.getmtime(Name_File):
                    #ConsoleLog("No Need to Reload Driver Names")
                    bLoadDriverNames = False
        
            if bLoadDriverNames:
                ConsoleLog("ReadDriverNames from %s"%(Name_File))
                with open(Name_File, 'r')as f:
                    driverNames = f.readlines()
                    #ConsoleLog("looping lines to read driver names")
                    for row in range(len(driverNames)):
                        if "|" in driverNames[row] and not driverNames[row].startswith(";"):
                            driverName, nickNameList = driverNames[row].split("|")
                            #ConsoleLog("DriverName = %s, nickNames = %s"%(driverName, nickNameList))
                            nickNames[driverName] = nickNameList.strip().split("^")
                            if verbose > 0:
                                ConsoleLog("nickNames[%s] = %s"%(driverName, nickNames[driverName]))
                        else:
                            if verbose:
                                ConsoleLog("Skipping %s"%(driverNames[row]))
                        
                uiDic[tmpKey] = "%0.4f"%os.path.getmtime(Name_File)
        else:
            ConsoleLog("ReadDriverNames File NOT Found")
            
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #ac.console('AutoCam ReadCars Error (logged to file)')
        #ac.log(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))    
        ConsoleLog(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))    

def ReadCarNames():
    global carNames #nickNames
    
    try:
        Name_File = 'apps\\python\\AnnouncerBot\\carNames.txt'
        if os.path.isfile(Name_File):
            ConsoleLog("ReadCarNames from %s"%(Name_File))
            with open(Name_File, 'r')as f:
                namesFromFile = f.readlines()
                #ConsoleLog("looping lines to read driver names")
                for row in range(len(namesFromFile)):
                    if "|" in namesFromFile[row] and not namesFromFile[row].startswith(";"):
                        driverName, nickNameList = namesFromFile[row].split("|")
                        #ConsoleLog("DriverName = %s, carNames = %s"%(driverName, nickNameList))
                        carNames[driverName] = nickNameList.strip().split("^")
                        if verbose > 0:
                            ConsoleLog("carNames[%s] = %s"%(driverName, carNames[driverName]))
                    else:
                        if verbose:
                            ConsoleLog("Skipping %s"%(namesFromFile[row]))
                    
    
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #ac.console('AutoCam ReadCars Error (logged to file)')
        #ac.log(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))    
        ConsoleLog(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))    

    
def ReadCarsInfo():
    global uiCars
    
    if verbose:
        ConsoleLog("Reading CARS Info")
    
    uniqueModels = "uniqueModels"
    uiCars[uniqueModels] = 0
    uniqueMakes = "uniqueMakes"
    uiCars[uniqueMakes] = 0
    
    #ConsoleLog("looping cars to read info")
    for car in range(0, ac.getCarsCount()):
        tmpKey = "Model%s"%ac.getCarName(car)
        if not tmpKey in uiCars:
            uiCars[tmpKey] = 1
            uiCars[uniqueModels] = uiCars[uniqueModels] + 1
            #content\cars\ks_mercedes_190_evo2\ui\ui_car.json
            try:
                jsonCar = "content\\cars\\" + ac.getCarName(car) + "\\ui\\ui_car.json"
                if os.path.isfile(jsonCar):
                    if verbose:
                        ConsoleLog("Reading %s"%(jsonCar))
                    
                    with codecs.open(jsonCar, "r", "utf-8-sig") as uiFile:
                        uiDataString = uiFile.read().replace('\r', '').replace('\n', '').replace('\t', '')
                    strErr = "1030"
                    uiTemp = json.loads(uiDataString)
                    
                    #with open(jsonCar) as f:
                    #    uiTemp = json.load(f)
                    #read the JSON
                    if verbose:
                        ConsoleLog("CAR name = %s"%(uiTemp["name"]))

                    #tmpKey = "Car-%s-Model"%(ac.getCarName(car))                    
                    #tmpKey = "Car-%s-Make"%(ac.getCarName(car))
                    
                    tmpKey = "Car-%s-Model"%(ac.getCarName(car))
                    uiCars[tmpKey] = uiTemp["name"]
                    
                    if verbose:
                        ConsoleLog("CAR brand = %s"%(uiTemp["brand"]))

                    tmpKey = "Car-%s-Make"%(ac.getCarName(car))
                    uiCars[tmpKey] = uiTemp["brand"]
                    
                    if not "Make%s"%uiTemp["brand"] in uiCars:
                        uiCars["Make%s"%uiTemp["brand"]] = 1
                        uiCars[uniqueMakes] = uiCars[uniqueMakes]  + 1
                    
                    if verbose:
                        ConsoleLog("FINISHED READING JSON")
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                ac.console('ReadCarsInfo Error (logged to file)')
                ac.log(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))    

    ConsoleLog("uiCars[%s] = %d"%(uniqueModels, uiCars[uniqueModels]))
    ConsoleLog("uiCars[%s] = %d"%(uniqueMakes, uiCars[uniqueMakes]))
                
def writeCarNames():
    global carNames
    
    strFileContents = ""
    
    try:
        Name_File = 'apps\\python\\AnnouncerBot\\carNames.txt'
        if os.path.isfile(Name_File):
            ConsoleLog("ReadCarNames from %s"%(Name_File))
            with open(Name_File, 'r')as f:
                fileCarNames = f.readlines()
                strFileContents = driverName
                #ConsoleLog("looping fileCarNames")
                for row in range(len(fileCarNames)):
                    if "|" in fileCarNames[row] and not fileCarNames[row].startswith(";"):
                        driverName, nickNameList = fileCarNames[row].split("|")
                        #ConsoleLog("DriverName = %s, carNames = %s"%(driverName, nickNameList))
                        carNames[driverName] = nickNameList.strip().split("^")
                        if verbose > 0:
                            ConsoleLog("carNames[%s] = %s"%(driverName, carNames[driverName]))
                    else:
                        if verbose:
                            ConsoleLog("Skipping %s"%(fileCarNames[row]))
                    
                    
        #any car that's not already in the carNames.txt should get a row, with any relevant data
        #scan the whole AC cars folder structure and open the JSON files?
    
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #ac.console('AutoCam ReadCars Error (logged to file)')
        #ac.log(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))    
        ConsoleLog(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))    
    

                
def ReadTrackInfo():
    global uiDic, trackSections
    
    #content\tracks\asrl_knockhill\ui\knockhill\ui_track.json
    #ac.getTrackName(0) + getValidFileName(ac.getTrackConfiguration(0)
    try:
   
        uiTrack = "content\\tracks\\" + ac.getTrackName(0) + "\\ui\\" + ac.getTrackConfiguration(0) + "\\ui_track.json" 
        if ac.getTrackConfiguration(0) == "":
            uiTrack = "content\\tracks\\" + ac.getTrackName(0) + "\\ui\\ui_track.json" 
            
        tmpJSON = "apps\\python\\AnnouncerBot\\TrackInfo\\" + ac.getTrackName(0) + "_" + ac.getTrackConfiguration(0) + ".json" 
        if ac.getTrackConfiguration(0) == "":
            tmpJSON = "apps\\python\\AnnouncerBot\\TrackInfo\\" + ac.getTrackName(0) + ".json" 
        
        if os.path.isfile(tmpJSON):
            uiTrack = tmpJSON
        elif os.path.isfile(uiTrack):
            ConsoleLog("Copying %s to %s"%(uiTrack, tmpJSON))
            copyfile(uiTrack, tmpJSON)            
            
        if os.path.isfile(uiTrack):
            bLoadTrackInfo = True
        
            #os.path.getmtime(path)
            tmpKey = "TrackInfoModifiedTime"
            if tmpKey in uiDic:
                if uiDic[tmpKey] == "%0.4f"%os.path.getmtime(uiTrack):
                    #ConsoleLog("No Need to Reload uiTrack")
                    bLoadTrackInfo = False

            if bLoadTrackInfo:
                ConsoleLog("Reading %s"%(uiTrack))
                with open(uiTrack) as f:
                    uiDic = json.load(f)
                #read the JSON
                #uiDic = json.loads(uiTrack)

                uiDic[tmpKey] = "%0.4f"%os.path.getmtime(uiTrack)
                
                if verbose:
                    ConsoleLog("Description = %s"%(uiDic["description"]))
                    ConsoleLog("Country = %s"%(uiDic["country"]))
                    ConsoleLog("City = %s"%(uiDic["city"]))
                    ConsoleLog("Length = %s"%(uiDic["length"]))
                    ConsoleLog("Width = %s"%(uiDic["width"]))
                    ConsoleLog("PitBoxes = %s"%(uiDic["pitboxes"]))
                    ConsoleLog("Run = %s"%(uiDic["run"]))
                    ConsoleLog("FINISHED READING JSON")
                    ConsoleLog("uiDic[%s] = %s"%(tmpKey, uiDic[tmpKey]))
            
                if uiDic["description"] is None:
                    ConsoleLog("uiDic['description'] IS NULL")
                    if "name" in uiDic and not uiDic["name"] is None:
                        uiDic["description"] = uiDic["name"]
                    else:
                        del uiDic["description"]
                
            
            
        sectionsINI = "content\\tracks\\" + ac.getTrackName(0) + "\\" + ac.getTrackConfiguration(0) + "\\data\\sections.ini" 
        if ac.getTrackConfiguration(0) == "":
            sectionsINI = "content\\tracks\\" + ac.getTrackName(0) + "\\data\\sections.ini"
            
        tmpINI = "apps\\python\\AnnouncerBot\\sections\\" + ac.getTrackName(0) + "_" + ac.getTrackConfiguration(0) + ".ini" 
        if ac.getTrackConfiguration(0) == "":
            tmpINI = "apps\\python\\AnnouncerBot\\sections\\" + ac.getTrackName(0) + ".ini" 
            
        if os.path.isfile(tmpINI):
            sectionsINI = tmpINI
        elif os.path.isfile(sectionsINI):
            ConsoleLog("Copying %s to %s"%(sectionsINI, tmpINI))
            copyfile(sectionsINI, tmpINI)
        else:
            ConsoleLog("NOT FOUND: %s"%(sectionsINI))
            
        if os.path.isfile(sectionsINI):
            bLoadSectionInfo = True
        
            #os.path.getmtime(path)
            tmpKey = "SectionModifiedTime"
            if tmpKey in uiDic:
                if uiDic[tmpKey] == "%0.4f"%os.path.getmtime(sectionsINI):
                    #ConsoleLog("No Need to Reload sectionsINI")
                    bLoadSectionInfo = False

            if bLoadSectionInfo:
                ConsoleLog("Reading %s"%(sectionsINI))
                uiDic[tmpKey] = "%0.4f"%os.path.getmtime(sectionsINI)
                
                if verbose:
                    ConsoleLog("uiDic[%s] = %s"%(tmpKey, uiDic[tmpKey]))
                    
                #[SECTION_0]
                #IN=0.024
                #OUT=0.065
                #TEXT=Turn 1
                config = configparser.ConfigParser()
                try:
                    config.read(sectionsINI)
                except:
                    ConsoleLog("Error Reading %s, trying utf-8-sig"%(sectionsINI))
                    config.read(sectionsINI, "utf-8-sig")
                    if False:
                        #config.read_file(codecs.open(sectionsINI, "r", "utf-8-sig"))
                        ConsoleLog("150")
                        with codecs.open(sectionsINI, "r", "utf-8-sig") as dataFile:
                            ConsoleLog("170")
                            dataString = dataFile.read().replace('\r', '').replace('\n', '').replace('\t', '')
                        ConsoleLog("190")
                        config.read_string(dataString)
                        ConsoleLog("195")
                        pass
                trackSections = config.sections()
                #ConsoleLog("looping sections to read INI files")
                for section in trackSections:
                    #ConsoleLog("330: Reading %s"%(section))
                    if False:
                        if config.has_section(section):
                            sectionOptions = config.options(section)

                            if verbose:
                                ConsoleLog("%s FOUND"%(section))
                                ConsoleLog("Reading Options")
                                ConsoleLog("Options = %s"%(sectionOptions))
                            #for option in sectionOption:
                                
                        else:
                            ConsoleLog("%s NOT FOUND"%(section))
                        
                    if True:
                        if config.has_option(section, "IN") and config.has_option(section, "OUT") and config.has_option(section, "TEXT"):
                            try:
                                uiDic["%s_IN"%(section)] =  config.getfloat(section, 'IN')
                                uiDic["%s_OUT"%(section)] =  config.getfloat(section, 'OUT')
                                uiDic["%s_TEXT"%(section)] =  config.get(section, 'TEXT').replace('\\', ' ').replace('/', ' ').split('^')
                                if config.has_option(section, "TTS"):
                                    uiDic["%s_TEXT"%(section)] =  config.get(section, 'TTS').replace('\\', ' ').replace('/', ' ').split('^')
                                #uiDic["%s_TEXT"%(section)] = uiDic["%s_TEXT"%(section)].replace('\\', ' ').replace('/', ' ')
                                if verbose:
                                    ConsoleLog("%s from %0.2f to %0.2f"%(uiDic["%s_TEXT"%(section)], uiDic["%s_IN"%(section)], uiDic["%s_OUT"%(section)]))
                            except:
                                pass
    except:
        ConsoleLog("Error Reading Track Info: check the relevant files for duplicate sections or improper formatting")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ac.console('ReadTrackInfo Error (logged to file)')
        ac.log(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    
def ReadSettings(INI_File):
    global HideIcon, deltaStringFormat, backgroundOpacity, drawBorderVar, reportables
    global windowx, windowy, skipDrivers, replacementNames, readDriverNamesDelay
    global soundsFolder, dirABSounds, announcePractice, announceQually, announceRace
    global voiceCmd, voiceCmdINI, isVoiceTTS, announceTyreCompounds, ballastName, verbose
    #SettingsINI
    
    try:
        if os.path.isfile(INI_File):
            ConsoleLog("Reading Settings from %s"%(INI_File))
            section = 'SETTINGS'
            SettingsConfig = configparser.ConfigParser()
            SettingsConfig.read(INI_File)
            boolWriteSettings = False
                     
                
            #from datetime import date
            tdate = datetime.date.today()
            DAY = calendar.day_name[tdate.weekday()]

            #hard code this for testing
            #DAY = "Thursday"
            
            if SettingsConfig.has_option(section, DAY):  
                if verbose:
                    ConsoleLog("Loading skipDrivers for %s"%(DAY))
                skipDrivers = SettingsConfig.get(section, DAY).split("|") #in the python
                AppCom.setSkipDrivers(SettingsConfig.get(section, DAY))
            elif SettingsConfig.has_option(section, 'skipDrivers'): 
                if verbose:
                    ConsoleLog("Loading skipDrivers")
                skipDrivers = SettingsConfig.get(section, 'skipDrivers').split("|") #in the python
                AppCom.setSkipDrivers(SettingsConfig.get(section, 'skipDrivers'))

            if verbose:
                ConsoleLog("skipDrivers %s"%(skipDrivers))
            #for strDriver in skipDrivers:
            #    ConsoleLog("Skipping %s"%(strDriver))

            if SettingsConfig.has_option(section, "replacementNames"):
                ConsoleLog("Loading replacementNames from the INI")
                replacementNames = SettingsConfig.get(section, "replacementNames").split("|") #in the python
            else:
                if verbose:
                    ConsoleLog("replacementNames not found")
            #    boolWriteSettings = True

            #reportables
            if SettingsConfig.has_option(section, "reportables"):  
                #ConsoleLog("Loading reportables from the INI")
                reportables = SettingsConfig.get(section, "reportables").split("|") #in the python
            #else:
            #    ConsoleLog("reportables not found")
            #    boolWriteSettings = True            
            
            if verbose:
                ConsoleLog("Reportables %s"%(reportables))
            
            #for reportable in reportables:
            #    ConsoleLog("Reportable: %s"%(reportable))
                
            if len(reportables) > 0:
                i = 0
                while i < len(reportables):
                    #ConsoleLog("Reportable[%d]: %s"%(i, reportables[i]))
                    i = i + 1
             
            #voiceCmd
            if SettingsConfig.has_option(section, "voiceCmd"):  
                if verbose:
                    ConsoleLog("Loading voiceCmd from the INI")
                voiceCmdINI = SettingsConfig.get(section, "voiceCmd")
                voiceCmd = voiceCmdINI.replace("OUTPUTFILE", "%s").replace("TEXTTOSPEECH", "%s") #in the python
            else:
                if verbose:
                    ConsoleLog("voiceCmd not found")
                boolWriteSettings = True
                
            #isVoiceTTS
            if SettingsConfig.has_option(section, 'isVoiceTTS'):  
                if verbose:
                    ConsoleLog("Loading isVoiceTTS from the INI")
                isVoiceTTS = SettingsConfig.getint(section, 'isVoiceTTS')    
            else:
                if verbose:
                    ConsoleLog("isVoiceTTS not found")
                boolWriteSettings = True
     
            if SettingsConfig.has_option(section, 'HideIcon'):  
                HideIcon = SettingsConfig.getint(section, 'HideIcon')    
            else:
                if verbose:
                    ConsoleLog("HideIcon not found")
                boolWriteSettings = True

                
            if SettingsConfig.has_option(section, 'AppWidth'):  
                windowx = SettingsConfig.getint(section, 'AppWidth')    
            else:
                if verbose:
                    ConsoleLog("AppWidth not found")
                boolWriteSettings = True
                
            #override these values? per car?
            if SettingsConfig.has_option(section, 'AppHeight'):  
                windowy = SettingsConfig.getint(section, 'AppHeight')
            else:
                if verbose:
                    ConsoleLog("AppHeight not found")
                boolWriteSettings = True
 
            #backgroundOpacity
            if SettingsConfig.has_option(section, 'backgroundOpacity'):  
                backgroundOpacity = SettingsConfig.getfloat(section, 'backgroundOpacity')    
            else:
                if verbose:
                    ConsoleLog("backgroundOpacity not found")
                boolWriteSettings = True

            #drawBorderVar
            if SettingsConfig.has_option(section, 'drawBorder'):  
                drawBorderVar = SettingsConfig.getint(section, 'drawBorder')    
            else:
                if verbose:
                    ConsoleLog("drawBorder not found")
                boolWriteSettings = True
         
            #soundsFolder
            if SettingsConfig.has_option(section, "soundsFolder"):  
                if verbose:
                    ConsoleLog("Loading soundsFolder from the INI")
                soundsFolder = SettingsConfig.get(section, "soundsFolder")
                dirABSounds = "apps/python/AnnouncerBot/sounds/%s/"%soundsFolder
                #.exists?                
                if not os.path.exists(dirABSounds):
                    ConsoleLog("Making %s"%(dirABSounds))
                    os.makedirs(dirABSounds)
                if verbose:
                    ConsoleLog("Looking for sounds in %s"%(dirABSounds))
            else:
                if verbose:
                    ConsoleLog("soundsFolder not found")
                boolWriteSettings = True
                     
            #if SettingsConfig.has_option(section, 'ThreeDigitPrecision'):  
            #    ThreeDigitPrecision = SettingsConfig.getint(section, 'ThreeDigitPrecision')
            #    if ThreeDigitPrecision == 1:
            #        deltaStringFormat = "%.3f"
            #else:
            #    boolWriteSettings = True            

            #announcePractice
            if SettingsConfig.has_option(section, 'announcePractice'):  
                announcePractice = SettingsConfig.getint(section, 'announcePractice')    
            else:
                if verbose:
                    ConsoleLog("announcePractice not found")
                boolWriteSettings = True
         
            #announceQually
            if SettingsConfig.has_option(section, 'announceQually'):  
                announceQually = SettingsConfig.getint(section, 'announceQually')    
            else:
                if verbose:
                    ConsoleLog("announceQually not found")
                boolWriteSettings = True
         
            #announceRace
            if SettingsConfig.has_option(section, 'announceRace'):  
                announceRace = SettingsConfig.getint(section, 'announceRace')    
            else:
                if verbose:
                    ConsoleLog("announceRace not found")
                boolWriteSettings = True
         
            #announceTyreCompounds
            if SettingsConfig.has_option(section, 'announceTyreCompounds'):  
                announceTyreCompounds = SettingsConfig.getint(section, 'announceTyreCompounds')    
            else:
                if verbose:
                    ConsoleLog("announceTyreCompounds not found")
                boolWriteSettings = True
         
            #ballastName
            if SettingsConfig.has_option(section, 'ballastName'):  
                ballastName = SettingsConfig.get(section, 'ballastName')    
            #else:
            #    ConsoleLog("ballastName not found")
            #    boolWriteSettings = True
            if verbose:
                ConsoleLog("ballastName = %s"%(ballastName))

            #verbose
            if SettingsConfig.has_option(section, 'verbose'):  
                verbose = SettingsConfig.getint(section, 'verbose')    
            else:
                if verbose:
                    ConsoleLog("verbose not found")
                boolWriteSettings = True
            
            #nameLookup
            if SettingsConfig.has_option(section, "nameLookup"):  
                if verbose:
                    ConsoleLog("Loading nameLookup from the INI")
                nameLookups = SettingsConfig.get(section, "nameLookup").split("|") #in the python
                for name in nameLookups:
                    driverName, spokenName = name.split("^")
                    nameLookup[driverName] = spokenName
            else:
                if verbose:
                    ConsoleLog("nameLookup not found")
                #boolWriteSettings = True
            
            #readDriverNamesDelay
            if SettingsConfig.has_option(section, 'readDriverNamesDelay'):  
                readDriverNamesDelay = SettingsConfig.getfloat(section, 'readDriverNamesDelay')    
            else:
                if verbose:
                    ConsoleLog("readDriverNamesDelay not found")
                boolWriteSettings = True

            #nickNames
            #if SettingsConfig.has_option(section, "nickNames"):  
            #    ConsoleLog("Loading nickNames from the INI")
            #    nameLookups = SettingsConfig.get(section, "nickNames").split("|") #in the python
            #    for name in nameLookups:
            #        driverName, spokenName = name.split("^")
            #        nickNames[driverName] = spokenName
            #else:
            #    ConsoleLog("nickNames not found")
            #    #boolWriteSettings = True
            
            if boolWriteSettings == True and INI_File == SettingsINI:
                ConsoleLog("AnnouncerBot new settings found, writing new AnnouncerBot.ini")
                WriteSettings()
                
                
            KMHDir = 'apps/python/fuel_usage/KMH/'
            KMHINI = KMHDir + 'dic_' + getValidFileName(ac.getCarName(0)) +"_" + getValidFileName(ac.getTrackName(0)) + getValidFileName(ac.getTrackConfiguration(0)) + ".ini"
            
            if os.path.isfile(KMHINI):
                ConsoleLog("AnnouncerBot Reading %s"%(KMHINI))

                section = 'SETTINGS'
                #ConsoleLog("100")
                DicConfig = configparser.ConfigParser()
                #ConsoleLog("110")
                DicConfig.read(KMHINI)
                #ConsoleLog("120")
                #loop the KMH dic attribute and search the DicConfig for them
                fltPoT = 0.000
                #ConsoleLog("130")
                while fltPoT <= 1.0:
                    #ConsoleLog("140")
                    keyPoTKMH = "KMH%0.3f"%(fltPoT)
                    #ConsoleLog("150")
                    if DicConfig.has_option(section, keyPoTKMH):  
                        #ConsoleLog("160")
                        dicKMH[keyPoTKMH] = DicConfig.getint(section, keyPoTKMH)
                    #ConsoleLog("KMHAvg at %0.3f is %0.1f"%(fltPoT, dicKMH[keyPoTKMH]))
                    #ConsoleLog("170")
                    fltPoT = fltPoT + 0.001
            
            else:
                ConsoleLog("NOT Reading %s"%(KMHINI))
                
        else:
            ConsoleLog("AnnouncerBot Unable to read %s"%(INI_File))
            if INI_File == SettingsINI:
                ConsoleLog("Error reading %s, creating new one"%(INI_File))
                WriteSettings()

    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ac.console('ReadSettings Error (logged to file)')
        ac.log(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))

def onChatMessage(message, author):
    global soundsOn, displayText
    
    AppDic = AppCom.dic
    
    #ConsoleLog("onChatMessage %s: '%s'"%(author, message), 1, 0)
    
    if not message == "":
        if author == "SERVER" and isVoiceTTS:
            #ConsoleLog("Received Message From %s: %s"%(author, message))
            if message.startswith("Kicked"):
                #find and replace driver names in these messages?
                #we need to check all driverNames to see if they match.
                for car in range(0,ac.getCarsCount()):
                    driverName = AppDic[keysCarDriverName[car]].strip()
                    if not driverName == "" and driverName in nickNames:                   
                        #ConsoleLog("Looking for {} in server message".format(driverName))
                        nickName = nickNames[driverName][0] #always use the first nickName, which should be full name
                        findStart = "".join(["Kicked ", driverName, " "])
                        findReplace =  "".join(["Kicked ", nickName, " "])
                        if message.startswith(findStart):
                            message = message.replace(findStart, findReplace)
                            break
                        #else:
                        #    ConsoleLog("Did not find {} in {}".format(findStart, message))
                
                addSound(getValidFileName(message) + ".wav")
                ###################addSound(dirABSounds + "..wav")
                #addSound(getValidFileName(message) + ".wav")
            #this data is not reliable
            #if "set the fastest lap of the" in message:
            #    addSound(getValidFileName(message.replace(":", "  ")) + ".wav")
        #example messages
        #Jonathan Cuppett|RA|PSP|Jonathan Cuppett|Lap 14|Pit Speed Entry 87.97 > 82.00 by 5.97|pit entry warning +0 seconds total
        #RA|PSP|Jon Wathen|Lap 10|Pit Speed Entry 161.55 > 82.00 by 79.55|+30 seconds +30 seconds total
        #RA|PSP|Mateo Mejia|Lap 18|Pit Speed Entry 103.49 > 82.00 by 21.49|+10 seconds +10 seconds total
    
        #VirtualSafetyCar - Formation Laps, Virtual Safety Car, Virtual Pace Car
        #do we need to check for any drivers named "SERVER"?
        if author == "SERVER":
            #MESSAGE FROM SERVER INDICATES FORMATION LAP
            #- do not overtake before the Green Flag signal
            if message == "- do not overtake before the Green Flag signal":
                ConsoleLog("Formation Lap Logic Detected")
                dic["VirtualSafetyCar"] = 1
            #MESSAGE FROM SERVER INDICATES FORMATION LAP STARTING
            #Formation Lap starts!
            if message == "Formation Lap starts!":
                ConsoleLog("Formation Lap In Progress")
                dic["VirtualSafetyCar"] = 2
            #MESSAGE FROM SERVER INDICATES END OF THE FORMATION LAP
            #Green flag! Race Start! Go go go!
            if message == "Green flag! Race Start! Go go go!":
                ConsoleLog("Formation Lap Completed")
                dic["VirtualSafetyCar"] = 3
                addSound(dirABSounds + "la vuelta de formación ha terminado.wav")
                ###################addSound(dirABSounds + "..wav")
                addSound(dirABSounds + "comenzamos la carrera.wav")
                ###################addSound(dirABSounds + "..wav")
                
            #ABot(13.2110): onChatMessage SERVER: 'KMR_CMD^virtual_pace_car_deployed'
            #ABot(14.5526): onChatMessage SERVER: 'KMR_CMD^virtual_pace_car_ended'            
            if message == "KMR_CMD^virtual_pace_car_deployed":
                dic["VirtualSafetyCar"] = 4
                addSound(dirABSounds + "Virtual Pace Car Deployed.wav")
                ###################addSound(dirABSounds + "..wav")
            if message == "KMR_CMD^virtual_pace_car_ended":
                dic["VirtualSafetyCar"] = 5
                addSound(dirABSounds + "Virtual Pace Car Ends This Lap.wav")
                ###################addSound(dirABSounds + "..wav")
            
            
            if message.startswith("Virtual Safety Car deployed"):
                ConsoleLog("Virtual Safety Car deployed - DETECTED")
                dic["VirtualSafetyCar"] = 4
                addSound(dirABSounds + "Virtual Safety Car Deployed.wav")
                ###################addSound(dirABSounds + "..wav")

            if message.startswith("Virtual Safety Car ended!"):
                ConsoleLog("Virtual Safety Car ended - DETECTED")
                dic["VirtualSafetyCar"] = 3
                addSound(dirABSounds + "Virtual Safety Car Complete.wav")
                ###################addSound(dirABSounds + "..wav")
            
            
                
        if "BA|ORDER|" in message:
            tmpBA, tmpOrder, displayText = message.split("|")
            displayText = int(displayText)
            ConsoleLog("displayText set to %d"%(displayText))
    
        #do not report warnings, only actual infractions
        if "RA|PSP|" in message:
            ConsoleLog("RA|PSP| found")
            #this is a message about speeding into pit lane
            if "|+30 seconds" in message:
                ConsoleLog("30 seconds")
                reportPitLaneSpeeding(author, 30)
            elif "|+10 seconds" in message:
                ConsoleLog("10 seconds")
                reportPitLaneSpeeding(author, 10)
    
        #we need to add logic so only certain drivers can enable/disable ABOT
        if "ABOT^OFF" in message:
            ConsoleLog("ABOT^OFF detected")
            #soundsOn = 0
            
        if "ABOT^ON" in message:
            ConsoleLog("ABOT^ON detected")
            #soundsOn = 1
    
    
def reportPitLaneSpeeding(driverName, seconds):

    if verbose:
        ConsoleLog("Reporting Pit Lane Speeding of %d seconds for %s"%(seconds, driverName))
    
    AppDic = AppCom.dic
    
    #track the total seconds of PSP in the dic?
    #ConsoleLog("looping cars in reportPitLaneSpeeding")    
    for car in range(0,ac.getCarsCount()):
        strCarId = str(car)
        carId = car
        if AppDic[keysCarConnected[carId]]: #ac.isConnected(car):
            #keyCarDriverName = keysCarDriverName[carId] # "".join(["Car", str(car), "DriverName"])
            if driverName == AppDic[keysCarDriverName[carId]]: # getABotDriverName(car):
                tmpKey = "Car%dPSPTotal"%(car)
                if tmpKey in dic:
                    dic[tmpKey] = dic[tmpKey] + seconds
                else:
                    dic[tmpKey] = seconds
                    
                ab_driverName = getABotDriverName(carId) # driverName.replace(" ", "_")
                fname = dirABSounds + ab_driverName + ".wav"
                if checkSound(fname):
                    if seconds == 30:
                        addSound("%s%d_second_pit_lane_speeding_penalty_for.wav"%(dirABSounds, seconds))
                        addSound(fname)                        
                        #add a period
                        ###################addSound(dirABSounds + "..wav")
                    elif seconds == 10:
                        addSound("%s%d_second_pit_lane_speeding_penalty_for.wav"%(dirABSounds, seconds))
                        addSound(fname)
                        #add a period
                        ###################addSound(dirABSounds + "..wav")
                    if not dic[tmpKey] == seconds:
                        #how many seconds total penalty to they have?
                        addSound("%s%d_seconds_total.wav"%(dirABSounds, dic[tmpKey]))
                        #add a period
                        ###################addSound(dirABSounds + "..wav")                        
                return
             
def getTTSName(car, driverName):
    #ConsoleLog("seeking %s in nickNames"%(driverName))
    tmpKey = "".join(["Driver", str(car), "FullName", driverName]) #"Driver%dFullName%s"%(car,driverName)
    if driverName in nickNames and tmpKey in dic:
        if len(nickNames[driverName]) == 1:
            #ConsoleLog("Only 1 NickName")
            driverName = nickNames[driverName][0]
        elif len(nickNames[driverName]) > 1:
            #ConsoleLog("More Than 1 NickName")
            driverName = nickNames[driverName][randInRange(0, len(nickNames[driverName])) - 1]
    elif driverName in nickNames:
        if len(nickNames[driverName]) > 0:
            driverName = nickNames[driverName][0]
    elif driverName in nameLookup:
        driverName = nameLookup[driverName]

    return driverName

#tmpKey = "".join(["Car", str(car), "FullName", carFolderName])
def getCarNickName(car):
    global carNames #nickNames, driverName
    
    try:
    
        carFolderName = ac.getCarName(car)
        carName = ""
        
        if isVoiceTTS:
            #ConsoleLog("seeking %s in carNames"%(carFolderName))
            #have we spoken the full name for the car yet?
            tmpKey = "".join(["Car", str(car), "FullName", carFolderName])
            if carFolderName in carNames and tmpKey in dic:
                if len(carNames[carFolderName]) == 1:
                    #ConsoleLog("Only 1 NickName")
                    carName = carNames[carFolderName][0]
                elif len(carNames[carFolderName]) > 1:
                    #ConsoleLog("More Than 1 NickName")
                    carName = carNames[carFolderName][randInRange(0, len(carNames[carFolderName])) - 1]
            elif carFolderName in carNames:
                dic[tmpKey] = 1
                if len(carNames[carFolderName]) > 0:
                    carName = carNames[carFolderName][0]
            else:
                #the car has no defined names
                dic[tmpKey] = 1

            return carName
    except:
        return ""
             
def getABotDriverName(car):
    #all the names in the following list have been recorded
                        
    #ConsoleLog("time.clock() = {}".format(time.clock()))

    if readDriverNamesDelay > 0.0:
        tmpKey = "lastCheckDriverNames"    
        try:
            varTemp = dic[tmpKey]
        except:
            dic[tmpKey] = 0
        if tmpKey in dic:
            if time.clock() - dic[tmpKey] > readDriverNamesDelay:
                #ConsoleLog("Calling ReadDriverNames")
                dic[tmpKey] = time.clock()
                ReadDriverNames()
                        
    #if the driver name is not known then use an alternate name
    driverName = ac.getDriverName(car)#.replace("|", " ").replace("^", " ") # safeName(car)

    if isVoiceTTS:
        #ConsoleLog("seeking %s in nickNames"%(driverName))
        tmpKey = "".join(["Driver", str(car), "FullName", driverName]) #"Driver%dFullName%s"%(car,driverName)
        if driverName in nickNames and tmpKey in dic:
            if len(nickNames[driverName]) == 1:
                #ConsoleLog("Only 1 NickName")
                driverName = nickNames[driverName][0]
            elif len(nickNames[driverName]) > 1:
                #ConsoleLog("More Than 1 NickName")
                driverName = nickNames[driverName][randInRange(0, len(nickNames[driverName])) - 1]
        elif driverName in nickNames:
            if len(nickNames[driverName]) > 0:
                driverName = nickNames[driverName][0]
        elif driverName in nameLookup:
            driverName = nameLookup[driverName]

        return driverName

    ab_driverName = driverName.replace(" ", "_")
    fname = dirABSounds + ab_driverName + ".wav"

    #if driverName in skipDrivers:
    #    return ""
    
    if not checkSound(fname) and not driverName in skipDrivers:
        if len(replacementNames) > 1:
            #ConsoleLog("Driver %s not known to ABot"%(ab_driverName))
            driverName = replacementNames[car % len(replacementNames)]
            #BroadcastApp should set this to true
    #else:
        #    ConsoleLog("Not using replacementNames")
    
    #ConsoleLog("Using %s for %s"%(driverName, safeName(car)))

    #tmpKey = "Driver%dFullName%s"%(car,driverName)
    #if not tmpKey in dic:
    #    ConsoleLog("Full Name for %s spoken"%(driverName))
    #    dic[tmpKey] = 1
    
            
    #ConsoleLog("using %s"%(driverName))
            
            #ConsoleLog("nameLookup returning %s"%(driverName))
    
    driverName = driverName.replace("/", " ").replace("\\", " ")
    
    return driverName
    
def getPosition(car):

    tmpKey = keysCarPosition[car] # "".join(["Car", str(car), "Position"]) #"Car{}Position".format(car)
    if tmpKey in AppCom.dic:
        #ConsoleLog("Returning %d for carId %d"%(AppCom.dic[tmpKey], car))
        return AppCom.dic[tmpKey]

    tmpKey = "APPS:BROADCAST APP"
    if order == "": #not tmpKey in dicPython:
        #ConsoleLog("returning 100 getCarRealTimeLeaderboardPosition for dic[%s]"%(tmpKey))
        try:
            position = ac.getCarRealTimeLeaderboardPosition(car)
        except:
            position = ac.getCarLeaderboardPosition(car)
        return position
    else:
        tmpKey = "".join(["Car", str(car), "Position"]) #"Car{}Position".format(car) #getPosition
        if tmpKey in dic:
            #ConsoleLog("dic[%s] = %s"%(tmpKey, dic[tmpKey]))
            return int(dic[tmpKey])
        else:
            #ConsoleLog("returning 200 getCarRealTimeLeaderboardPosition for dic[%s]"%(tmpKey))
            try:
                position = ac.getCarRealTimeLeaderboardPosition(car)
            except:
                position = ac.getCarLeaderboardPosition(car)
            return position
    
def setPositions():
    #ConsoleLog("setPositions subroutine")
    #this is no longer necessary?
    return 
    
    #we can return 0 to skip all this logic
    #return 0
    tmpKey = "APPS:BROADCAST APP"
    if order == "": # not tmpKey in dicPython:
        #ConsoleLog("not using setPositions logic")
        return False
    else: #pull the driver order directly from BA textOrder?
        #do we know the value for the BA data share control? ac.sendChatMessage(text) doesn't work offline
        #ConsoleLog("%s"%(ac.getText(displayText)))
        if True:
            #1st|2nd|3rd|4th|5th|6th|etc
            #18|3|25|13|20|24|2|7|12|4|6|1|19|16|17|5|8|9|10|11|14|15|21|22|23|
            if not order == "":
                #ConsoleLog("Order = %s"%(order))
                orderStrings = order.split("|")
                position = 0
                #ConsoleLog("looping cars in setPositions")
                for car in orderStrings:
                    if not car == "":
                        #ConsoleLog("Car = " + car)
                        dic["Car%dPosition"%(int(car))] = position #setPositions
                        #ConsoleLog("Driver %d in position %d named %s"%(int(car), position + 1, safeName(int(car))))
                        position = position + 1
                        
                return True
            else:
                ConsoleLog("unable to set order")
                return False

def StoreStartingPositions():
    #dic["Car%dPosition"%(int(car))] = position #setPositions
    #ConsoleLog("looping cars in StoreStartingPositions")
    for car in range(0, ac.getCarsCount()):
        strCarId = str(car)
        carId = car
        if AppDic[keysCarConnected[carId]]: #ac.isConnected(car):
            startKey = "".join(["Car", strCarId, "StartPosition"]) # "Car{}StartPosition".format(car)            
            tmpKey = "".join(["Car", strCarId, "Position"]) #"Car{}Position".format(car)
            if tmpKey in AppCom.dic:
                #ConsoleLog("Returning %d for carId %d"%(AppCom.dic[tmpKey], car))
                dic[startKey] = AppCom.dic[tmpKey]
            elif tmpKey in dic:
                #tmpKey = "Car{}Position".format(car) #getPosition
                dic[startKey] = dic[tmpKey]
            if startKey in dic and verbose:
                ConsoleLog("dic[{}] = {}".format(startKey, dic[startKey]))
    return

def savePositions():
    AppDic = AppCom.dic
    
    #dic["Car%dPosition"%(int(car))] = position #setPositions
    #ConsoleLog("looping cars in StoreStartingPositions")
    for car in range(0, ac.getCarsCount()):
        strCarId = str(car)
        carId = car
        if AppDic[keysCarConnected[carId]]: # ac.isConnected(car):
            posKey = keysCarSavedPositions[carId] # "".join(["Car", strCarId, "SavedPosition"]) #"Car{}SavedPosition".format(car)
            tmpKey = keysCarPosition[carId]# "".join(["Car", strCarId, "Position"]) #"Car{}Position".format(car)
            if tmpKey in AppDic:
                #ConsoleLog("Returning %d for carId %d"%(AppDic[tmpKey], car))
                dic[posKey] = AppDic[tmpKey]
            elif tmpKey in dic:
                #tmpKey = "Car{}Position".format(car) #getPosition
                dic[posKey] = dic[tmpKey]
            if posKey in dic and verbose:
                ConsoleLog("dic[{}] = {}".format(posKey, dic[posKey]))
    return

def getSavedPosition(car):
    strCarId = str(car)
    tmpKey = keysCarSavedPositions[car] # "".join(["Car", strCarId, "SavedPosition"]) #"Car%dSavedPosition"%(car) #getPosition
    if tmpKey in dic:
        #ConsoleLog("dic[%s] = %s"%(tmpKey, dic[tmpKey]))
        return int(dic[tmpKey])
    else:
        #ConsoleLog("returning 200 getCarRealTimeLeaderboardPosition for dic[%s]"%(tmpKey))
        try:
            position = ac.getCarRealTimeLeaderboardPosition(car)
        except:
            position = ac.getCarLeaderboardPosition(car)
        return position

def savePositionsOLD():
    #ConsoleLog("savePositions subroutine")
    
    #we can return 0 to skip all this logic
    #return 0
    tmpKey = "APPS:BROADCAST APP"
    if order == "": # not tmpKey in dicPython:
        #ConsoleLog("not using setPositions logic")
        return False
    else: #pull the driver order directly from BA textOrder?
        #do we know the value for the BA data share control? ac.sendChatMessage(text) doesn't work offline
        #ConsoleLog("%s"%(ac.getText(displayText)))
        if True:
            #1st|2nd|3rd|4th|5th|6th|etc
            #18|3|25|13|20|24|2|7|12|4|6|1|19|16|17|5|8|9|10|11|14|15|21|22|23|
            if not order == "":
                #ConsoleLog("Order = %s"%(order))
                orderStrings = order.split("|")
                position = 0
                #ConsoleLog("looping cars in setPositions")
                for car in orderStrings:
                    if not car == "":
                        dic["Car%dSavedPosition"%(int(car))] = position #setPositions
                        #ConsoleLog("Driver %d in position %d named %s"%(int(car), position + 1, safeName(int(car))))
                        position = position + 1
                        
                return True
            else:
                ConsoleLog("unable to set order")
                return False

                   
#BestLap and LastLap
#ac.getCarState(self.slotId, acsys.CS.BestLap)
#ac.getCarState(car, acsys.CS.LastLap)
def reportLastLapTime(car):
    lastLapTime = ac.getCarState(car, acsys.CS.LastLap)
    tmpKey = "Car%dReportLastLap"%(car)
    
    if tmpKey in dic:
        if lastLapTime == dic[tmpKey]:
            return False
            
    if lastLapTime > 0:
        addSound(dirABSounds + "ultima vuelta de%s.wav"%(formatLapTime3Digits(lastLapTime).replace(":", "_")))
        dic[tmpKey] = lastLapTime
            
def reportGapToFastest(car):
    #is this reporting the fastest lap from qually?
    #return 
    #bIsQually = False
    #if AppCom.dic["Session"] == 1:
    #    bIsQually = True
    #bIsPractice = False
    #if AppCom.dic["Session"] == 0:
    #    bIsPractice = True
    #bIsRace = False
    #if AppCom.dic["Session"] == 2:
    #    bIsRace = True

    #bestLapTime = ac.getCarState(car, acsys.CS.BestLap)
    #tmpKey = "Car%dReportBestLap"%(car)
    
    #report time behind the leader?
    #ConsoleLog("looping getCarsCount to report gap to leader")
    #for i in range(0,ac.getCarsCount()):
    #    if ac.isConnected(i):
    #        iBestLapTime = ac.getCarState(i, acsys.CS.BestLap)
    #        if iBestLapTime > 0 and iBestLapTime < iBestTime:
    #            iBestTime = iBestLapTime
    
    
    bestLapTime = AppCom.dic[keysCarBestLap[car]]
    iBestTime = AppCom.dic["FastestLap"] # bestLapTime
    if AppCom.dic["FastestLap"] < bestLapTime: # AppCom.dic["".join(["Car", str(car), "BestLapTime"])]: # bestLapTime:
        #we don't needs minutes or leading zeros
        if AppCom.dic["IsQually"]: # bIsQually:
            addSound(dirABSounds + " _._a cero %s segundos de distancia con la pole.wav"%(formatGap3Digits(bestLapTime - iBestTime).replace(":", "_")))
        if AppCom.dic["IsRace"]: #bIsRace:
            addSound(dirABSounds + " _a cero_%s_segundos_de diferencia con la mejor vuelta de la carrera.wav"%(formatGap3Digits(bestLapTime - iBestTime).replace(":", "_")))

            
def reportBestLapTime(car):

    #bIsQually = False
    #if AppCom.dic["Session"] == 1:
    #    bIsQually = True
    #bIsPractice = False
    #if AppCom.dic["Session"] == 0:
    #    bIsPractice = True
    #bIsRace = False
    #if AppCom.dic["Session"] == 2:
    #    bIsRace = True

    strCarId = str(car)
    carId = car

    bestLapTime = AppCom.dic[keysCarBestLap[carId]] # ac.getCarState(car, acsys.CS.BestLap)
    tmpKey = "".join(["Car", strCarId, "ReportBestLap"]) # "Car%dReportBestLap"%(car)
    
    if tmpKey in dic:
        if bestLapTime == dic[tmpKey]:
            return False
            
    if bestLapTime > 0:
        addSound(dirABSounds + "._su_mejor_tiempo_es_de_%s_,_.wav"%(formatLapTime3Digits(bestLapTime).replace(":", "_")))
        dic[tmpKey] = bestLapTime

    reportGapToFastest(car)
        

#def reportTimeBehindLeader():

def randInRange(lower, upper):
    if upper >= lower:
        return random.randint(lower, upper)
    else:
        return lower
             
def reportDriverNameAndPosition(car, closestCar, closestCarGap):
    #iniciar_contador()
    global pVoiceTimeedu


    AppDic = AppCom.dic
    strCarId = str(car)
    carId = car
    strClosest = str(closestCar)
    #keyCarDriverName = keysCarDriverName[carId] # "".join(["Car", strCarId, "DriverName"])
    keyCarRaceFinished = keysCarRaceFinished[carId] # "".join(["Car", strCarId, "RaceFinished"])
    
    if not AppDic[keysCarActive[carId]]:
        ConsoleLog("NOT reporting Name and Position for inactive car %s"%(AppDic[keysCarDriverName[carId]]))
        return
    
    if verbose:
        ConsoleLog("REPORTING Name and Position for %s, qSpeech.qsize = %d, pVoiceTime = %d"%(AppDic[keysCarDriverName[carId]], qSpeech.qsize(), pVoiceTime))
  
    #for testing
    #reportTyreCompoundAB(focusedCar)
    
    
    bIsQually = False
    if AppCom.dic["Session"] == 1:
        bIsQually = True
    bIsPractice = False
    if AppCom.dic["Session"] == 0:
        bIsPractice = True
    bIsRace = False
    if AppCom.dic["Session"] == 2:
        bIsRace = True
    
    raceOver = dic["raceOver"]
    
    driverName = AppDic[keysCarDriverName[car]] # getABotDriverName(car)
    ballast = ac.getCarBallast(car)
    ab_driverName = getABotDriverName(car) # driverName.replace(" ", "_")
    
    nationCode = ac.getDriverNationCode(car)
    
    position = AppDic[keysCarPosition[carId]] # getPosition(car)
    currPoT = AppDic[keysCarPoT[carId]] # ac.getCarState(car,acsys.CS.NormalizedSplinePosition)
    
    #carCurrPoT = AppDic[keysCarPoT[carId]]
    #ConsoleLog("200")
    carDistance = currPoT * trackLength
    
    try:
        lastLapTime = AppDic[keysCarLastLapTime[carId]] # ac.getCarState(car, acsys.CS.LastLap)
    except:
        lastLapTime = 0.0
        
    lapCount = AppDic[keysCarLapCount[carId]] # ac.getCarState(car, acsys.CS.LapCount)
    inPits = AppDic[keysCarInPits[carId]]
    isSpeaking = isVoiceSpeaking()
    
    #maxReportables = 10
    whatToReport = 0
    report = "NOTHING"
    if (lapCount > 0 or AppDic["Car0LapTime"] > raceStartDelay) and not raceOver and not (dic["VirtualSafetyCar"] == 2 or dic["VirtualSafetyCar"] == 4):
        #ConsoleLog("100")
        whatToReport = randInRange(0, len(reportables) - 1)
        #ConsoleLog("200")
        report = reportables[whatToReport]
        if verbose:
            ConsoleLog("Reporting %s"%(report))
        
    if (report == "MAKE" or report == "MODEL") and ac.getCarName(car) in carNames:
        #ConsoleLog("REPORTING CAR_NAME INSTEAD OF MAKE OR MODEL")
        report = "CAR_NAME"
        
    tmpKey = "uniqueModels"
    if not tmpKey in uiCars:
        uiCars[tmpKey] = 0

    tmpKey = "uniqueMakes"
    if not tmpKey in uiCars:
        uiCars[tmpKey] = 0
        
        
    #0 - report nothing extra
    #1 - report tyres
    #2 - lead lap or laps down?
    #3 - nationality
    #4 - in which car (only if more than 2 cars on the server)
        #tmpKey = "Car-%s-Model"%(ac.getCarName(car))                    
    #5 - fastest lap
    #6 - ballast
    #7 - starting position
    #8 - brand?
        #tmpKey = "Car-%s-Make"%(ac.getCarName(car))
    #if verbose == 1:
    #    if whatToReport == 1:
    #        ConsoleLog("What to report = %d, TYRES"%(whatToReport))
    #    elif whatToReport == 2:
    #        ConsoleLog("What to report = %d, LEAD LAP OR LAP DOWN"%(whatToReport))
    #    elif whatToReport == 3:
    #        ConsoleLog("What to report = %d, NATIONALITY"%(whatToReport))
    #    elif whatToReport == 4:
    #        ConsoleLog("What to report = %d, MODEL"%(whatToReport))   
    #    elif whatToReport == 5:
    #        ConsoleLog("What to report = %d, FASTEST LAP"%(whatToReport))        
    #    elif whatToReport == 6:
    #        ConsoleLog("What to report = %d, BALLAST"%(whatToReport))        
    #    elif whatToReport == 7:
    #        ConsoleLog("What to report = %d, STARTING POSITION"%(whatToReport))
    #    elif whatToReport == 8:
    #        ConsoleLog("What to report = %d, MAKE"%(whatToReport))
    #    elif whatToReport == 9:
    #        ConsoleLog("What to report = %d, LAP NUMBER"%(whatToReport))
    #    else:
    #        ConsoleLog("What to report = %d"%(whatToReport))
    

    #dirABSounds
    fname = dirABSounds + ab_driverName + ".wav"
    norepetirenpits = 0 #AQUI DECLARO LA VARIABLE A CERO
    if checkSound(fname) and not driverName in skipDrivers:
        
        
        #edu no sé que hace este addsound aqui... es el nombre del piloto y no sé que hace
        addSound(fname)
        
        tmpKey = "Driver%dFullName%s"%(car,AppDic[keysCarDriverName[carId]])
        if not tmpKey in dic:
            if verbose:
                ConsoleLog("Full Name %s spoken"%(driverName))
            dic[tmpKey] = 1
        
            
        if qSpeech.qsize() < qSkipLength and not isSpeaking:
            tmpKey = "driver%dNation"%(car)
            if not tmpKey in dic or report == "NATIONALITY":
                dic[tmpKey] = nationCode
                if nationCode in dicNations:
                    #ConsoleLog("Found Nation Code = %s"%(nationCode))
                    addSound("del equipo_%s.wav"%(dicNations[nationCode].replace(" ", "_")))
                #else:
                #    ConsoleLog("NO Nation Code = %s"%(nationCode))

            #where on track
            namedLocation = ""
            #ConsoleLog("looping sections")
            for section in trackSections:
                try:
                    if currPoT > uiDic["%s_IN"%(section)] and currPoT < uiDic["%s_OUT"%(section)]:
                        if len(uiDic["%s_TEXT"%(section)]) == 1:
                            #ConsoleLog("Only 1 NickName")
                            namedLocation = uiDic["%s_TEXT"%(section)][0]
                        elif len(uiDic["%s_TEXT"%(section)]) > 1:
                            #ConsoleLog("More Than 1 NickName")
                            namedLocation = uiDic["%s_TEXT"%(section)][randInRange(0, len(uiDic["%s_TEXT"%(section)])) - 1]

                        #namedLocation = uiDic["%s_TEXT"%(section)]
                        if verbose:
                            ConsoleLog("Current car in %s"%(namedLocation))
                            
                except:
                    pass
                    
            #if qually report perf delta as the named locations change?
            if not namedLocation == "" and "NAMED_LOCATION" in reportables and ((AppDic["Car0LapTime"] > 0.0 and not raceOver and not inPits) or dic["VirtualSafetyCar"] == 2):
                #ConsoleLog("REPORTING NAMED LOCATION %s"%(namedLocation))
                
                
                
                #EDU SUSSY
                #leo el fichero de probabilidad de leer las frases
                # Lee el número del archivo externo
                Name_File = 'apps\\python\\AnnouncerBot\\probabilidadsusy.txt'
                with open(Name_File, 'r')as f:
                    probabilidad = int(f.read())
                    print(probabilidad)
                    ConsoleLog("numero3: PASAR POR ZONA probabilidad %s"%(probabilidad))
                # Si la probabilidad es mayor que 0 y menor que 100
                if 0 < probabilidad < 101:
                    # Ejecuta la sentencia if con la probabilidad correspondiente
                    azarnum = random.uniform(0, 100)
                    ConsoleLog("numeroazar: %s"%(azarnum))
                    if azarnum < probabilidad :
                        #Edu este if de numero2 no quiero que lo lea cuando es qualy. Solo cuando es carrera
                        if bIsRace: #si es carrera lee estas frases


                            ##bIsMutedForIntro = True                
                            #qSpeech.queue.clear()
                            #dic.clear()                                
                            #sessionStartTime = clock()
    


                                numero3 = randInRange(0, 96)
                                if numero3 == 0:
                                    addSound("_pasando por la zona de_%s,.wav"%(namedLocation))
                                elif numero3 == 1:
                                    addSound("_pasa ahora por_%s,.wav"%(namedLocation))
                                elif numero3 == 2:
                                    addSound("_atravesando_%s,.wav"%(namedLocation))
                                elif numero3 == 3:
                                    addSound("_girando en_%s,.wav"%(namedLocation))
                                elif numero3 == 4:
                                    addSound("transita por_%s,.wav"%(namedLocation))
                                elif numero3 == 5:
                                    addSound(",pasando por_%s,.wav"%(namedLocation))
                                elif numero3 == 6:
                                    addSound(",cruzando_%s,.wav"%(namedLocation))
                                elif numero3 == 7:
                                    addSound("_circula por_%s,.wav"%(namedLocation))
                                    ###################addSound(dirABSounds + "..wav")
                                elif numero3 == 8:
                                    addSound("_aborda el área de_%s,.wav"%(namedLocation))
                                elif numero3 == 9:
                                    addSound("_volando por_%s,.wav"%(namedLocation))
                                elif numero3 == 10:
                                    addSound("está apretando..wav")
                                elif numero3 == 11:
                                    addSound("Está tirando fuerte..wav")
                                elif numero3 == 12:
                                    addSound("No quiere cometer ningún error..wav")
                                    ###################addSound(dirABSounds + "..wav")
                                elif numero3 == 13:
                                    addSound("Manteniendo la concentración..wav")
                                elif numero3 == 14:
                                    addSound("Está apretando los dientes..wav")               
                                elif numero3 == 15:
                                    addSound("Está dando todo lo que tiene..wav")
                                elif numero3 == 16:
                                    addSound("Está luchando por la posición..wav")
                                elif numero3 == 17:
                                    addSound("No se deja distraer..wav")
                                elif numero3 == 18:
                                    addSound("Está enfocado en la carrera..wav")
                                elif numero3 == 19:
                                    addSound("Está aprovechando cada oportunidad..wav")
                                elif numero3 == 20:
                                    addSound("Está dando un gran espectáculo..wav")
                                elif numero3 == 21:
                                    addSound("Está compitiendo con determinación..wav")
                                elif numero3 == 22:
                                    addSound("Está haciendo una carrera inteligente..wav")
                                elif numero3 == 23:
                                    addSound("Está sacando el máximo partido al coche..wav")
                                elif numero3 == 24:
                                    addSound("Está dando una actuación espectacular..wav")
                                elif numero3 == 25:
                                    addSound("Está empujando el coche al límite..wav")
                                elif numero3 == 26:
                                    addSound("Está haciendo una gran carrera..wav")
                                elif numero3 == 27:
                                    addSound("Está sorprendiendo a todos..wav")
                                elif numero3 == 28:
                                    addSound("Está demostrando su habilidad al volante..wav")
                                elif numero3 == 29:
                                    addSound("Está llevando el coche al límite..wav")
                                elif numero3 == 30:
                                    addSound("Está compitiendo con fuerza..wav")    
                                elif numero3 == 31:
                                    addSound("Está buscando mejorar su posición..wav")
                                elif numero3 == 32:
                                    addSound("Está defendiendo su posición..wav")
                                elif numero3 == 33:
                                    addSound("Está dando lo mejor de sí mismo..wav")
                                elif numero3 == 34:
                                    addSound("Está demostrando su talento..wav")
                                elif numero3 == 35:
                                    addSound("Está manteniendo la calma..wav")
                                elif numero3 == 36:
                                    addSound("Está compitiendo con tesón..wav")
                                elif numero3 == 37:
                                    addSound("Está haciendo una maginífica carrera..wav")
                                elif numero3 == 38:
                                    addSound("Está dejando todo en la pista..wav")
                                elif numero3 == 39:
                                    addSound("Está haciendo una carrera sólida..wav")
                                elif numero3 == 40:
                                    addSound("Está manteniendo la concentración..wav")
                                elif numero3 == 41:
                                    addSound("Está corriendo con determinación..wav")
                                elif numero3 == 42:
                                    addSound("Está buscando la victoria..wav")
                                elif numero3 == 43:
                                    addSound("Está corriendo con fuerza..wav")
                                elif numero3 == 44:
                                    addSound("Está protegiendo la posición..wav")
                                elif numero3 == 45:
                                    addSound("Está corriendo con habilidad..wav")
                                elif numero3 == 46:
                                    addSound("Está haciendo una carrera impresionante..wav")
                                elif numero3 == 47:
                                    addSound("Está demostrando su valía al volante..wav")
                                elif numero3 == 48:
                                    addSound("Está corriendo con astucia..wav")
                                elif numero3 == 49:
                                    addSound("Está buscando la victoria..wav")
                                elif numero3 == 50:
                                    addSound("Está dando lo mejor de sí mismo..wav")
                                elif numero3 == 51:
                                    addSound("Está corriendo con determinación..wav")
                                elif numero3 == 52:
                                    addSound("se dirige a la zona de%s,.wav"%(namedLocation))
                                elif numero3 == 53:
                                    addSound("llegando a%s,.wav"%(namedLocation))
                                elif numero3 == 54:
                                    addSound("entrando en%s,.wav"%(namedLocation))
                                elif numero3 == 55:
                                    addSound("tomando la curva de%s,.wav"%(namedLocation))
                                elif numero3 == 56:
                                    addSound("viajando por%s,.wav"%(namedLocation))
                                elif numero3 == 57:
                                    addSound("pasando por%s,.wav"%(namedLocation))
                                elif numero3 == 58:
                                    addSound("atravesando%s,.wav"%(namedLocation))
                                elif numero3 == 59:
                                    addSound("cruzando%s,.wav"%(namedLocation))
                                elif numero3 == 60:
                                    addSound("ingresando a%s,.wav"%(namedLocation))
                                elif numero3 == 61:
                                    addSound("explorando%s,.wav"%(namedLocation))
                                elif numero3 == 62:
                                    addSound("navegando por%s,.wav"%(namedLocation))
                                elif numero3 == 63:
                                    addSound("pasando por%s,.wav"%(namedLocation))
                                elif numero3 == 64:
                                    addSound("atraviesa%s,.wav"%(namedLocation))
                                elif numero3 == 65:
                                    addSound("en curva %s,.wav"%(namedLocation))
                                elif numero3 == 66:
                                    addSound("conduciendo por%s,.wav"%(namedLocation))
                                elif numero3 == 67:
                                    addSound("viajando por%s,.wav"%(namedLocation))
                                elif numero3 == 68:
                                    addSound("cruzando%s,.wav"%(namedLocation))
                                elif numero3 == 69:
                                    addSound("paseando por%s,.wav"%(namedLocation))
                                elif numero3 == 70:
                                    addSound("entrando en%s,.wav"%(namedLocation))
                                elif numero3 == 71:
                                    addSound("volando por%s,.wav"%(namedLocation))
                                elif numero3 == 72:
                                    addSound("%s, en dirección a %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 73:
                                    addSound("%s, cerca de %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 74:
                                    addSound("%s, en el área de %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 75:
                                    addSound("%s, en la zona de %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 76:
                                    addSound("%s, en %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 77:
                                    addSound("%s, en las inmediaciones de %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 78:
                                    addSound("%s, en la recta anterior a %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 79:
                                    addSound("%s, en la recta cercana a %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 80:
                                    addSound("%s, en la carrera por %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 81:
                                    addSound("%s, en carrera por %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 82:
                                    addSound("%s, en la lucha por %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 83:
                                    addSound("%s, en la vuelta por %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 84:
                                    addSound("%s, en vuelta buena por %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 85:
                                    addSound("%s, en la carrera hacia %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 86:
                                    addSound("%s, en la competición hacia %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 87:
                                    addSound("%s, avanzando hacia %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 88:
                                    addSound("%s, aproximándose a %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 89:
                                    addSound("%s, cerca de %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 90:
                                    addSound("%s, en el área de %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 91:
                                    addSound("%s, en la zona de %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 92:
                                    addSound("%s, en %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 93:
                                    addSound("%s, en las inmediaciones de %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 94:
                                    addSound("%s, en la zona cercana a %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 95:
                                    addSound("%s, en la recta anterior a %s,.wav"%(dirABSounds, namedLocation))
                                elif numero3 == 96:
                                    addSound("%s, en la carrera por %s,.wav"%(dirABSounds, namedLocation))
                                pVoiceTimeedu = clock()
                        
                        else: #esto significa que no estamos en carrera, estamos en qualy o entrenamiento
                            #addSound("pasando por%s,.wav"%(namedLocation))
                            numero3 = randInRange(0, 96)
                            if numero3 == 0:
                                addSound("_pasando por la zona de_%s,.wav"%(namedLocation))
                            elif numero3 == 1:
                                addSound("_pasa ahora por_%s,.wav"%(namedLocation))
                            elif numero3 == 2:
                                addSound("_atravesando_%s,.wav"%(namedLocation))
                            elif numero3 == 3:
                                addSound("_girando en_%s,.wav"%(namedLocation))
                            elif numero3 == 4:
                                addSound("transita por_%s,.wav"%(namedLocation))
                            elif numero3 == 5:
                                addSound(",pasando por_%s,.wav"%(namedLocation))
                            elif numero3 == 6:
                                addSound(",cruzando_%s,.wav"%(namedLocation))
                            elif numero3 == 7:
                                addSound("_circula por_%s,.wav"%(namedLocation))
                                ###################addSound(dirABSounds + "..wav")
                            elif numero3 == 8:
                                addSound("_aborda el área de_%s,.wav"%(namedLocation))
                            elif numero3 == 9:
                                addSound("_volando por_%s,.wav"%(namedLocation))
                            elif numero3 == 10:
                                addSound("pasando por%s,.wav"%(namedLocation))
                                addSound("está apretando en la sesión de cuali..wav")
                            elif numero3 == 11:
                                addSound("Está tirando fuerte..wav")
                                addSound("cuando pasa por%s,.wav"%(namedLocation))
                            elif numero3 == 12:
                                addSound("No quiere cometer errores..wav")
                                addSound("en la zona de%s,.wav"%(namedLocation))
                                ###################addSound(dirABSounds + "..wav")
                            elif numero3 == 13:
                                addSound("Manteniendo la concentración..wav")
                                addSound("en%s,.wav"%(namedLocation))
                            elif numero3 == 14:
                                addSound("Está apretando los dientes..wav")
                                addSound("cruzando %s,.wav"%(namedLocation))               
                            elif numero3 == 15:
                                addSound("Está dando todo lo que tiene en esta sesión de cuali..wav")
                            elif numero3 == 16:
                                addSound("Está luchando por la posición, busca hacer una buena cuali..wav")
                            elif numero3 == 17:
                                addSound("No se deja distraer..wav")
                            elif numero3 == 18:
                                addSound("Está enfocado en la sesión de clasificación..wav")
                            elif numero3 == 19:
                                addSound("Está aprovechando cada oportunidad..wav")
                            elif numero3 == 20:
                                addSound("Está dando un gran espectáculo..wav")
                            elif numero3 == 21:
                                addSound("Está compitiendo con determinación..wav")
                            elif numero3 == 22:
                                addSound("Está haciendo una cuali inteligente..wav")
                            elif numero3 == 23:
                                addSound("Está sacando el máximo partido al coche en esta sesión de cuali..wav")
                            elif numero3 == 24:
                                addSound("Está dando una actuación espectacular..wav")
                            elif numero3 == 25:
                                addSound("Está empujando el coche al límite..wav")
                                addSound("por el área de%s,.wav"%(namedLocation))
                            elif numero3 == 26:
                                addSound("Está haciendo una gran clasificación..wav")
                            elif numero3 == 27:
                                addSound("Está sorprendiendo en esta cuali..wav")
                            elif numero3 == 28:
                                addSound("Está demostrando su habilidad al volante..wav")
                            elif numero3 == 29:
                                addSound("Está llevando el coche al límite..wav")
                            elif numero3 == 30:
                                addSound("Está compitiendo con fuerza..wav")    
                            elif numero3 == 31:
                                addSound("Está buscando mejorar su posición..wav")
                            elif numero3 == 32:
                                addSound("Está luchando por salir lo más arriba posible en carrera..wav")
                            elif numero3 == 33:
                                addSound("Está dando lo mejor de sí mismo..wav")
                            elif numero3 == 34:
                                addSound("Está demostrando su talento..wav")
                            elif numero3 == 35:
                                addSound("Está manteniendo la calma..wav")
                            elif numero3 == 36:
                                addSound("Está compitiendo con tesón..wav")
                            elif numero3 == 37:
                                addSound("Está haciendo una cuali impresionante..wav")
                            elif numero3 == 38:
                                addSound("Está dejando todo en la pista..wav")
                            elif numero3 == 39:
                                addSound("Está haciendo una cuali muy sólida..wav")
                            elif numero3 == 40:
                                addSound("Está manteniendo la concentración..wav")
                            elif numero3 == 41:
                                addSound("Está clasificando con determinación..wav")
                            elif numero3 == 42:
                                addSound("Está buscando su mejor tiempo de cualy..wav")
                            elif numero3 == 43:
                                addSound("Está clasificando con fuerza..wav")
                            elif numero3 == 44:
                                addSound("Está luchando por hacer la pole..wav")
                            elif numero3 == 45:
                                addSound("Está clasificando con habilidad..wav")
                            elif numero3 == 46:
                                addSound("Está haciendo una magnífica cuali..wav")
                            elif numero3 == 47:
                                addSound("Está demostrando su valía al volante..wav")
                            elif numero3 == 48:
                                addSound("Está clasificando con astucia..wav")
                            elif numero3 == 49:
                                addSound("Está buscando la pole..wav")
                            elif numero3 == 50:
                                addSound("Está dando lo mejor de sí mismo..wav")
                            elif numero3 == 51:
                                addSound("Está intentando clasificar con determinación..wav")
                            elif numero3 == 52:
                                addSound("se dirige a la zona de%s,.wav"%(namedLocation))
                            elif numero3 == 53:
                                addSound("llegando a%s,.wav"%(namedLocation))
                            elif numero3 == 54:
                                addSound("entrando en%s,.wav"%(namedLocation))
                            elif numero3 == 55:
                                addSound("tomando la curva de%s,.wav"%(namedLocation))
                            elif numero3 == 56:
                                addSound("viajando por%s,.wav"%(namedLocation))
                            elif numero3 == 57:
                                addSound("pasando por%s,.wav"%(namedLocation))
                            elif numero3 == 58:
                                addSound("atravesando%s,.wav"%(namedLocation))
                            elif numero3 == 59:
                                addSound("cruzando%s,.wav"%(namedLocation))
                            elif numero3 == 60:
                                addSound("ingresando a%s,.wav"%(namedLocation))
                            elif numero3 == 61:
                                addSound("explorando%s,.wav"%(namedLocation))
                            elif numero3 == 62:
                                addSound("navegando por%s,.wav"%(namedLocation))
                            elif numero3 == 63:
                                addSound("pasando por%s,.wav"%(namedLocation))
                            elif numero3 == 64:
                                addSound("atraviesa%s,.wav"%(namedLocation))
                            elif numero3 == 65:
                                addSound("en curva %s,.wav"%(namedLocation))
                            elif numero3 == 66:
                                addSound("conduciendo por%s,.wav"%(namedLocation))
                            elif numero3 == 67:
                                addSound("viajando por%s,.wav"%(namedLocation))
                            elif numero3 == 68:
                                addSound("cruzando%s,.wav"%(namedLocation))
                            elif numero3 == 69:
                                addSound("paseando por%s,.wav"%(namedLocation))
                            elif numero3 == 70:
                                addSound("entrando en%s,.wav"%(namedLocation))
                            elif numero3 == 71:
                                addSound("volando por%s,.wav"%(namedLocation))
                            elif numero3 == 72:
                                addSound("%s, en dirección a %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 73:
                                addSound("%s, cerca de %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 74:
                                addSound("%s, en el área de %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 75:
                                addSound("%s, en la zona de %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 76:
                                addSound("%s, en %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 77:
                                addSound("%s, en las inmediaciones de %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 78:
                                addSound("%s, en la recta anterior a %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 79:
                                addSound("%s, en la recta cercana a %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 80:
                                addSound("%s, en la cuali por %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 81:
                                addSound("%s, en cuali por %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 82:
                                addSound("%s, en la lucha por %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 83:
                                addSound("%s, en la vuelta por %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 84:
                                addSound("%s, en vuelta buena por %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 85:
                                addSound("%s, en la cuali hacia %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 86:
                                addSound("%s, en la sesión hacia %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 87:
                                addSound("%s, avanzando hacia %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 88:
                                addSound("%s, aproximándose a %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 89:
                                addSound("%s, cerca de %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 90:
                                addSound("%s, en el área de %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 91:
                                addSound("%s, en la zona de %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 92:
                                addSound("%s, en %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 93:
                                addSound("%s, en las inmediaciones de %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 94:
                                addSound("%s, en una curva cerca de %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 95:
                                addSound("%s, en una recta cerca de %s,.wav"%(dirABSounds, namedLocation))
                            elif numero3 == 96:
                                addSound("%s, en la cuali por %s,.wav"%(dirABSounds, namedLocation))
                            pVoiceTimeedu = clock()











            if bIsRace and report == "LAP_NUMBER" and (lapCount > 0 or AppDic["Car0LapTime"] > raceStartDelay):
                if not AppDic[keysCarRaceFinished[carId]]: # ac.getCarState(car, acsys.CS.RaceFinished) == 0:

                        addSound("%sen vuelta_%d.wav"%(dirABSounds, lapCount + 1))
                        pVoiceTimeedu = clock()    
                    
            if bIsRace and report == "START_POSITION":
                startKey = "".join(["Car", strCarId, "StartPosition"]) #"Car%dStartPosition"%(car)
                if startKey in dic:
                    try:
                        #ConsoleLog("Announcing Starting Position")
                        keyNum = str(int(dic[startKey]) + 1)
                        if randInRange(0, 1) == 0 or not keyNum in dicNumbers:

                            
                                addSound("%s_ha tomado la salida en posición_%d.wav"%(dirABSounds, int(dic[startKey]) + 1))
                                pVoiceTimeedu = clock()
                        else:
                            #ConsoleLog("Speaking from dicNumbers 100")

                            
                                addSound("%scomenzó en posición_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))
                                pVoiceTimeedu = clock()
                    except:
                        #ConsoleLog("ERROR Announcing Starting Position")
                        pass
                else:
                    if verbose:
                        ConsoleLog("startKey NOT FOUND")

        #what position?
        #ConsoleLog("Position 100")

        if verbose:
            ConsoleLog("100 - Driver %s is in position %d"%(driverName, position + 1))
        
        if AppDic["Car0LapTime"] == 0.0 and bIsRace:
            keyNum = str(position + 1)
            if randInRange(0, 1) == 0 or not keyNum in dicNumbers:
                #addSound("%sis_starting_p-%d.wav"%(dirABSounds, position + 1))
                addSound("%ssale en posición_%d.wav"%(dirABSounds, position + 1))
                
            else:
                #ConsoleLog("Speaking from dicNumbers 200")
                #addSound("%sis_starting_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))            
                addSound("%ssale_%s.wav"%(dirABSounds, dicNumbers[keyNum]))            
        elif AppDic[keysCarRaceFinished[carId]] == 0 or not bIsRace:
            if norepetirenpits == 0:
                keyNum = str(position + 1)

                
                #EDU SUSSY
                #leo el fichero de probabilidad de leer las frases
                # Lee el número del archivo externo
                Name_File = 'apps\\python\\AnnouncerBot\\probabilidadsusy.txt'
                with open(Name_File, 'r')as f:
                    probabilidad = int(f.read())
                    print(probabilidad)
                    ConsoleLog("numero2: PLATANDO SE ENCUENTRA EN LA P probabilidad %s"%(probabilidad))
                # Si la probabilidad es mayor que 0 y menor que 100
                # Si la probabilidad es mayor que 0 y menor que 100
                if 0 < probabilidad < 101:
                    # Ejecuta la sentencia if con la probabilidad correspondiente
                    azarnum = random.uniform(0, 100)
                    ConsoleLog("numeroazar: %s"%(azarnum))
                    if azarnum < probabilidad :


                        #bIsMutedForIntro = True                
                        #qSpeech.queue.clear()
                        #dic.clear()                                
                        #sessionStartTime = clock()


                        # startupinfo = subprocess.STARTUPINFO()
                        # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                        # # Ejecutar el comando "taskkill" para detener "Audiodg.exe"
                        # subprocess.call(["taskkill", "/F", "/IM", "Audiodg.exe"], startupinfo=startupinfo)


                        #Edu este if de numero2 no quiero que lo lea cuando es qualy. Solo cuando es carrera
                        if bIsRace: #si es carrera lee estas frases    

                                #if is lap 1 read this phrases     edu si es primera vuelta
                                if lapCount == 0:
                                    tiempo_actual = time.time()
                                    ConsoleLog("tiempo_actual: %s"%(tiempo_actual))
                                    
                                    

                                    numero2 = randInRange(0, 9)
                                    if numero2 == 0:
                                        addSound("%sha salido con mucho ritmo y se encuentra en posición %d_.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 1:
                                        addSound("%s_ha tenido una salida limpia y alcanza la posición %d_en esta primera vuelta.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 2:
                                        addSound("%s con mucho ritmo en la posición %d_en esta primera vuelta.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 3:
                                        addSound("%s en esta primera vuelta ataca en la posición %d_.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 4:
                                        addSound("%ssalió muy fuerte y está en p_%d_en esta primera vuelta.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 5:
                                        addSound("%s ha tenido una buena salida, lo vemos en p_%d_.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 6:
                                        addSound("%s tras un buen arranque de carrera,  en p %d _._.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 7:
                                        addSound("%sen la primera vuelta, ahora_mismo_es_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))
                                    elif numero2 == 8:
                                        addSound("%s_en_primera_vuelta_en_p_%d_.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 9:
                                        addSound(".%s_ha hecho una estupenda salida y se mantiene_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))    
                                    pVoiceTimeedu = clock()
                                    
                                
                                    #edu
                                    #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                                    #cuando han pasado 15 segundos sin que se haya dicho nada
                                   



                                else:
                                    numero2 = randInRange(0, 55)
                                    ConsoleLog("ME LO SALTO")

                                    #bIsMutedForIntro = True                
                                    #qSpeech.queue.clear()
                                    #dic.clear()                                
                                    #sessionStartTime = clock()




                                    if numero2 == 0:
                                        addSound("%sactualmente mantiene la posición %d_.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 1:
                                        addSound("%s_situado en posición %d_.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 2:
                                        addSound("%s custodiando la posición %d_.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 3:
                                        addSound("%s defendiendo la posición %d_.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 4:
                                        addSound("%sse encuentra en p_%d_.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 5:
                                        addSound("%s ubicado en p_%d_.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 6:
                                        addSound("%s plantado en p %d _._.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 7:
                                        addSound("%sahora_mismo_es_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))
                                    elif numero2 == 8:
                                        addSound("%s_en_pantalla_en_p_%d_.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 9:
                                        addSound(".%s_se mantiene_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))       
                                    elif numero2 == 10:
                                        #si position + 1 es 1 entonces lee "primero"
                                        if position + 1 == 1:
                                            addSound("%sse encuentra en primera posición.wav"%(dirABSounds))
                                        else:
                                            addSound("%s se encuentra en la posición %d en estos momentos.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 11:
                                        addSound("%s está compitiendo en la posición %d.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 12:
                                        addSound("%s está luchando por la posición %d.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 13:
                                        addSound("%s está en la posición %d en esta vuelta.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 14:
                                        #si position + 1 es 1 entonces lee "primero"
                                        if position + 1 == 1:
                                            addSound("%sse encuentra en primera posición en la carrera.wav"%(dirABSounds))
                                        else:
                                            addSound("%s se encuentra en la posición %d en la carrera_.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 15:
                                        #si position + 1 es 1 entonces lee "primero"
                                        if position + 1 == 1:
                                            addSound("%sse encuentra en primera posición ahora mismo.wav"%(dirABSounds))
                                        else:
                                            addSound("%s está en la posición %d ahora_.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 16:
                                        #si position + 1 es 1 entonces lee "primero"
                                        if position + 1 == 1:
                                            addSound("%sse encuentra en primera posición.wav"%(dirABSounds))
                                        else:
                                            addSound("%s se encuentra en la posición %d en la carrera,.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 17:
                                        addSound("%s está en la posición %d justo ahora_.wav"%(dirABSounds, position + 1))   
                                    elif numero2 == 18:
                                        addSound("%s se encuentra actualmente en la posición %d en la pista.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 19:
                                        addSound("%s está en la posición %d en la carrera.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 20:
                                        addSound("%s está ocupando la posición %d en este momento.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 21:
                                        addSound("%s se ha colocado en la posición %d en la pista.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 22:
                                        addSound("%s se encuentra en la posición %d en este momento de la carrera.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 23:
                                        addSound("%s está compitiendo en la posición %d en la pista.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 24:
                                        addSound("%s se encuentra en la posición %d en este instante de la carrera.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 25:
                                        addSound("%s está en la posición %d en este momento de la carrera.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 26:
                                        addSound("%s se encuentra en la posición %d en esta vuelta de la carrera.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 27:
                                        addSound("%s está en la posición %d en esta etapa de la carrera.wav"%(dirABSounds, position + 1))            
                                    elif numero2 == 28:
                                        addSound("%s se encuentra en la posición %d gestionando bien la carrera.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 29:
                                        addSound("%s está en la posición %d _ , una buena posición para adelantar.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 30:
                                        addSound("%s se encuentra en la posición %d y necesita mejorar su tiempo.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 31:
                                        addSound("%s está en la posición %d , está luchando por subir algún puesto.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 32:
                                        addSound("%s se encuentra en la posición %d y manteniendo su ritmo.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 33:
                                        addSound("%s está en la posición %d _._una buena posición para él.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 34:
                                        addSound("%s se encuentra en la posición %d, está buscando mejorar su tiempo.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 35:
                                        addSound("%s está en la posición %d _._es una posición competitiva.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 36:
                                        addSound("%s se encuentra en la posición %d , está luchando por mantenerse.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 37:
                                        addSound("%s está en la posición %d y haciendo una gran carrera.wav"%(dirABSounds, position + 1))            
                                    elif numero2 == 38:
                                        addSound("%s se encuentra en la posición %d en este momento.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 39:
                                        addSound("%s está manteniéndose en carrera en la posición %d.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 40:
                                        addSound("%s ocupa la posición %d en la parrilla actual.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 41:
                                        addSound("%s está avanzando en la posición %d en la carrera.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 42:
                                        addSound("%s ha subido a la posición %d y se mantiene.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 43:
                                        addSound("%s ha perdido posiciones y se encuentra ahora en la P %d.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 44:
                                        addSound("%s se encuentra en la posición %d .wav"%(dirABSounds, position + 1))
                                    elif numero2 == 45:
                                        addSound("%s está en la posición %d .wav"%(dirABSounds, position + 1))
                                    elif numero2 == 46:
                                        addSound("%s ha logrado mantenerse en la posición %d tras varios adelantamientos.wav"%(dirABSounds, position + 1))            
                                    elif numero2 == 47:
                                        addSound("%s se encuentra en la posición %d en la actualidad.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 48:
                                        addSound("%s está en la posición %d en esta carrera.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 49:
                                        addSound("%s se mantiene en la posición %d.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 50:
                                        addSound("%s está en la posición %d en este momento.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 51:
                                        addSound("%s se encuentra en la posición %d .wav"%(dirABSounds, position + 1))
                                    elif numero2 == 52:
                                        addSound("%s está en la posición %d en este instante.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 53:
                                        addSound("%s se mantiene en la posición %d en la carrera.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 54:
                                        addSound("%s se encuentra en la posición %d en estos momentos.wav"%(dirABSounds, position + 1))
                                    elif numero2 == 55:
                                        addSound("%s está en la posición %d en este momento de la carrera.wav"%(dirABSounds, position + 1))            
                                    pVoiceTimeedu = clock()
                            
                                #edu
                                #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                                #cuando han pasado 15 segundos sin que se haya dicho nada
                                                      




                        
                        
                        
                        
                        else: #edu esto significa que no es carrera...asi que es qualy o es practica
                            #if currentLap == 1:  # Si es la primera vuelta

                            lapCount = ac.getCarState(car, acsys.CS.LapCount)
                            focusedCarLapCount = AppDic["".join(["Car", strCarId, "LapCount"])]  # ac.getCarState(car, acsys.CS.LapCount) #if ac.getCarState(car, acsys.CS.LapCount) > 1
                            if focusedCarLapCount == 0:  # Si es la primera vuelta    
                                numero2 = randInRange(0, 23)
                                if numero2 == 0:
                                    addSound("%s intentará en la siguiente vuelta su vuelta de qualy.wav"%(dirABSounds))
                                elif numero2 == 1:
                                    addSound("%s ajustando el coche y calentando ruedas para su intento de qualy.wav"%(dirABSounds))
                                elif numero2 == 2:
                                    addSound("%s está preparando el coche para hacer su vuelta lanzada.wav"%(dirABSounds))
                                elif numero2 == 3:
                                    addSound("%s en pantalla , que ya está también en la vuelta de calentamiento.wav"%(dirABSounds))
                                elif numero2 == 4:
                                    addSound("%stambién ha salido ya de pits y se dispone a calentar neumáticos.wav"%(dirABSounds))
                                elif numero2 == 5:
                                    addSound("%sestá en su vuelta de guarmmap calentando los neumáticos.wav"%(dirABSounds))
                                elif numero2 == 6:
                                    addSound("%s ya ha toma la calle de salida de boxes y espera la luz verde de su equipo." % dirABSounds)
                                elif numero2 == 7:
                                    addSound("La tensión en el ambiente es palpable, %s está a punto de comenzar la vuelta lanzada." % dirABSounds)
                                elif numero2 == 8:
                                    addSound("El equipo de %s está realizando los últimos ajustes en el coche antes de su intento de vuelta" % dirABSounds)
                                elif numero2 == 9:
                                     addSound("Vemos a %s se encuentra en su vuelta de guarmmap antes de su intento de marcar un tiempo válido." % dirABSounds)
                                elif numero2 == 10:
                                    addSound("%s está realizando una vuelta de reconocimiento del circuito y está a punto de tomar la salida lanzada ." % dirABSounds)
                                elif numero2 == 11:
                                    addSound(" %s está listo para darlo todo en la pista.En minutos comenzarán los pilotos a marcar tiempos." % dirABSounds)    
                                elif numero2 == 12:
                                    addSound("El equipo de %s está revisando los datos del coche para mejorar su rendimiento en la siguiente vuelta." % dirABSounds)
                                elif numero2 == 13:
                                    addSound("¡Atención, atención! %s estaba ajustando el setup en boxes y ya ha salido a la pista para su vuelta lanzada." % dirABSounds)
                                elif numero2 == 14:
                                    addSound("%s  está en la zona de espera para tomar la salida lanzada." % dirABSounds)
                                elif numero2 == 15:
                                    addSound("%s está ajustando su asiento y colocando sus manos en el volante para su intento de qualy." % dirABSounds)
                                elif numero2 == 16:
                                    addSound("El equipo de %s está haciendo los últimos ajustes al coche antes de su vuelta lanzada." % dirABSounds)
                                elif numero2 == 17:
                                    addSound("%s está rodando en su vuelta de guarmmap y se prepara para su intento de marcar un buen tiempo." % dirABSounds)
                                elif numero2 == 18:
                                    addSound("%s ya está en pista. está listo para hacer su mejor tiempo en la siguiente vuelta." % dirABSounds)
                                elif numero2 == 19:
                                    addSound("%s está visualizando mentalmente la pista antes de tomar la salida para su vuelta de calificación." % dirABSounds)
                                elif numero2 == 20:
                                    addSound(" %s y todo su equipo están muy motivados. están animando al piloto para que dé lo mejor de sí en la siguiente vuelta." % dirABSounds)
                                elif numero2 == 21:
                                    addSound("%s está a punto de comenzar su vuelta lanzada." % dirABSounds)
                                elif numero2 == 22:
                                    addSound("%s está saliendo de boxes y acelerando hacia la salida de pista para su intento de qualy." % dirABSounds)
                                elif numero2 == 23:
                                    addSound("%s en pista con un coche en óptimas condiciones , está listo para dar una gran vuelta en la pista." % dirABSounds)
                                elif numero2 == 24:
                                    addSound("%s está concentrado en el trabajo y listo para sacar el máximo provecho de su coche en la siguiente vuelta." % dirABSounds)
                                pVoiceTimeedu = clock()                                    
                                    
                            else:
                                numero2 = randInRange(0, 55)
                                if numero2 == 0:
                                    addSound("%sactualmente en la posición %d_.wav"%(dirABSounds, position + 1))
                                elif numero2 == 1:
                                    addSound("%s_situado en posición %d_.wav"%(dirABSounds, position + 1))
                                elif numero2 == 2:
                                    addSound("%s custodiando la posición %d_.wav"%(dirABSounds, position + 1))
                                elif numero2 == 3:
                                    addSound("%s defendiendo la posición %d_.wav"%(dirABSounds, position + 1))
                                elif numero2 == 4:
                                    addSound("%sse encuentra en p_%d_.wav"%(dirABSounds, position + 1))
                                elif numero2 == 5:
                                    addSound("%s ubicado en p_%d_.wav"%(dirABSounds, position + 1))
                                elif numero2 == 6:
                                    addSound("%s plantado en p %d _._.wav"%(dirABSounds, position + 1))
                                elif numero2 == 7:
                                    addSound("%sahora_mismo_es_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))
                                elif numero2 == 8:
                                    addSound("%s_en_pantalla_en_p_%d_.wav"%(dirABSounds, position + 1))
                                elif numero2 == 9:
                                    addSound(".%s_se encuentra_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))       
                                elif numero2 == 10:
                                    addSound("%s se encuentra en la posición %d en estos momentos.wav"%(dirABSounds, position + 1))
                                elif numero2 == 11:
                                    addSound("%s está compitiendo en la posición %d.wav"%(dirABSounds, position + 1))
                                elif numero2 == 12:
                                    addSound("%s está luchando por la posición %d.wav"%(dirABSounds, position + 1))
                                elif numero2 == 13:
                                    addSound("%s está en la posición %d en esta vuelta.wav"%(dirABSounds, position + 1))
                                elif numero2 == 14:
                                    addSound("%s se encuentra en la posición %d en la cuali_.wav"%(dirABSounds, position + 1))
                                elif numero2 == 15:
                                    addSound("%s está en la posición %d ahora_.wav"%(dirABSounds, position + 1))
                                elif numero2 == 16:
                                    addSound("%s se encuentra en la posición %d en la cuali,.wav"%(dirABSounds, position + 1))
                                elif numero2 == 17:
                                    addSound("%s está en la posición %d justo ahora_.wav"%(dirABSounds, position + 1))   
                                elif numero2 == 18:
                                    addSound("%s se encuentra actualmente en la posición %d en la pista.wav"%(dirABSounds, position + 1))
                                elif numero2 == 19:
                                    addSound("%s está en la posición %d en la cuali.wav"%(dirABSounds, position + 1))
                                elif numero2 == 20:
                                    addSound("%s está ocupando la posición %d en este momento.wav"%(dirABSounds, position + 1))
                                elif numero2 == 21:
                                    addSound("%s se ha colocado en la posición %d en la pista.wav"%(dirABSounds, position + 1))
                                elif numero2 == 22:
                                    addSound("%s se encuentra en la posición %d en este momento de la cuali.wav"%(dirABSounds, position + 1))
                                elif numero2 == 23:
                                    addSound("%s está compitiendo en la posición %d en la pista.wav"%(dirABSounds, position + 1))
                                elif numero2 == 24:
                                    addSound("%s se encuentra en la posición %d en este instante de la cuali.wav"%(dirABSounds, position + 1))
                                elif numero2 == 25:
                                    addSound("%s está en la posición %d en este momento de la cuali.wav"%(dirABSounds, position + 1))
                                elif numero2 == 26:
                                    addSound("%s se encuentra en la posición %d en esta vuelta de la cuali.wav"%(dirABSounds, position + 1))
                                elif numero2 == 27:
                                    addSound("%s está en la posición %d en esta etapa de la cuali.wav"%(dirABSounds, position + 1))            
                                elif numero2 == 28:
                                    addSound("%s se encuentra en la posición %d gestionando bien la cuali.wav"%(dirABSounds, position + 1))
                                elif numero2 == 29:
                                    addSound("%s está en la posición %d _ , una posición con todavía margen de mejora.wav"%(dirABSounds, position + 1))
                                elif numero2 == 30:
                                    addSound("%s se encuentra en la posición %d y necesita mejorar su tiempo.wav"%(dirABSounds, position + 1))
                                elif numero2 == 31:
                                    addSound("%s está en la posición %d y luchando por subir algún puesto.wav"%(dirABSounds, position + 1))
                                elif numero2 == 32:
                                    addSound("%s se encuentra en la posición %d y manteniendo su ritmo de cuali.wav"%(dirABSounds, position + 1))
                                elif numero2 == 33:
                                    addSound("%s está en la posición %d _._una buena posición para él en esta cuali.wav"%(dirABSounds, position + 1))
                                elif numero2 == 34:
                                    addSound("%s se encuentra en la posición %d y buscando mejorar su tiempo.wav"%(dirABSounds, position + 1))
                                elif numero2 == 35:
                                    addSound("%s está en la posición %d _._es una posición competitiva.wav"%(dirABSounds, position + 1))
                                elif numero2 == 36:
                                    addSound("%s se encuentra en la posición %d y luchando por mantenerse.wav"%(dirABSounds, position + 1))
                                elif numero2 == 37:
                                    addSound("%s está en la posición %d y haciendo una buena cuali.wav"%(dirABSounds, position + 1))            
                                elif numero2 == 38:
                                    addSound("%s se encuentra en la posición %d en este momento.wav"%(dirABSounds, position + 1))
                                elif numero2 == 39:
                                    addSound("%s está manteniéndose en esta cuali en la posición %d.wav"%(dirABSounds, position + 1))
                                elif numero2 == 40:
                                    addSound("%s ocupa la posición %d en la parrilla de hoy.wav"%(dirABSounds, position + 1))
                                elif numero2 == 41:
                                    addSound("%s está avanzando en la posición %d en la cuali.wav"%(dirABSounds, position + 1))
                                elif numero2 == 42:
                                    addSound("%s ha subido a la posición %d y se mantiene.wav"%(dirABSounds, position + 1))
                                elif numero2 == 43:
                                    addSound("%s ha perdido posiciones y se encuentra ahora en la P %d.wav"%(dirABSounds, position + 1))
                                elif numero2 == 44:
                                    addSound("%s se encuentra en la posición %d .wav"%(dirABSounds, position + 1))
                                elif numero2 == 45:
                                    addSound("%s está en la posición %d .wav"%(dirABSounds, position + 1))
                                elif numero2 == 46:
                                    addSound("%s ha logrado mantenerse en la posición %d tras varios intentos de vuelta rápida.wav"%(dirABSounds, position + 1))            
                                elif numero2 == 47:
                                    addSound("%s se encuentra en la posición %d en la actualidad.wav"%(dirABSounds, position + 1))
                                elif numero2 == 48:
                                    addSound("%s está en la posición %d en esta cuali.wav"%(dirABSounds, position + 1))
                                elif numero2 == 49:
                                    addSound("%s se mantiene en la posición %d.wav"%(dirABSounds, position + 1))
                                elif numero2 == 50:
                                    addSound("%s está en la posición %d en este momento.wav"%(dirABSounds, position + 1))
                                elif numero2 == 51:
                                    addSound("%s se encuentra en la posición %d .wav"%(dirABSounds, position + 1))
                                elif numero2 == 52:
                                    addSound("%s está en la posición %d en este instante.wav"%(dirABSounds, position + 1))
                                elif numero2 == 53:
                                    addSound("%s se mantiene en la posición %d en la cuali.wav"%(dirABSounds, position + 1))
                                elif numero2 == 54:
                                    addSound("%s se encuentra en la posición %d en estos momentos.wav"%(dirABSounds, position + 1))
                                elif numero2 == 55:
                                    addSound("%s está en la posición %d en este momento de la cuali.wav"%(dirABSounds, position + 1))            
                                    norepetirenpits = 0
                                    ConsoleLog("repetir en pits ahora es falso")
                                pVoiceTimeedu = clock()
                        
                        
                        
                        #edu
                        #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                        #cuando han pasado 15 segundos sin que se haya dicho nada
                        




                    ###################addSound(dirABSounds + "..wav")

        else: #  dic["raceOver"] == 1:
            #addSound("%sfinished_p-%d.wav"%(dirABSounds, position + 1))
           
            
                keyNum = str(position + 1)
                numero10 = randInRange(0, 38)	
                if numero10 == 0:
                    addSound("%sha terminado en_p_%d.wav"%(dirABSounds, position + 1))
                elif numero10 == 1:
                    addSound("%sterminó_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))
                elif numero10 == 2:
                    addSound("%sfinaliza_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))
                elif numero10 == 3:
                    addSound("%sha conseguido terminar_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))
                elif numero10 == 4:
                    addSound("%sfinalmente es_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))
                elif numero10 == 5:
                    addSound("%sha logrado ser_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))
                elif numero10 == 6:
                    addSound("%sterminó_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))
                elif numero10 == 7:
                    addSound("%s se adjudica la p_%d.wav"%(dirABSounds, position + 1))                
                elif numero10 == 8:
                    addSound("%s viendo la bandera a cuadros es%s_.wav"%(dirABSounds, dicNumbers[keyNum]))
                elif numero10 == 9:
                    addSound("%scruza por meta en p_%s_.wav"%(dirABSounds, dicNumbers[keyNum])) 
                elif numero10 == 10:
                    addSound("%s ha terminado en la posición %d"%(driverName, position + 1))
                elif numero10 == 11:
                    addSound("%s ha finalizado en el puesto %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 12:
                    addSound("%s ha conseguido terminar en el lugar %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 13:
                    addSound("%s ha logrado ser el número %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 14:
                    addSound("%s ha terminado en el puesto %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 15:
                    addSound("%s se ha adjudicado el lugar %d"%(driverName, position + 1))
                elif numero10 == 16:
                    addSound("%s ve la bandera a cuadros en el lugar %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 17:
                    addSound("%s cruza la meta en el lugar %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 18:
                    addSound("%s ha terminado en la posición %d"%(driverName, position + 1))
                elif numero10 == 19:
                    addSound("%s ha finalizado en el puesto %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 20:
                    addSound("%s ha conseguido terminar en el lugar %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 21:
                    addSound("%s ha logrado ser el número %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 22:
                    addSound("%s ha terminado en el puesto %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 23:
                    addSound("%s se ha adjudicado el lugar %d"%(driverName, position + 1))
                elif numero10 == 24:
                    addSound("%s ve la bandera a cuadros en el lugar %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 25:
                    addSound("%s cruza la meta en el lugar %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 26:
                    addSound("%s ha terminado en la posición %d"%(driverName, position + 1))
                elif numero10 == 27:
                    addSound("%s ha finalizado en el puesto %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 28:
                    addSound("%s ha conseguido terminar en el lugar %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 29:
                    addSound("%s ha logrado ser el número %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 30:
                    addSound("%s ha terminado en el puesto %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 31:
                    addSound("%s se ha adjudicado el lugar %d"%(driverName, position + 1))
                elif numero10 == 32:
                    addSound("%s ve la bandera a cuadros en el lugar %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 33:
                    addSound("%s cruza la meta en el lugar %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 34:
                    addSound("%s se encuentra en la posición %d"%(driverName, position + 1))
                elif numero10 == 35:
                    addSound("%s ha completado la carrera en el puesto %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 36:
                    addSound("%s ha finalizado la carrera en el lugar %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 37:
                    addSound("%s ha logrado terminar la carrera en el puesto %s"%(driverName, dicNumbers[keyNum]))
                elif numero10 == 38:
                    addSound("%s se encuentra en el lugar %s al final de la carrera"%(driverName, dicNumbers[keyNum]))
                pVoiceTimeedu = clock()
                
        #edu
        #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
        #cuando han pasado 15 segundos sin que se haya dicho nada
        
            
            
        if not AppDic["RaceOver"] and qSpeech.qsize() < qSkipLength and not isSpeaking and not (dic["VirtualSafetyCar"] == 2 or dic["VirtualSafetyCar"] == 4):
            #ConsoleLog("Checking PerformanceMeter, bIsQually = %d, perfMeter = %0.4f"%(bIsQually, ac.getCarState(car, acsys.CS.PerformanceMeter)))
            perfMeter = AppDic[keysCarPerfMeter[carId]] # ac.getCarState(car, acsys.CS.PerformanceMeter)
            if bIsQually and perfMeter < -0.01 and perfMeter > - 29.0:
                #ConsoleLog("Checking strDelta, acsys.CS.PerformanceMeter = %0.4f"%(ac.getCarState(car, acsys.CS.PerformanceMeter)))
                strDelta = "%0.2f"%perfMeter
                strDelta = strDelta.replace("-", "").strip()
                if not strDelta == "0.00":
                    #ConsoleLog("Found Delta %s"%(strDelta))
                    dic["namedLocationLastReported"] = clock()
                    #ConsoleLog("100")
                    #ConsoleLog("300")
                    #ConsoleLog("currPoT = %0.3f, carDistance = %0.1f, trackLength = %0.1f"%(carCurrPoT, carDistance, trackLength))
                    if carDistance > 600.0 and carDistance < (trackLength - 400.0):
                        #ConsoleLog("400")
                        #don't actually report this when they are close to S/F
                        ###################addSound(dirABSounds + "..wav")
                        addSound("%s_está en vuelta lanzada y está mejorando su delta en_%s_segundos_.wav"%(dirABSounds, strDelta))
                        pVoiceTimeedu = clock()
        
            if qClockReported + qClockDelay < clock() and ballast > 0:
                #fnameKG = "%scargado_con_%d%s.wav"%(dirABSounds, ballast, ballastName)



                #EDU SUSSY
                #leo el fichero de probabilidad de leer las frases
                # Lee el número del archivo externo
                Name_File = 'apps\\python\\AnnouncerBot\\probabilidadsusy.txt'
                with open(Name_File, 'r')as f:
                    probabilidad = int(f.read())
                    print(probabilidad)
                    ConsoleLog("numero11: LASTRES probabilidad %s"%(probabilidad))
                # Si la probabilidad es mayor que 0 y menor que 100
                # Si la probabilidad es mayor que 0 y menor que 100
                if 0 < probabilidad < 101:
                    # Ejecuta la sentencia if con la probabilidad correspondiente
                    azarnum = random.uniform(0, 100)
                    ConsoleLog("numeroazar: %s"%(azarnum))
                    if azarnum < probabilidad :


                        #bIsMutedForIntro = True                
                        #qSpeech.queue.clear()
                        #dic.clear()                                
                        #sessionStartTime = clock()
                           



                        
                        
                            numero11 = randInRange(0, 29)	
                            if numero11 == 0:
                                fnameKG = "%s_llevando_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 1:
                                fnameKG = "%s_penalizado_con_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 2:
                                fnameKG = "%s_colmado_con_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 3:
                                fnameKG = "%s_rodando_con_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 4:
                                fnameKG = "%s_soportando__%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 5:
                                fnameKG = "%s_aguantando_con_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 6:
                                fnameKG = "%s_con_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 7:
                                fnameKG = "%s_algo lento_por sus_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 8:
                                fnameKG = "%s_cargando__%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 9:
                                fnameKG = "%s_lastrado_con_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 10:
                                fnameKG = "%s_con_una carga_de_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 11:
                                fnameKG = "%s_empeñado_con_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 12:
                                fnameKG = "%s_sobresaliendo_con_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 13:
                                fnameKG = "%s_con_%d%s_en_el_coche.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 14:
                                fnameKG = "%s_arrastrando_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 15:
                                fnameKG = "%s_con_%d%s_en_el_maletero.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 16:
                                fnameKG = "%s_luchando_con_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 17:
                                fnameKG = "%s_llevando_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 18:
                                fnameKG = "%s_penalizado_con_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 19:
                                fnameKG = "%s_llevando a la rubia de_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 20:
                                fnameKG = "%s_cargando una rubia de_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 21:
                                fnameKG = "%s_con_%d%s_en_el_capó.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 22:
                                fnameKG = "%s_con_%d%s_en_el_asiento_trasero.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 23:
                                fnameKG = "%s_con_%d%s_en_el_baúl.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 24:
                                fnameKG = "%s_con_%d%s_en_el_maletero_delantero.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 25:
                                fnameKG = "%s_pesado_con_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 26:
                                fnameKG = "%s_trabajando_con_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 27:
                                fnameKG = "%s_desafiando_a_%d%s.wav.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 28:
                                fnameKG = "%s_sobrecargado_con_%d%s.wav"%(dirABSounds, ballast, ballastName)
                            elif numero11 == 29:
                                fnameKG = "%s_luchando_contra_%d%s.wav"%(dirABSounds, ballast, ballastName)    

                       





                    #edu
                    #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                    #cuando han pasado 15 segundos sin que se haya dicho nada
                   




                tmpKey = "car%dReportedBallast"%(car)
                if not tmpKey in dic or report == "BALLAST":
                    if checkSound(fnameKG) and qSpeech.qsize() < qSkipLength:
                        dic[tmpKey] = 1
                        addSound(fnameKG)
            
                        
            if not bIsQually and qClockReported + qClockDelay < clock():
                #only report tyres once per session?  can report when they change?
                tmpKey = "coche%dcompuestos%s"%(car, ac.getCarTyreCompound(car))
                if not tmpKey in dic or report == "TYRES":
                    dic[tmpKey] = 1
                    reportTyreCompoundAB(car)
            elif bIsQually: # and qClockReported + qClockDelay < clock():
                #only report compound once per qually period?
                tmpKey = "Coche%dCompuestos%s"%(car, ac.getCarTyreCompound(car))
                if not tmpKey in dic or report == "TYRES":
                    dic[tmpKey] = 1
                    reportTyreCompoundAB(car)
                      

            #carFolderName = ac.getCarName(car)
            tmpKey = "".join(["Car", str(car), "FullName", ac.getCarName(car)])
            if (not tmpKey in dic or report == "CAR_NAME") and (uiCars["uniqueMakes"] > 2 or uiCars["uniqueModels"] > 2):
                carNickName = getCarNickName(car)
                if not carNickName == "":
                    addSound("%sconduciendo un_%s.wav"%(dirABSounds, carNickName.replace(" ", "_")))
            else:                      
                #in what model - skip announcing models for now?
                tmpKey = "Car%dModel"%(car)
                if False: # tmpKey not in dic or report == "MODEL" and False:
                    dic[tmpKey] = 1
                    #ConsoleLog("Reporting Car Name 100")
                    tmpKey = "uniqueModels"
                    if tmpKey in uiCars:
                        #ConsoleLog("Reporting Car Name 200")
                        if uiCars[tmpKey] > 2:
                            #ConsoleLog("Reporting Car Name 300")
                            tmpKey = "Car-%s-Model"%(ac.getCarName(car))
                            #ConsoleLog("Reporting Car Name 400")
                            if tmpKey in uiCars:
                                #ConsoleLog("Reporting Car Name 500")
                                addSound("%sin_a_%s.wav"%(dirABSounds, uiCars[tmpKey].replace(" ", "_")))
                #in what make
                elif report == "MAKE":
                    #ConsoleLog("Reporting Car Name 100")
                    tmpKey = "uniqueMakes"
                    if tmpKey in uiCars:
                        #ConsoleLog("Reporting Car Name 200")
                        if uiCars[tmpKey] > 2:
                            #ConsoleLog("Reporting Car Name 300")
                            tmpKey = "Car-%s-Make"%(ac.getCarName(car))
                            #ConsoleLog("Reporting Car Name 400")
                            if tmpKey in uiCars:
                                #ConsoleLog("Reporting Car Name 500")
                                addSound("%sconduce un_%s.wav"%(dirABSounds, uiCars[tmpKey].replace(" ", "_")))
                               
            if bIsRace and qSpeech.qsize() < qSkipLength and not report == "FASTEST_LAP": #comment out the qsize code for testing
                if qClockReported + qClockDelay < clock():
                    reportP2PActivationsAB(car)

                if closestCar >= 0 and not AppDic[keysCarInPits[closestCar]] and closestCarGap > 0.0 and (lapCount > 0 or AppDic["Car0LapTime"] > raceStartDelay):
                    closestDriverName = getABotDriverName(closestCar)
                    closestAB_driverName = closestDriverName.replace(" ", "_")
                    fname = dirABSounds + closestAB_driverName + ".wav"

                    if checkSound(fname):
                        #focusedCarLapCount = AppDic["".join(["Car", strCarId, "LapCount"])] # ac.getCarState(car, acsys.CS.LapCount)
                        #focusedCarCurrPoT = AppDic["".join(["Car", strCarId, "PoT"])] #ac.getCarState(car,acsys.CS.NormalizedSplinePosition)
                        focusedCarDistance = AppDic[keysCarDistance[carId]] * trackLength
                        #closestCarLapCount = ac.getCarState(closestCar, acsys.CS.LapCount)
                        #closestCarCurrPoT = ac.getCarState(closestCar,acsys.CS.NormalizedSplinePosition)              
                        closestCarDistance = AppDic[keysCarDistance[closestCar]] * trackLength
                        
                        #can we estimate the gap in time based on average speed?
                        #kmh and distance to seconds?
                        
                        gapRounded = "%.1f"%(round(closestCarGap, 1))
                        
                        #Trailing, Following, Chasing, Battling, Fending Off, Leading, Ahead of, in front of, far in front of, barely beating, slightly
                        #ConsoleLog("Closest Car is %d, Gap is %0.4f"%(closestCar, closestCarGap))
                        #ConsoleLog("Closest Car = %d, Driver Name %s, Distance = %0.6f, Gap = %0.4f"%(closestCar, getABotDriverName(closestCar), closestCarDistance, closestCarGap))                            
                        
                        if isVoiceTTS:
                            if gapRounded == "0.0":
                                addSound(dirABSounds + "en lucha con.wav")
                                addSound(fname)
                                pVoiceTimeedu = clock()
                                #don't do this all the time
                                if ac.getCarState(car, acsys.CS.LapCount) > 1 and randInRange(0,4) == 1:
                                    tmpKey = "Lap%dDeltaCar%dCar%d"%(ac.getCarState(car, acsys.CS.LapCount), car, closestCar)
                                    if not tmpKey in dic:
                                        dic[tmpKey] = clock()

                                        focusedCarLastLapTime = ac.getCarState(car, acsys.CS.LastLap)
                                        closestCarLastLapTime = ac.getCarState(closestCar, acsys.CS.LastLap)
                                        
                                        if verbose:
                                            ConsoleLog("Last Lap Difference = %0.4f"%(focusedCarLastLapTime - closestCarLastLapTime))
                                        if focusedCarLastLapTime < closestCarLastLapTime:
                                            fltDelta = (focusedCarLastLapTime - closestCarLastLapTime) / 1000
                                            if fltDelta < -0.5:
                                                strDelta = "%0.1f"%(fltDelta)
                                                strDelta = strDelta.replace("-", "").strip()
                                                #strDelta = "%0.2f"%ac.getCarState(focusedCar, acsys.CS.PerformanceMeter)
                                                #ConsoleLog("FocusedCar %0.4f faster on the last lap"%(focusedCarLastLapTime - closestCarLastLapTime))
                                                #FocusedCar -328.0000 faster on the last lap
                                                ###################addSound(dirABSounds + "..wav")
                                                addSound(dirABSounds + "%s_ha sido_%ssegundos_mas rápido que en su vuelta anterior.wav"%(ab_driverName, strDelta))
                                                pVoiceTimeedu = clock()
                                        elif closestCarLastLapTime < focusedCarLastLapTime:
                                            fltDelta = (closestCarLastLapTime - focusedCarLastLapTime) / 1000
                                            if fltDelta < -0.5:
                                                strDelta = "%0.1f"%(fltDelta)
                                                strDelta = strDelta.replace("-", "").strip()
                                                #strDelta = "%0.2f"%ac.getCarState(focusedCar, acsys.CS.PerformanceMeter)
                                                #ConsoleLog("FocusedCar %0.4f faster on the last lap"%(focusedCarLastLapTime - closestCarLastLapTime))
                                                #FocusedCar -328.0000 faster on the last lap
                                                ###################addSound(dirABSounds + "..wav")
                                                addSound(dirABSounds + "%s_ha sido_%ssegundos_mas rápido que en su anterior vuelta.wav"%(closestAB_driverName, strDelta))
                                                pVoiceTimeedu = clock()
                                
                            elif closestCarGap < gapTrailing:
                                if focusedCarDistance > closestCarDistance:


                                    #EDU SUSSY
                                    #leo el fichero de probabilidad de leer las frases
                                    # Lee el número del archivo externo
                                    Name_File = 'apps\\python\\AnnouncerBot\\probabilidadsusy.txt'
                                    with open(Name_File, 'r')as f:
                                        probabilidad = int(f.read())
                                        print(probabilidad)
                                        ConsoleLog("numero14: POR DELANTE probabilidad %s"%(probabilidad))
                                    # Si la probabilidad es mayor que 0 y menor que 100
                                    # Si la probabilidad es mayor que 0 y menor que 100
                                    if 0 < probabilidad < 101:
                                        # Ejecuta la sentencia if con la probabilidad correspondiente
                                        azarnum = random.uniform(0, 100)
                                        ConsoleLog("numeroazar: %s"%(azarnum))
                                        #if azarnum < probabilidad :
                                        if probabilidad < 101:


                                            #bIsMutedForIntro = True                
                                            #qSpeech.queue.clear()
                                            #dic.clear()                                
                                            #sessionStartTime = clock()
                                                

                                            
                                            
                                                numero14 = randInRange(0, 34)
                                                if numero14 == 0:
                                                    addSound(dirABSounds + ",_%s segundos_delante de.wav"%(gapRounded))
                                                elif numero14 == 1:
                                                    addSound(dirABSounds + ",_%s segundos_por delante de.wav"%(gapRounded))
                                                elif numero14 == 2:
                                                    addSound(dirABSounds + ",_%s segundos_sobre.wav"%(gapRounded))
                                                elif numero14 == 3:
                                                    addSound(dirABSounds + ",_%s segundos_de ventaja con.wav"%(gapRounded))
                                                elif numero14 == 4:
                                                    addSound(dirABSounds + ",_%s segundos_de distancia por encima de.wav"%(gapRounded))
                                                elif numero14 == 5:
                                                    
                                                    addSound(dirABSounds + "tiene %s segundos_de ventaja sobre.wav"%(gapRounded))
                                                elif numero14 == 6:
                                                    
                                                    addSound(dirABSounds + "está todavía a %ssegundos_de.wav"%(gapRounded))
                                                elif numero14 == 7:
                                                    
                                                    addSound(dirABSounds + "ahora va %s segundos_delante de.wav"%(gapRounded))
                                                elif numero14 == 8:
                                                    
                                                    addSound(dirABSounds + "precede por %s segundos_a.wav"%(gapRounded))
                                                elif numero14 == 9:
                                                    
                                                    addSound(dirABSounds + "viendo por el retrovisor a %s segundos_a su perseguidor.wav"%(gapRounded))
                                                elif numero14 == 10:
                                                    
                                                    addSound(dirABSounds + "perseguido por %s segundos_por.wav"%(gapRounded))
                                                elif numero14 == 11:
                                                    addSound("_Se encuentra a %s segundos de su competidor más cercano que es_._.wav"%(gapRounded))
                                                elif numero14 == 12:
                                                    addSound("_tiene un diferencial con el piloto que le sigue de %s segundos que es.wav"%(gapRounded))
                                                elif numero14 == 13:
                                                    addSound("_Mantiene una ventaja de %s segundos sobre el piloto que le sigue en la clasificación que es.wav"%(gapRounded))
                                                elif numero14 == 14:
                                                    addSound("_Ha logrado una diferencia de %s segundos con el piloto que le sigue que es.wav"%(gapRounded))
                                                elif numero14 == 15:
                                                    addSound("_Mantiene una distancia de %s segundos con el piloto que le sigue que es.wav"%(gapRounded))
                                                elif numero14 == 16:
                                                    addSound("_tiene_%s segundos_de ventaja sobre.wav"%(gapRounded))
                                                    
                                                elif numero14 == 17:
                                                    addSound("_se encuentra a %s segundos delante de.wav"%(gapRounded))
                                                elif numero14 == 18:
                                                    addSound("_está a %s segundos por delante de.wav"%(gapRounded))
                                                elif numero14 == 19:
                                                    addSound("_tiene %s segundos sobre.wav"%(gapRounded))
                                                elif numero14 == 20:
                                                    addSound("_tiene %s segundos de ventaja con.wav"%(gapRounded))
                                                elif numero14 == 21:
                                                    addSound("_está a %s segundos de distancia por encima de.wav"%(gapRounded))
                                                elif numero14 == 22:
                                                    addSound("_mantiene _%s segundos_de ventaja sobre.wav"%(gapRounded))
                                                elif numero14 == 23:
                                                    addSound(dirABSounds + "delante de .wav")
                                                elif numero14 == 24:
                                                    addSound(dirABSounds + "sobre .wav")
                                                elif numero14 == 25:
                                                    addSound(dirABSounds + "seguido por .wav")
                                                elif numero14 == 26:
                                                    addSound(dirABSounds + "separado de .wav")
                                                elif numero14 == 27:
                                                    addSound(dirABSounds + "alejado de .wav")
                                                elif numero14 == 28:
                                                    addSound(dirABSounds + "perseguido por .wav")
                                                elif numero14 == 29:
                                                    addSound(dirABSounds + "distanciado de.wav")
                                                elif numero14 == 30:
                                                    addSound(dirABSounds + "en la pugna con .wav")
                                                elif numero14 == 31:
                                                    addSound(dirABSounds + "dejando estela sobre .wav")
                                                elif numero14 == 32:
                                                    addSound(dirABSounds + "A poca distancia de.wav")
                                                elif numero14 == 33:
                                                    addSound(dirABSounds + "A una diferencia mínima con.wav")
                                                elif numero14 == 34:
                                                    addSound(dirABSounds + "A una distancia muy cercana de.wav")
                                                pVoiceTimeedu = clock()
                                            #edu
                                            #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                                            #cuando han pasado 15 segundos sin que se haya dicho nada
                                            



                                else:
                                    #generate a random number between 0 and 4


                                    #EDU SUSSY
                                    #leo el fichero de probabilidad de leer las frases
                                    # Lee el número del archivo externo
                                    Name_File = 'apps\\python\\AnnouncerBot\\probabilidadsusy.txt'
                                    with open(Name_File, 'r')as f:
                                        probabilidad = int(f.read())
                                        print(probabilidad)
                                        ConsoleLog("numero15: POR DETRAS probabilidad %s"%(probabilidad))
                                    # Si la probabilidad es mayor que 0 y menor que 100
                                    # Si la probabilidad es mayor que 0 y menor que 100
                                    if 0 < probabilidad < 101:
                                        # Ejecuta la sentencia if con la probabilidad correspondiente
                                        azarnum = random.uniform(0, 100)
                                        ConsoleLog("numeroazar: %s"%(azarnum))
                                        #if azarnum < probabilidad :
                                        if probabilidad < 101:


                                            #bIsMutedForIntro = True                
                                            #qSpeech.queue.clear()
                                            #dic.clear()                                
                                            #sessionStartTime = clock()
                                                                 



                                            
                                            
                                                numero15 = randInRange(0, 46)
                                                if numero15 == 0:
                                                    addSound(dirABSounds + "_%ssegundos_detrás de.wav"%(gapRounded))
                                                elif numero15 == 1:
                                                    addSound(dirABSounds + "_%ssegundos_tras.wav"%(gapRounded))
                                                elif numero15 == 2:
                                                    addSound(dirABSounds + "_%ssegundos_de distancia tras.wav"%(gapRounded))
                                                elif numero15 == 3:
                                                    addSound(dirABSounds + "_%ssegundos_de diferencia con.wav"%(gapRounded))
                                                elif numero15 == 4:
                                                    addSound(dirABSounds + "_%ssegundos_de separación con.wav"%(gapRounded))
                                                elif numero15 == 5:
                                                    addSound(dirABSounds + "persiguiendo a.wav")
                                                    addSound(dirABSounds + "_%ssegundos_a.wav"%(gapRounded))
                                                elif numero15 == 6:
                                                    addSound(dirABSounds + "buscando recortar los.wav")
                                                    addSound(dirABSounds + "_%ssegundos_de diferencia con.wav"%(gapRounded))
                                                elif numero15 == 7:
                                                    addSound(dirABSounds + "ahora va.wav")
                                                    addSound(dirABSounds + "_%ssegundos_por detrás de.wav"%(gapRounded))
                                                elif numero15 == 8:
                                                    
                                                    addSound(dirABSounds + "precedido por_%ssegundos_de.wav"%(gapRounded))
                                                elif numero15 == 9:
                                                    addSound(dirABSounds + "a solo.wav")
                                                    addSound(dirABSounds + "_%ssegundos_de.wav"%(gapRounded))
                                                elif numero15 == 10:
                                                    addSound(dirABSounds + "distanciado por sólo.wav")
                                                    addSound(dirABSounds + "_%ssegundos_de.wav"%(gapRounded))
                                                elif numero15 == 11:
                                                    addSound(dirABSounds + "%ssegundos_de retraso con.wav"%(gapRounded))
                                                elif numero15 == 12:
                                                    addSound(dirABSounds + "%ssegundos_detrás de.wav"%(gapRounded))
                                                elif numero15 == 13:
                                                    addSound(dirABSounds + "%ssegundos_de distancia detrás de.wav"%(gapRounded))
                                                elif numero15 == 14:
                                                    addSound(dirABSounds + "%ssegundos_más lento que.wav"%(gapRounded))
                                                elif numero15 == 15:
                                                    addSound(dirABSounds + "%ssegundos_de diferencia con.wav"%(gapRounded))
                                                elif numero15 == 16:
                                                    addSound(dirABSounds + "siguiendo a.wav")
                                                    addSound(dirABSounds + "%ssegundos_a.wav"%(gapRounded))
                                                elif numero15 == 17:
                                                    addSound(dirABSounds + "tratando de recortar los.wav")
                                                    addSound(dirABSounds + "%ssegundos_de diferencia con.wav"%(gapRounded))
                                                elif numero15 == 18:
                                                    addSound(dirABSounds + "ahora va.wav")
                                                    addSound(dirABSounds + "%ssegundos_por detrás de.wav"%(gapRounded))
                                                elif numero15 == 19:
                                                    addSound(dirABSounds + "siendo superado por.wav")
                                                    addSound(dirABSounds + ",%ssegundos_de.wav"%(gapRounded))
                                                elif numero15 == 20:
                                                    addSound(dirABSounds + "a sólo.wav")
                                                    addSound(dirABSounds + "%ssegundos_de.wav"%(gapRounded))
                                                elif numero15 == 21:
                                                    addSound(dirABSounds + "a la estela de.wav")
                                                    addSound(dirABSounds + "_%ssegundos_de.wav"%(gapRounded))
                                                elif numero15 == 22:
                                                    addSound(dirABSounds + "detrás de .wav")
                                                elif numero15 == 23:
                                                    addSound(dirABSounds + "tras .wav")
                                                elif numero15 == 24:
                                                    addSound(dirABSounds + "sigue a .wav")
                                                elif numero15 == 25:
                                                    addSound(dirABSounds + "a la estela de .wav")
                                                elif numero15 == 26:
                                                    addSound(dirABSounds + "separado de .wav")
                                                elif numero15 == 27:
                                                    addSound(dirABSounds + "persiguiendo a .wav")                                                
                                                elif numero15 == 28:
                                                    addSound(dirABSounds + "a la caza de .wav")
                                                elif numero15 == 29:
                                                    addSound(dirABSounds + "a la zaga de .wav")
                                                elif numero15 == 30:
                                                    addSound(dirABSounds + "a la estela de .wav")
                                                elif numero15 == 31:
                                                    addSound(dirABSounds + "A poca distancia de.wav")
                                                elif numero15 == 32:
                                                    addSound(dirABSounds + "A una diferencia mínima con.wav")
                                                elif numero15 == 33:
                                                    addSound(dirABSounds + "A una distancia muy cercana de.wav")
                                                elif numero15 == 34:
                                                    addSound(dirABSounds + "En persecución de.wav")
                                                elif numero15 == 35:
                                                    addSound(dirABSounds + "Casi alcanzando a.wav")
                                                elif numero15 == 36:
                                                    addSound(dirABSounds + "Siguiendo de cerca a.wav")
                                                elif numero15 == 37:
                                                    addSound(dirABSounds + "Intentando recortar la distancia con.wav")
                                                elif numero15 == 38:
                                                    addSound(dirABSounds + "en la estela de.wav")
                                                elif numero15 == 39:
                                                    addSound(dirABSounds + "a la zaga de.wav")
                                                elif numero15 == 40:
                                                    addSound(dirABSounds + "a la cola de.wav")
                                                elif numero15 == 41:
                                                    addSound(dirABSounds + "siguiendo con atención a.wav")
                                                elif numero15 == 42:
                                                    addSound(dirABSounds + "tratando de acortar la distancia con.wav")
                                                elif numero15 == 43:
                                                    addSound(dirABSounds + "a cierta distancia prudencial de.wav")
                                                elif numero15 == 44:
                                                    addSound(dirABSounds + "a distancia de.wav")
                                                elif numero15 == 45:
                                                    addSound(dirABSounds + "en búsqueda de.wav")
                                                elif numero15 == 46:
                                                    addSound(dirABSounds + "a la caza de .wav")

                                        addSound(fname)
                                        pVoiceTimeedu = clock()   
                                #edu
                                #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                                #cuando han pasado 15 segundos sin que se haya dicho nada
                                     




                                
                                #don't do this all the time
                                if ac.getCarState(car, acsys.CS.LapCount) > 1 and randInRange(0,4) == 1:
                                    tmpKey = "Lap%dDeltaCar%dCar%d"%(ac.getCarState(car, acsys.CS.LapCount), car, closestCar)
                                    if not tmpKey in dic:
                                        dic[tmpKey] = clock()

                                        focusedCarLastLapTime = ac.getCarState(car, acsys.CS.LastLap)
                                        closestCarLastLapTime = ac.getCarState(closestCar, acsys.CS.LastLap)
                                        
                                        if verbose:
                                            ConsoleLog("Last Lap Difference = %0.4f"%(focusedCarLastLapTime - closestCarLastLapTime))
                                        if focusedCarLastLapTime < closestCarLastLapTime:
                                            fltDelta = (focusedCarLastLapTime - closestCarLastLapTime) / 1000
                                            if fltDelta < -0.5:
                                                strDelta = "%0.1f"%(fltDelta)
                                                strDelta = strDelta.replace("-", "").strip()
                                                #strDelta = "%0.2f"%ac.getCarState(focusedCar, acsys.CS.PerformanceMeter)
                                                #ConsoleLog("FocusedCar %0.4f faster on the last lap"%(focusedCarLastLapTime - closestCarLastLapTime))
                                                #FocusedCar -328.0000 faster on the last lap
                                                ###################addSound(dirABSounds + "..wav")
                                                addSound(dirABSounds + "_ha sido_%s_segundos_mas rápido que en su anterior giro.wav"%(strDelta))
                                                pVoiceTimeedu = clock()
                                        elif closestCarLastLapTime < focusedCarLastLapTime:
                                            fltDelta = (closestCarLastLapTime - focusedCarLastLapTime) / 1000
                                            if fltDelta < -0.5:
                                                strDelta = "%0.1f"%(fltDelta)
                                                strDelta = strDelta.replace("-", "").strip()
                                                #strDelta = "%0.2f"%ac.getCarState(focusedCar, acsys.CS.PerformanceMeter)
                                                #ConsoleLog("FocusedCar %0.4f faster on the last lap"%(focusedCarLastLapTime - closestCarLastLapTime))
                                                #FocusedCar -328.0000 faster on the last lap
                                                #######################################################################################v###################addSound(dirABSounds + "..wav")
                                                addSound(dirABSounds + "%s_ha sido_%ssegundos_mas rápido que en su última vuelta.wav"%(closestAB_driverName, strDelta))
                                                pVoiceTimeedu = clock()
                        else:
                            fGap = dirABSounds + gapRounded + ".wav"
                            
                            if gapRounded != "0.0" and checkSound(fGap):
                                if focusedCarDistance > closestCarDistance:
                                    addSound(fGap)
                                    addSound(dirABSounds + "segundos delante de.wav")
                                else:
                                    addSound(fGap)
                                    #generate a random number between 0 and 4
                                    if randInRange(0,4) == 0:
                                        addSound(dirABSounds + "segundos detrás de.wav")
                                    elif randInRange(0,4) == 1:
                                        addSound(dirABSounds + "segundos tras.wav") 
                                    elif randInRange(0,4) == 2:
                                        addSound(dirABSounds + "segundos por detrás de.wav") 
                                    elif randInRange(0,4) == 3:
                                        addSound(dirABSounds + "segundos de diferencia con.wav") 
                                    else:
                                        addSound(dirABSounds + "segundos de separación con.wav")


                                addSound(fname)                                
                                pVoiceTimeedu = clock()

                            elif closestCarGap < gapBattles:
                                addSound(dirABSounds + "en batalla con.wav")
                                addSound(fname)
                            elif closestCarGap < gapFending:
                                if focusedCarDistance > closestCarDistance:
                                    addSound(dirABSounds + "fending_off.wav")
                                else:
                                    addSound(dirABSounds + "chasing.wav")
                                addSound(fname)
                            elif closestCarGap < gapFollowing:
                                if focusedCarDistance > closestCarDistance:
                                    addSound(dirABSounds + "ahead_of.wav")
                                else:
                                    addSound(dirABSounds + "following.wav")
                                addSound(fname)
                            elif closestCarGap < gapTrailing:
                                if focusedCarDistance > closestCarDistance:
                                    addSound(dirABSounds + "far_in_front_of.wav")
                                else:
                                    addSound(dirABSounds + "trailing.wav")
                                addSound(fname)
                                pVoiceTimeedu = clock()
    
            if (bIsPractice or (bIsQually and AppDic[keysCarPerfMeter[carId]] > 0.0) or report == "FASTEST_LAP") and carDistance < (trackLength - 800.0):
                reportBestLapTime(carId)

            
def reportTyreCompoundAB(car):
    global pVoiceTimeedu




    #check to see if drivers are running another compound?
    AppDic = AppCom.dic




    #edu ruedas: con esto me salto que al principio de la carrera me diga el compuesto de cada uno, me lo quiero saltar porque las frases actuales no me sirven
    # bIsRace = False
    # if AppCom.dic["Session"] == 2:
    #     bIsRace = True
    # if AppDic["Car0LapTime"] == 0.0 and bIsRace:
    #     return










    #typeCompound = AppDic[keysCarTyres[car]]
    bReport = False
    for otherCar in range(0,ac.getCarsCount()):
        if not otherCar == car and AppDic[keysCarConnected[otherCar]] and AppDic[keysCarName[otherCar]] == AppDic[keysCarName[car]]:
            if not AppDic[keysCarTyres[otherCar]] == AppDic[keysCarTyres[car]] and not AppDic[keysCarTyres[otherCar]] == "":
                #ConsoleLog("Tyre Check: {} <> {}".format(AppDic[keysCarTyres[otherCar]], AppDic[keysCarTyres[car]]))
                bReport = True
                break

    if bReport:
        #we need to test this?
        if announceTyreCompounds:
            tmpKey = ac.getCarName(car) + "_" + ac.getCarTyreCompound(car)
            if tmpKey in dicTyres:
                addSound(dirABSounds + dicTyres[tmpKey] + ".wav")
            else:
                if ac.getCarTyreCompound(car) in ["Q"]:
                    addSound(dirABSounds + "con cualis.wav")
                elif ac.getCarTyreCompound(car) in ["C4", "SS"]:
                    
                    
                    
                    #EDU SUSSY
                    #leo el fichero de probabilidad de leer las frases
                    # Lee el número del archivo externo
                    Name_File = 'apps\\python\\AnnouncerBot\\probabilidadsusy.txt'
                    with open(Name_File, 'r')as f:
                        probabilidad = int(f.read())
                        ConsoleLog("numero6: RUEDAS DURAS probabilidad %s"%(probabilidad))
                    # Si la probabilidad es mayor que 0 y menor que 100
                    # Si la probabilidad es mayor que 0 y menor que 100
                    if 0 < probabilidad < 101:
                        # Ejecuta la sentencia if con la probabilidad correspondiente
                        azarnum = random.uniform(0, 100)
                        ConsoleLog("numeroazar: %s"%(azarnum))
                        if azarnum < probabilidad :


                            
                    
                    
                    
                    
                            numero6 = randInRange(0, 18)
                            if numero6 == 0:
                                addSound(dirABSounds + "con duras C4.wav")
                            elif numero6 == 1:
                                addSound(dirABSounds + "con el compuesto más duro.wav")
                            elif numero6 == 2:
                                addSound(dirABSounds + "con las gomas C4.wav")
                            elif numero6 == 3:
                                addSound(dirABSounds + "con las ruedas más duras.wav")
                            elif numero6 == 4:
                                addSound(dirABSounds + "tratando de calentar las C4.wav")
                            elif numero6 == 5:
                                addSound(dirABSounds + "montando las C4.wav")
                            elif numero6 == 6:
                                addSound(dirABSounds + "con c4.wav")
                            elif numero6 == 7:
                                addSound(dirABSounds + "con duras.wav")                
                            elif numero6 == 8:
                                addSound(dirABSounds + "con ruedas duras.wav")
                            elif numero6 == 9:
                                addSound(dirABSounds + "con las gomas más duras.wav")
                            elif numero6 == 10:
                                addSound(dirABSounds + "con ruedas C4.wav")
                            elif numero6 == 11:
                                addSound(dirABSounds + "con las gomas duras.wav")
                            elif numero6 == 12:
                                addSound(dirABSounds + "con el compuesto duro.wav")
                            elif numero6 == 13:
                                addSound(dirABSounds + "con gomas C4.wav")
                            elif numero6 == 14:
                                addSound(dirABSounds + "con neutáticos C4.wav")
                            elif numero6 == 15:
                                addSound(dirABSounds + "montando ruedas C4 en estas vueltas.wav")
                            elif numero6 == 16:
                                addSound(dirABSounds + "usando ruedas duras para un stint largo.wav")
                            elif numero6 == 17:
                                addSound(dirABSounds + "con gomas duras para estas vueltas.wav")                
                            elif numero6 == 18:
                                addSound(dirABSounds + "cambiando a ruedas C4 para mejorar el tiempo.wav")

                        #edu
                        #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                        #cuando han pasado 15 segundos sin que se haya dicho nada
                        

                elif ac.getCarTyreCompound(car) in ["C3", "S"]:



                    #EDU SUSSY
                    #leo el fichero de probabilidad de leer las frases
                    # Lee el número del archivo externo
                    Name_File = 'apps\\python\\AnnouncerBot\\probabilidadsusy.txt'
                    with open(Name_File, 'r')as f:
                        probabilidad = int(f.read())
                        print(probabilidad)
                        ConsoleLog("numero9: GOMAS C3 probabilidad %s"%(probabilidad))
                    # Si la probabilidad es mayor que 0 y menor que 100
                    # Si la probabilidad es mayor que 0 y menor que 100
                    if 0 < probabilidad < 101:
                        # Ejecuta la sentencia if con la probabilidad correspondiente
                        azarnum = random.uniform(0, 100)
                        ConsoleLog("numeroazar: %s"%(azarnum))
                        if azarnum < probabilidad :


                            







                            numero9 = randInRange(0, 19)	
                            if numero9 == 0:
                                addSound(dirABSounds + "con intermedias c3.wav")
                            elif numero9 == 1:
                                addSound(dirABSounds + "con el compuesto intermedio.wav")
                            elif numero9 == 2:
                                addSound(dirABSounds + "con las gomas C3.wav")
                            elif numero9 == 3:
                                addSound(dirABSounds + "con las ruedas intermedias.wav")
                            elif numero9 == 4:
                                addSound(dirABSounds + "con las c3.wav")
                            elif numero9 == 5:
                                addSound(dirABSounds + "montando las C3.wav")
                            elif numero9 == 6:
                                addSound(dirABSounds + "con c3.wav")
                            elif numero9 == 7:
                                addSound(dirABSounds + "con intermedias.wav")                
                            elif numero9 == 8:
                                addSound(dirABSounds + "con ruedas intermedias.wav")
                            elif numero9 == 9:
                                addSound(dirABSounds + "con las gomas intermedias.wav")
                            elif numero9 == 10:
                                addSound(dirABSounds + "en vuelta rápida con las c3.wav")
                            elif numero9 == 11:
                                addSound(dirABSounds + "calentando las gomas C3.wav")
                            elif numero9 == 12:
                                addSound(dirABSounds + "con las ruedas intermedias en buena temperatura.wav")
                            elif numero9 == 13:
                                addSound(dirABSounds + "montando las C3 en estas vueltas.wav")
                            elif numero9 == 14:
                                addSound(dirABSounds + "con las gomas C3 en buena vuelta.wav")
                            elif numero9 == 15:
                                addSound(dirABSounds + "sacando provecho del agarre con las C3.wav")
                            elif numero9 == 16:
                                addSound(dirABSounds + "con ruedas intermedias.wav")
                            elif numero9 == 17:
                                addSound(dirABSounds + "con compuesto intermedio.wav")                
                            elif numero9 == 18:
                                addSound(dirABSounds + "calentando las gomas intermedias en estas vueltas.wav")
                            elif numero9 == 19:
                                addSound(dirABSounds + "con las C3 mejorando el tiempo.wav")


                        #edu
                        #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                        #cuando han pasado 15 segundos sin que se haya dicho nada
                    


                elif ac.getCarTyreCompound(car) in ["C2", "M", "SM"]:


                    #EDU SUSSY
                    #leo el fichero de probabilidad de leer las frases
                    # Lee el número del archivo externo
                    Name_File = 'apps\\python\\AnnouncerBot\\probabilidadsusy.txt'
                    with open(Name_File, 'r')as f:
                        probabilidad = int(f.read())
                        print(probabilidad)
                        ConsoleLog("numero2: GOMAS C2 probabilidad %s"%(probabilidad))
                    # Si la probabilidad es mayor que 0 y menor que 100
                    # Si la probabilidad es mayor que 0 y menor que 100
                    if 0 < probabilidad < 101:
                        # Ejecuta la sentencia if con la probabilidad correspondiente
                        azarnum = random.uniform(0, 100)
                        ConsoleLog("numeroazar: %s"%(azarnum))
                        if azarnum < probabilidad :


                            






                            numero7 = randInRange(0, 22)	
                            if numero7 == 0:
                                addSound(dirABSounds + "con blandas c2.wav")
                            elif numero7 == 1:
                                addSound(dirABSounds + "con el compuesto blando.wav")
                            elif numero7 == 2:
                                addSound(dirABSounds + "con las gomas C2.wav")
                            elif numero7 == 3:
                                addSound(dirABSounds + "con las ruedas blandas.wav")
                            elif numero7 == 4:
                                addSound(dirABSounds + "con las c2 en buena temperatura.wav")
                            elif numero7 == 5:
                                addSound(dirABSounds + "montando las C2.wav")
                            elif numero7 == 6:
                                addSound(dirABSounds + "con c2.wav")
                            elif numero7 == 7:
                                addSound(dirABSounds + "con blandas.wav")                
                            elif numero7 == 8:
                                addSound(dirABSounds + "con ruedas blandas.wav")
                            elif numero7 == 9:
                                addSound(dirABSounds + "con las gomas blandas.wav")
                            elif numero7 == 10:
                                addSound(dirABSounds + "está sintiendo el agarre extra con sus ruedas blandas.wav")
                            elif numero7 == 11:
                                addSound(dirABSounds + "nos reporta que El compuesto blando está ofreciendo un rendimiento óptimo en esta pista.wav")
                            elif numero7 == 12:
                                addSound(dirABSounds + "está reportando que las C2 están en una temperatura ideal para ofrecer el máximo agarre.wav")
                            elif numero7 == 13:
                                addSound(dirABSounds + " está notando el agarre adicional de las C2 en las curvas.wav")
                            elif numero7 == 14:
                                addSound(dirABSounds + "experimentando con el compuesto blando en esta vuelta.wav")
                            elif numero7 == 15:
                                addSound(dirABSounds + "sacando provecho de las ruedas blandas en esta vuelta rápida.wav")
                            elif numero7 == 16:
                                addSound(dirABSounds + "ha decidido montar las gomas más blandas.wav")
                            elif numero7 == 17:
                                addSound(dirABSounds + "con blandas.wav")                
                            elif numero7 == 18:
                                addSound(dirABSounds + "con ruedas blandas.wav")
                            elif numero7 == 19:
                                addSound(dirABSounds + "con las gomas blandas.wav")
                            elif numero7 == 20:
                                addSound(dirABSounds + "está aprovechando el mejor rendimiento de sus ruedas blandas en esta pista.wav")
                            elif numero7 == 21:
                                addSound(dirABSounds + "ha optado por montar el compuesto más blando para esta vuelta rápida.wav")
                            elif numero7 == 22:
                                addSound(dirABSounds + "ha conseguido una temperatura ideal para sus C2 en esta vuelta.wav")



                        #edu
                        #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                        #cuando han pasado 15 segundos sin que se haya dicho nada
                       






                elif ac.getCarTyreCompound(car) in ["C1", "H", "SH"]:
                    
                    #EDU SUSSY
                    #leo el fichero de probabilidad de leer las frases
                    # Lee el número del archivo externo
                    Name_File = 'apps\\python\\AnnouncerBot\\probabilidadsusy.txt'
                    with open(Name_File, 'r')as f:
                        probabilidad = int(f.read())
                        print(probabilidad)
                        ConsoleLog("numero8: GOMAS C1 probabilidad %s"%(probabilidad))
                    # Si la probabilidad es mayor que 0 y menor que 100
                    # Si la probabilidad es mayor que 0 y menor que 100
                    if 0 < probabilidad < 101:
                        # Ejecuta la sentencia if con la probabilidad correspondiente
                        azarnum = random.uniform(0, 100)
                        ConsoleLog("numeroazar: %s"%(azarnum))
                        if azarnum < probabilidad :


                            
                    
                    
                    
                    
                    
                    
                            numero8 = randInRange(0, 19)	
                            if numero8 == 0:
                                addSound(dirABSounds + "con superblandas c1.wav")
                            elif numero8 == 1:
                                addSound(dirABSounds + "con el compuesto superblando.wav")
                            elif numero8 == 2:
                                addSound(dirABSounds + "con las gomas C1.wav")
                            elif numero8 == 3:
                                addSound(dirABSounds + "con las ruedas superblandas.wav")
                            elif numero8 == 4:
                                addSound(dirABSounds + "con las c1 en óptima temperatura.wav")
                            elif numero8 == 5:
                                addSound(dirABSounds + "montando las C1.wav")
                            elif numero8 == 6:
                                addSound(dirABSounds + "con c1.wav")
                            elif numero8 == 7:
                                addSound(dirABSounds + "con superblandas.wav")                
                            elif numero8 == 8:
                                addSound(dirABSounds + "con ruedas superblandas.wav")
                            elif numero8 == 9:
                                addSound(dirABSounds + "con las gomas superblandas.wav")
                            if numero8 == 10:
                                addSound(dirABSounds + "Se está deslizando por la pista con superblandas C1.wav")
                            elif numero8 == 11:
                                addSound(dirABSounds + "Con el compuesto superblando, se está moviendo rápidamente.wav")
                            elif numero8 == 12:
                                addSound(dirABSounds + "obteniendo un excelente agarre con las superblandas c1.wav")
                            elif numero8 == 13:
                                addSound(dirABSounds + "sacando el máximo provecho de las ruedas superblandas c1.wav")
                            elif numero8 == 14:
                                addSound(dirABSounds + "con las gomas C1 en perfecto estado.wav")
                            elif numero8 == 15:
                                addSound(dirABSounds + "utilizando las c1 en esta vuelta rápida.wav")
                            elif numero8 == 16:
                                addSound(dirABSounds + "aprovechando el rendimiento de las c1 en esta curva.wav")
                            elif numero8 == 17:
                                addSound(dirABSounds + "montando las c1 para mejorar sus tiempos.wav")
                            elif numero8 == 18:
                                addSound(dirABSounds + "con las ruedas superblandas c1 en su mejor momento.wav")
                            elif numero8 == 19:
                                addSound(dirABSounds + "optimizando el rendimiento de las gomas superblandas c1.wav")

                        #edu
                        #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                        #cuando han pasado 15 segundos sin que se haya dicho nada
                        




                else:
                    ConsoleLog("Tyre Compound %s not known"%(ac.getCarTyreCompound(car)))
        else:
            if verbose:
                ConsoleLog("Not reporting tyre compounds for %s"%(ac.getCarName(car)))
    else:
        if verbose:
            ConsoleLog("Not reporting, no other tyre compounds in use for %s"%(ac.getCarName(car))) 
        
    
        
def reportP2PActivationsAB(car):
    #P2PStatus (OFF = 0, COOLING = 1,AVAILABLE = 2, ACTIVE = 3)
    p2pStatus = ac.getCarState(car, acsys.CS.P2PStatus)
    p2pLeft = ac.getCarState(car, acsys.CS.P2PActivations)
    tmpKey = "Car%dP2PLeft"%(car)
    if tmpKey in dic:
        if not p2pLeft == dic[tmpKey]:
            dic[tmpKey] = p2pLeft
            addSound(dirABSounds + "%d_p2p_left.wav"%(p2pLeft))
    else:
        dic[tmpKey] = p2pLeft
                   
def gapBetweenCars(car1, car2):

    #closestCarGap
    car1LapCount = ac.getCarState(car1, acsys.CS.LapCount)
    car1CurrPoT = ac.getCarState(car1,acsys.CS.NormalizedSplinePosition)
    car1Distance = (car1LapCount + car1CurrPoT) * trackLength

    car2LapCount = ac.getCarState(car2, acsys.CS.LapCount)
    car2CurrPoT = ac.getCarState(car2,acsys.CS.NormalizedSplinePosition)
    car2Distance = (car2LapCount + car2CurrPoT) * trackLength
    
    carsGap = abs(car1Distance - car2Distance) / (((ac.getCarState(car1,acsys.CS.SpeedKMH) + ac.getCarState(car2,acsys.CS.SpeedKMH)) / 2) / 3.6)
    
    ConsoleLog("Cars Gap = %0.2f"%(carsGap))
    
    return carsGapiniciar_contador
               
#@profile

def acUpdate(deltaT):
    global displayLabel, appWindow, appWindow1, dic, LastStatus, LastSession
    global timer, speechTimer, focusedCar, trackLength, recentLapTime, playedIntro
    global pVoice, delayTimer, sessionStartTime
    global pVoiceTimeedu




    
#############################################################################################

    try:
        #ac.ext_perfBegin("AppCom.checkValues(1)")
        AppCom.checkValues(1)
        #ac.ext_perfEnd("AppCom.checkValues(1)")
        #ConsoleLog("AppCom values checked")
    except:
        pass

#############################################################################################

    try:

        #ConsoleLog("acUpdate")

        timer += deltaT
        
        #ac.ext_perfBegin("AppDic = AppCom.dic")
        AppDic = AppCom.dic
        #ac.ext_perfEnd("AppDic = AppCom.dic")

        if AppDic["SkipProcessing"]:
            #ac.setTitle(appWindow, "Announcer Bot SP")
            #ConsoleLog("SkipProcessing")
            #ac.console("ABot SkipProcessing")
            #ac.console("ABot(%0.4f): SkipProcessing"%(clock()))
            return
        #else:
        #    ac.setTitle(appWindow, "Announcer Bot")
        
        #ac.setText(displayText,"1^10|2^9|3^8|4^7|5^6|6^5|7^4|8^3|9^2|10^1")
        
        #ac.getCarState(0, acsys.CS.LapTime) > raceStartDelay
        #ConsoleLog("AnnouncerBot acUpdate ac.getCarState(0, acsys.CS.LapTime) = %0.4f"%(ac.getCarState(0, acsys.CS.LapTime)))

        #NotAVariable = NotAnotherVariable
        
        #camFOV = 0.0
        #trackCams = 0
        #trackCam = 0
        #driveCam = 0
        #currCam = 0
        
        #camFOV = ac.ext_getCameraFov()
        #trackCams = ac.ext_getTrackCamerasNumber()
        #trackCam = ac.ext_getCurrentTrackCamera()
        #ac.ext_setCurrentTrackCamera(INT)
        #currCam = ac.ext_getCurrentCamera()
        #ac.ext_setCurrentCamera(INT)
        #driveCam = ac.ext_getCurrentDrivableCamera()
        #ac.ext_setCurrentDrivableCamera(INT)
        
        #ConsoleLog("camFOV = %d, CurrCam = %d, TrackCams %d, TrackCam = %d, DriveCam = %d"%(camFOV, currCam, trackCams, trackCam, driveCam))
        
        #ConsoleLog("Number of sessions = %d, reversedGridPositions = %d"%(sim_info_obj.static.numberOfSessions, sim_info_obj.static.reversedGridPositions))
        
        serverName = ac.getServerName()
        serverIP = ac.getServerIP()
        
        #currentTime = sim_info_obj.graphics.iCurrentTime
        #clock is in seconds
        #ConsoleLog("clock = %0.4f"%(clock()))
        
        #acSession = AppDic["Session"]

        
        
        if not LastSession == AppDic["Session"]:
            ConsoleLog("dic.clear LastSession = %d, Session = %d"%(LastSession, AppDic["Session"]))
            LastSession = AppDic["Session"]
            dic.clear()
            sessionStartTime = clock()
            #announce info about the track and the weather?
            
        #be aggressive about getting this value
        if trackLength == 0:
            trackLength = AppDic["TrackSplineLength"]
            if verbose:
                ConsoleLog("Spline Length = %0.6f"%(trackLength))
                    
        if trackLength == 0:
            trackLength = ac.getTrackLength(0)
            if verbose:
                ConsoleLog("Track Length = %0.6f"%(trackLength))

        bIsQually = False
        if AppDic["Session"] == 1:
            bIsQually = True

        bIsPractice = False
        if AppDic["Session"] == 0:
            bIsPractice = True
    
        bIsRace = False
        if AppDic["Session"] == 2:
            bIsRace = True
                        
        totalLaps = AppDic["TotalLaps"]
        maxReportingDistance = 9999999.9
        if trackLength > 0 and totalLaps > 0:
            #do not report info about focus change for some amount of the last lap
            maxReportingDistance = (totalLaps * trackLength) - 800.0
                
        minReportingDistance = 2000.0
        if trackLength > 0:
            minReportingDistance = min(2000.0, trackLength)
                
                
        #if AppDic["IsTimedRace"] and bIsRace:
        #    tmpKey = "totalLaps"
        #    if tmpKey in dic:
        #        totalLaps = dic[tmpKey]
                
        #ConsoleLog("Max Reporting Distance = %0.4f"%(maxReportingDistance))
        #ConsoleLog("Min Reporting Distance = %0.4f"%(minReportingDistance))
        
        timeLeft = AppDic["SessionTimeLeft"]
        
        #ConsoleLog("timeLeft = %0.4f"%(timeLeft))
        #detect when the session restarts?

        timedSession = 0
        if AppDic["IsTimedRace"] and bIsRace:
            timedSession = 1
        if bIsPractice or bIsQually:
            timedSession = 1
        
        try:                
            if timedSession:
                strTimeLeft = formatTime(timeLeft)
                
                if len(strTimeLeft) > 5:
                    strTimeLeft = strTimeLeft[0:5]

                #ConsoleLog("strTimeLeft = %s"%(strTimeLeft))
                totalLaps = AppDic["TotalLaps"]
                #ConsoleLog("Timed Session totalLaps = %d"%(totalLaps))
                    
                tmpKey = "TimeRemaining%s"%(strTimeLeft.split(":")[0])
                if (strTimeLeft.split(":")[0].endswith("0") or strTimeLeft.split(":")[0].endswith("5")) and not tmpKey in dic and not strTimeLeft.split(":")[0] == "00" and strTimeLeft.split(":")[1] == "00":
                    ConsoleLog("Announcing %s left in the session"%(strTimeLeft))
                    dic[tmpKey] = strTimeLeft
                    addSound("%s.wav"%(strTimeLeft.split(":")[0].lstrip("0"))) #
                    addSound("minutos restantes para que termine la sesión.wav")                    
                    
                    
                    #solo si es carrera y quedan 30 minutos para el final , leo el fichero de datos del circuito
                    if bIsRace:
                        if (strTimeLeft.split(":")[0].lstrip("0")) == "30":                            
                            #lee archivo externo datos del circuito eeduu
                            variables = {}
                            Name_File = 'apps\\python\\AnnouncerBot\\01_datoscircuito.txt'
                            with open(Name_File, 'r')as f:
                                for line in f:
                                    name, value = line.split("=")
                                    variables[name] = (value)
                                    leercircuito1 = variables["circuito1"]
                            addSound("ahora, por cortesía de sim tec pro, Vamos con unos datos del circuito._%s.wav"%(leercircuito1))




                if bIsRace:
                    tmpKey = "raceStart"
                    if not tmpKey in dic:
                        lapTime = AppDic["Car0LapTime"]
                        #ConsoleLog("lapTime = %0.4f"%(lapTime))
                        if lapTime > 0.0 and lapTime < 1000.0:
                            if dic["VirtualSafetyCar"] == 0:
                                ConsoleLog("Race Start!")
                                addSound(dirABSounds + "comienza la carrera.wav")
                            else:
                                ConsoleLog("Formation Lap In Progress")
                                addSound(dirABSounds + "formation_lap_in_progress.wav")
                                
                            #add a period
                            ###################addSound(dirABSounds + "..wav")
                            dic[tmpKey] = 1
                            StoreStartingPositions()
                    else:
                        lapTime = AppDic["Car0LapTime"]
                        if lapTime == 0.0:
                            #reset
                            ConsoleLog("dic.clear(); lapTime = %0.4f"%(lapTime))
                            dic.clear()
                            sessionStartTime = clock()
                            return
                            
            elif bIsRace:
                #ConsoleLog("not a timed session 100")
                strTimeLeft = formatTime(timeLeft)
                #ConsoleLog("not a timed session 200")
                if len(strTimeLeft) > 5:
                    #ConsoleLog("not a timed session 300")
                    strTimeLeft = strTimeLeft[0:5]
                
                #ConsoleLog("not a timed session 400")
                #ConsoleLog("strTimeLeft = %s"%(strTimeLeft))
                
                tmpKey = "lastTimeLeft"
                if tmpKey in dic:
                    if dic[tmpKey] == "00:01" and strTimeLeft == "00:00":
                        dic[tmpKey] = strTimeLeft
                        tmpKey = "raceStart"
                        if not tmpKey in dic:
                            if dic["VirtualSafetyCar"] == 0:
                                ConsoleLog("Race Start!")
                                #EDU aqui meto el reloj del semáforo verde
                                current_time = datetime.datetime.now()
                                hour = current_time.hour
                                minute = current_time.minute


                                #bIsMutedForIntro = True                
                                #qSpeech.queue.clear()
                                #dic.clear()                                
                                #sessionStartTime = clock()
                          



                                addSound("El semáforo se abrió a las %s_horas y %s_minutos;.wav"%(hour, minute))
                                ###################addSound(dirABSounds + "..wav")
                                numero = random.randint(1, 10)
                                if numero == 1:
                                    addSound(dirABSounds + "comienza la emoción.wav")
                                elif numero == 2:
                                    addSound(dirABSounds + "la carrera está comenzando.wav")
                                elif numero == 3:
                                    addSound(dirABSounds + "los motores rugen.wav")
                                elif numero == 4:
                                    addSound(dirABSounds + "se apagan las luces.wav")
                                elif numero == 5:
                                    addSound(dirABSounds + "se inicia el gran premio.wav")
                                elif numero == 6:
                                    addSound(dirABSounds + "arranca el gran premio.wav")                                
                                elif numero == 7:
                                    addSound(dirABSounds + "la bandera verde ya está ondeando.wav")                                
                                elif numero == 8:
                                    addSound(dirABSounds + "los motores ya están en marcha.wav")                                
                                elif numero == 9:
                                    addSound(dirABSounds + "la carrera ya ha comenzado.wav")                                
                                elif numero == 10:
                                    addSound(dirABSounds + "los coches ya están en la línea de salida.wav")    
                                #add a period
                                ###################addSound(dirABSounds + "..wav")
                                pVoiceTimeedu = clock()

                                
                                
# ##################################################################################################################################################
                                
#                                 #EDU pruebaPROBAR TEXTO CIRCUITO
#                                 variables = {}
#                                 Name_File = 'apps\\python\\AnnouncerBot\\01_datoscircuito.txt'
#                                 with open(Name_File, 'r')as f:
#                                    for line in f:
#                                        name, value = line.split("=")
#                                        variables[name] = (value)
#                                        leercircuito1 = variables["circuito1"]
#                                    addSound("ahora, por cortesía de sim tec pro, Vamos con unos datos del circuito._%s.wav"%(leercircuito1))   

# ##################################################################################################################################################






 
                            else:
                                ConsoleLog("Formation Lap In Progress")
                                addSound(dirABSounds + "formation_lap_in_progress.wav")
                            #add a period
                            ###################addSound(dirABSounds + "..wav")
                            dic[tmpKey] = 1
                            StoreStartingPositions()
                    elif dic[tmpKey] != strTimeLeft:
                        dic[tmpKey] = strTimeLeft
                else:
                    dic[tmpKey] = strTimeLeft

                tmpKey = "raceStart"
                if tmpKey in dic:                    
                    if timeLeft > 10000.0:
                        ConsoleLog("dic.clear(); timeLeft = %0.4f"%(timeLeft))
                        dic.clear()
                        sessionStartTime = clock()
                        return                        
                
                
                
                #DETECT A RESTART!!!!
                
        except:
            #ConsoleLog("cannot test timeLeft")
            pass
        
        if isVoiceTTS:
            try:
                if not isVoiceSpeaking():
                    playNextSound()
                    AppCom.ABot_Talking = False
                else:
                    AppCom.ABot_Talking = True
            except:
                pass
        else:        
            if speechDuration > 0:
                speechTimer += (deltaT * 1000) #convert to milliseconds
                #ConsoleLog("speechTimer = %d, speechDuration = %d"%(speechTimer, speechDuration))
                if speechTimer > speechDuration:
                    playNextSound()            
            else:
                playNextSound()

        #always play sounds in the queue, but don't play new sounds
        #practice
        if AppDic["Session"] == 0 and not announcePractice:
            return False
            
        #qually
        if AppDic["Session"] == 1 and not announceQually:
            return False
            
        #race
        if AppDic["Session"] == 2 and not announceRace:
            return False
            
        tmpKey = "raceOver"
        if not tmpKey in dic:
            dic[tmpKey] = 0
        
        
        WindKMH = ac.getWindSpeed()
        WindDirection = ac.getWindDirection()
        TrackName = "" # ac.getTrackName(0).replace("ks_", "").replace("nagp_", "") #do these values need to be in the INI?
        if ac.getTrackName(0) in dicTracks:
            TrackName = dicTracks[ac.getTrackName(0)]
        else:
            TrackName = ac.getTrackName(0).replace("ks_", "").replace("acu_", "").replace("nagp_", "").replace("asrl_", "") #do these values need to be in the INI?
            #ConsoleLog("Name from dicTracks = %s"%(TrackName))

        tmpKey = "description"
        if tmpKey in uiDic:
            #what's a reasonable maximum?
            if len(uiDic[tmpKey]) < 200:
                TrackName = uiDic[tmpKey]

        Country = ""
        City = ""
            
        tmpKey = "country"
        if tmpKey in uiDic:
            Country = uiDic[tmpKey]

        tmpKey = "city"
        if tmpKey in uiDic:
            City = uiDic[tmpKey]
            
        #ConsoleLog("Description = %s"%(uiDic["description"]))
        #ConsoleLog("Country = %s"%(uiDic["country"]))
        #ConsoleLog("City = %s"%(uiDic["city"]))
        #ConsoleLog("Length = %s"%(uiDic["length"]))
        #ConsoleLog("Width = %s"%(uiDic["width"]))
        #ConsoleLog("PitBoxes = %s"%(uiDic["pitboxes"]))
        #ConsoleLog("Run = %s"%(uiDic["run"]))
                    
        WindDirs = ["norte","nor noreste","noreste","este noroeste","este","este sureste","sureste","sur sureste","sur","sur suroeste","suroeste","oeste suroeste","oeste","oeste noroeste","noroeste","nor noroeste","norte"]
        WindIdx = round(WindDirection / 22.5, 0)
        WindName = "north"
        try:
            WindName = WindDirs[int(WindIdx)]
        except:
            pass
     
        #ConsoleLog("acUpdate")
     
        #skip this for now?
        if True: #announce the turn names all the time?
            #ConsoleLog("100")
            if ac.getCarsCount() == 1:
                #only do this once per second?
                ReadTrackInfo()
                #ConsoleLog("200")
                namedLocation = ""
                sectionName = ""
                currPoT = ac.getCarState(0,acsys.CS.NormalizedSplinePosition)
                #ConsoleLog("looping sections")
                #ac.ext_perfBegin("Looping Section")
                for section in trackSections:
                    try:
                        if currPoT > uiDic["%s_IN"%(section)] and currPoT < uiDic["%s_OUT"%(section)]:
                            #namedLocation = uiDic["%s_TEXT"%(section)]
                            sectionName = "%s_TEXT"%(section)
                            if len(uiDic[sectionName]) == 1:
                                #ConsoleLog("Only 1 NickName")
                                namedLocation = uiDic[sectionName][0]
                            elif len(uiDic[sectionName]) > 1:
                                #ConsoleLog("More Than 1 NickName")
                                namedLocation = uiDic[sectionName][randInRange(0, len(uiDic[sectionName])) - 1]
                            
                            #if verbose == 1:
                            #    ConsoleLog("focusCar in %s"%(namedLocation))
                    except:
                        pass

                #ac.ext_perfEnd("Looping Section")
                
                #ConsoleLog("300")
                tmpKey = "LastReportedLocation"
                if not namedLocation == "":
                    #ConsoleLog("400")
                    if tmpKey in dic:
                        #ConsoleLog("500")
                        if not sectionName == dic[tmpKey]:
                            #ConsoleLog("600")
                            dic[tmpKey] = sectionName
                            addSound("%s%s.wav"%(dirABSounds, namedLocation))
                    else:
                        #ConsoleLog("700")
                        dic[tmpKey] = sectionName                                
                        addSound("%s%s.wav"%(dirABSounds, namedLocation))
        
        
        if clock() -  sessionStartTime < sessionDelay:
            #wait X seconds before considering anything else in the session
            focusedCar = 0
            return 1
        
        
        #due to AC bug we can't announce this info for a practice session, or it will sometimes duplicate
        if (bIsRace or bIsQually) and extraSessionInfo:

            tmpKey = "trackName"
            if not tmpKey in dic:
                ConsoleLog("Announcing Track Name")
                dic[tmpKey] = TrackName
                #not announcing the practice session is handled above, but we'll leave this here for future testing (if need be)
                if bIsRace:
                    addSound("la carrera se celebra en.wav")

                elif bIsPractice:
                    addSound("the_practice_session_is_at.wav")
                elif bIsQually:
                    addSound("comienza la sesión de cualy en el circuito de.wav")
                else:
                    addSound("the_unknown_session_is_at.wav")
                
                addSound("%s.wav"%(TrackName))

                if not Country == "" and not City == "":
                    addSound("en.wav")
                    addSound("%s.wav"%(City))
                    #addSound(",.wav")
                    addSound("%s.wav"%(Country))
                elif not Country == "":
                    addSound("en.wav")
                    addSound("%s.wav"%(Country))
                elif not City == "":
                    addSound("en.wav")
                    addSound("%s.wav"%(City))
                #EDU METO TEXTO SOBRE EL CIRCUITO
                #addSound("El Circuito pol armañác es un autódromo situado en Nogaro, en la región de Mediodía-Pirineos francesa._. Fue abierto en 1960 como el primer circuito permanente construido en Francia, con un trazado de POCO MÁS DE KILÓMETRO Y MEDIO de longitud. La pista fue alargada a más de 3 kilómetros en 1972, y a los más de 3600 metros actuales en 1989. YA En 2007, el circuito se modernizó incluyendo una nueva torre de control, un nuevo pitLEIN y la ampliación del ANCHO DE la pista a 12 metros,. . Además de albergar campeonatos franceses de automovilismo y motociclismo ,   LA PISTA ha recibido a categorías como la F4, F2, GT3 y Moto GP.  a lo largo de su historia, El circuito no es uno de los más conocidos en el mundo, pero al ser de la vieja escuela, posee curvas trepidantes que los mejores pilotos deberán dominar..wav")
                #add a period
                ###################addSound(dirABSounds + "..wav")
                tmpKey = "windName"
                LastWindName = WindName
                if tmpKey in dic:
                    LastWindName = dic[tmpKey]
                if WindKMH > 0.0 and (not LastWindName == WindName or not tmpKey in dic):
                    dic[tmpKey] = WindName
                    addSound("el viento sopla a una velocidad de.wav")
                    addSound("%d_kilómetros hora.wav"%(WindKMH))
                    addSound("con dirección.wav")
                    addSound("%s.wav"%(WindName))
                    #add a period
                    ###################addSound(dirABSounds + "..wav")

        
        #if False:
        #    ConsoleLog("TrackName = %s")
        #    ConsoleLog("WindKMH = %0.1f"%(WindKMH))
        #    ConsoleLog("WindDirection = %0.1f"%(WindDirection))
        #    addSound("the_race_is_at.wav")
        #    addSound("%s.wav"%(TrackName))
        #    WindDirs = ["north","north_north_east","north_east","east_north_east","east","east_south_east","south_east","south_south_east","south","south_south_west","south_west","west_south_west","west","west_north_west","north_west","north_north_west","north"]
        #    WindIdx = round(WindDirection / 22.5, 0)
        #    ConsoleLog("WindIdx = %d"%(WindIdx))
        #    #addSound("the_wind_is_%d_K M H_")
        #    addSound("the_wind_speed_is.wav")
        #    addSound("%d_K_M_H.wav"%(WindKMH))
        #    addSound("from_the.wav")
        #    try:
        #        addSound("%s.wav"%(WindDirs[int(WindIdx)]))
        #    except:
        #        pass

        #setPositions()
                
        #ConsoleLog("Back From setPositions")
        
        #tmpRaceOver = 0
        maxLaps = 0

        if not "VirtualSafetyCar" in dic:
            dic["VirtualSafetyCar"] = 0

        #ConsoleLog("acUpdate 1000")
        #we only need to monitor this if there's a 2nd race?
        #this should catch when a race session is restarted after it's finished and before it cycles to the next qually, or if there are only race sessions
        if dic["raceOver"] and AppDic["Car0LapTime"] == 0.0: # and not sim_info_obj.static.reversedGridPositions == 0:
            #extra time check in addition to tmpRaceOver to try and prevent a false positive
            ConsoleLog("Race Session Reset, Clearing dic")
            with qSpeech.mutex:
                ConsoleLog("clearing the qSpeech")
                qSpeech.queue.clear()
            dic.clear()
            sessionStartTime = clock()
            return 1
        
        #ac.ext_perfBegin("focusedCarCheck")
        if not focusedCar == ac.getFocusedCar():
            focusedCar = ac.getFocusedCar()
            strCarId = str(focusedCar)
            carId = focusedCar
            
            if "LastReportedLocation" in dic:
                del dic["LastReportedLocation"]
            if "namedLocationLastReported" in dic:
                del dic["namedLocationLastReported"]
            if "TrackingFocusCarPositionChange" in dic:
                del dic["TrackingFocusCarPositionChange"]
            
            
            #ConsoleLog("Focus set to %s"%(safeName(focusedCar)))

            savePositions()

            #store the current position
            #tmpKey = "FocusCarPosition"
            #dic[tmpKey] = int(getPosition(focusedCar))
            #ConsoleLog("dic[%s] = %d"%(tmpKey, dic[tmpKey]))

            closestCarDistance = 99999999.0
            closestCar = -1
            closestCarGap = 9999.0

            position = AppDic[keysCarPosition[carId]]
            #tmpKey = "Position{0}Car".format(position - 1)
            #keyCarDistanceGapAhead = keysCarDistanceGapAhead[carId] # "".join(["Car", strCarId, "DistanceGapAhead"])
            #keyCarDistanceGapBehind = keysCarDistanceGapBehind[carId] #  "".join(["Car", strCarId, "DistanceGapBehind"])
            if keysCarDistanceGapAhead[carId] in AppDic and position > 0:
                if AppDic[keysCarDistanceGapAhead[carId]] < closestCarDistance:
                    closestCarDistance = AppDic[keysCarDistanceGapAhead[carId]]
                    closestCar = AppDic[keysPositionCar[position - 1]]
                    closestCarGap = AppDic[keysCarTimeGapAhead[carId]]
            #tmpKey = "Position{0}Car".format(position + 1)
            if keysCarDistanceGapBehind[carId] in AppDic:
                if AppDic[keysCarDistanceGapBehind[carId]] < closestCarDistance:
                    try:
                        closestCarDistance = AppDic[keysCarDistanceGapBehind[carId]]
                        closestCar = AppDic[keysPositionCar[position + 1]]
                        closestCarGap = AppDic[keysCarTimeGapBehind[carId]]
                    except:
                        pass
                
                
            #ConsoleLog("Closest Car = %d, Driver Name %s, Distance = %0.6f, Gap = %0.4f"%(closestCar, getABotDriverName(closestCar), closestCarDistance, closestCarGap))                            
            
            #if focuscar is within 800 meters of the finish line do not report their information
            #if focusedCar is approaching the checkered flag then no need to report
            #raceOver
            if not AppDic["RaceOver"]:
                if AppDic[keysCarDistance[carId]] * trackLength < maxReportingDistance:
                    #ConsoleLog("reportDriverNameAndPosition 100")
                    reportDriverNameAndPosition(focusedCar, closestCar, closestCarGap)
            elif trackLength > 0:
                carCurrPoT = AppDic[keysCarPoT[carId]] # ac.getCarState(focusedCar,acsys.CS.NormalizedSplinePosition)
                carDistance = carCurrPoT * trackLength
                #if the car is within 800 meters of the finish line
                #finished
                if carDistance < (trackLength - 800.0) or AppDic[keysCarRaceFinished[carId]]:
                    reportDriverNameAndPosition(focusedCar, closestCar, closestCarGap)
            else:
                reportDriverNameAndPosition(focusedCar, closestCar, closestCarGap)
                
            #else:
            #    ConsoleLog("Current distance %d > %d"%(focusedCarDistance, maxReportingDistance))
        else:
            #THIS IS FIRING TOO OFTEN, MAYBE SAVE POSITIONS IS BROKEN?
            #filter out times we don't want to track this
            bReport = True #"RaceStart"
            if (maxReportingDistance > 0 and AppDic[keysCarDistance[focusedCar]] * trackLength > maxReportingDistance) or (minReportingDistance > 0 and AppDic[keysCarDistance[focusedCar]] * trackLength < minReportingDistance):
                bReport = False
                
            #strFocusedCar = str(focusedCar)
            if bIsRace and AppDic["Car0LapTime"] > 0.1 and not AppDic[keysCarRaceFinished[focusedCar]] and not AppDic[keysCarInPits[focusedCar]] and bReport: #and maxLaps > 0 
                #keyCarPosition = "".join(["Car", str(focusedCar), "InPits"])
                carPosition = AppDic[keysCarPosition[focusedCar]]
                #ConsoleLog("Looking to see if the focusCar changed positions")
                savedPosition = getSavedPosition(focusedCar)
                if not carPosition == savedPosition: # getPosition(focusedCar) == getSavedPosition(focusedCar):
                    tmpKey = "TrackingFocusCarPositionChange"
                    if not tmpKey in dic:
                        dic[tmpKey] = clock()
                        #ConsoleLog("%s was P-%d, is now in P-%d at %0.4f"%(safeName(focusedCar), getSavedPosition(focusedCar) + 1, AppDic["Car{}Position".format(focusedCar)] + 1, dic[tmpKey]))
                    else:
                        if clock() -  dic[tmpKey] > positionChangeDelay:
                            #announce the new position
                            #addSound("%s_is_now_p-%d.wav"%(getABotDriverName(focusedCar), getPosition(focusedCar) + 1))
                            keyNum = str(carPosition + 1)
                            bChangeReported = False






                            # #EDU LIMITO LAS VECES QUE CANTA CUANDO UN PILOTO PIERDE POSICIÓN, YA QUE SI PIERDE VARIOS PUESTOS, ES ABURRIDO ESCUCHAR TANTAS VECES QUE PIERDE POSICION


                            # # #manage moving up the grid vs down the grid
                            # if carPosition > savedPosition: #moved DOWN the grid
                            #     keyNum = str(carPosition)
                            #     #who passed them?
                            #     otherCarId = AppDic[keysPositionCar[carPosition - 1]]
                            #     #ConsoleLog("getSavedPosition(otherCarId) = {}, carPosition = {}".format(getSavedPosition(otherCarId), carPosition))
                            #     if getSavedPosition(otherCarId) == carPosition:
                            #         bChangeReported = True
                            #         otherDriver = getABotDriverName(otherCarId) # AppDic[keysCarSafeName[otherCarId]] #AppDic positions zero based
                            #         if randInRange(0, 1) == 0 or not keyNum in dicNumbers:
                            #             addSound("_ha perdido la posición%d_en favor de_%s.wav"%(carPosition, otherDriver))
                            #         else:
                            #             #ConsoleLog("Speaking from dicNumbers 400")
                            #             addSound("%s_ha perdido el puesto_%s_y se lo ha arrebatado_%s_.wav"%(getABotDriverName(focusedCar), dicNumbers[keyNum], otherDriver))
                            # elif carPosition < savedPosition: #moved UP the grid
                            #     keyNum = str(carPosition + 1)


                            positions_lost = 0
                            limit = 2
                            if carPosition > savedPosition: #moved DOWN the grid
                                positions_lost += (carPosition - savedPosition)
                                if positions_lost <= limit:
                                    keyNum = str(carPosition)
                                    #who passed them?
                                    otherCarId = AppDic[keysPositionCar[carPosition - 1]]
                                    #ConsoleLog("getSavedPosition(otherCarId) = {}, carPosition = {}".format(getSavedPosition(otherCarId), carPosition))
                                    if getSavedPosition(otherCarId) == carPosition:
                                        threading.Thread(target=playsound, args=("apps\\python\\AnnouncerBot\\adelantamiento.wav",)).start()
                                        bChangeReported = True
                                        otherDriver = getABotDriverName(otherCarId)
                                        if randInRange(0, 1) == 0 or not keyNum in dicNumbers:
                                            addSound("_ha perdido la posición%d_en favor de_%s.wav"%(carPosition, otherDriver))
                                            pVoiceTimeedu = clock()
                                        else:
                                            #ConsoleLog("Speaking from dicNumbers 400")
                                            addSound("%s_ha perdido el puesto_%s_y se lo ha arrebatado_%s_.wav"%(getABotDriverName(focusedCar), dicNumbers[keyNum], otherDriver))
                                            pVoiceTimeedu = clock()
                                else:
                                    positions_lost = 0
                            elif carPosition < savedPosition: #moved UP the grid
                                positions_lost = 0
                                keyNum = str(carPosition + 1)
    




                                
                                otherCarId = AppDic[keysPositionCar[carPosition + 1]]
                                #ConsoleLog("getSavedPosition(otherCarId) = {}, carPosition = {}".format(getSavedPosition(otherCarId), carPosition))
                                if getSavedPosition(otherCarId) == carPosition:
                                    bChangeReported = True
                                
                                    otherDriver = getABotDriverName(otherCarId) # AppDic[keysCarSafeName[otherCarId]] #AppDic positions zero based
                                    #if randInRange(0, 1) == 0 or not keyNum in dicNumbers:
                                    #    addSound("%s_ha adelantado a_%s_y ahora es_%d_.wav"%(getABotDriverName(focusedCar), otherDriver, carPosition + 1))
                                    #else:
                                    #    #ConsoleLog("Speaking from dicNumbers 400")
                                    #    addSound("%s_ha pasado a_%s_y_es_%s_.wav"%(getABotDriverName(focusedCar), otherDriver, dicNumbers[keyNum]))
                                    
                                    
                                    currentFocusedCarID = ac.getFocusedCar()
                                    ## edu ers con un decimal # ers_value = round(ac.getCarState(currentFocusedCarID, acsys.CS.KersCharge) * 100, 1)
                                    #ers_value = int(round(ac.getCarState(currentFocusedCarID, acsys.CS.KersCharge) * 100, 1))
                                    #addSound("%s_ha adelantado a_%s_y ahora es_%d_. tiene un e-erre-ese restante de %.1f%%_,_.wav"%(getABotDriverName(focusedCar), otherDriver, carPosition + 1, ers_value))
                                    


                                #EDU SUSSY
                                #leo el fichero de probabilidad de leer las frases
                                # Lee el número del archivo externo
                                Name_File = 'apps\\python\\AnnouncerBot\\probabilidadsusy.txt'
                                with open(Name_File, 'r')as f:
                                    probabilidad = int(f.read())
                                    print(probabilidad)
                                    ConsoleLog("numero13: ADELANTAMIENTO probabilidad %s"%(probabilidad))
                                # Si la probabilidad es mayor que 0 y menor que 100
                                # Si la probabilidad es mayor que 0 y menor que 100
                                if 0 < probabilidad < 101:
                                    # Ejecuta la sentencia if con la probabilidad correspondiente
                                    azarnum = random.uniform(0, 100)
                                    ConsoleLog("numeroazar: %s"%(azarnum))
                                    #if azarnum < probabilidad :
                                    if probabilidad < 101:


                                        



                                        numero13 = randInRange(0, 30)
                                        ConsoleLog("HAY ADELANTAMIENTO")
                                        threading.Thread(target=playsound, args=("apps\\python\\AnnouncerBot\\adelantamiento.wav",)).start()



                                        # # Cargar el archivo de audio
                                        # sound = pygame.mixer.Sound(filenameadelantamiento)
                                        
                                        # # Reproducir el archivo de audio
                                        # sound.play()
                                        
                                        # pygame.mixer.Sound.play(sound)

                                        # # Esperar a que el archivo de audio termine de reproducirse
                                        # #while pygame.mixer.get_busy():
                                        # #    pygame.time.wait(100)

                                        # # Terminar Pygame
                                        # #pygame.mixer.quit()






                                        otherDriver = getABotDriverName(otherCarId)
                                        
                                        #addSound("apps\\python\\AnnouncerBot\\adelantamiento.wav")
                                        
                                        #bIsMutedForIntro = True                
                                        #qSpeech.queue.clear()
                                        #dic.clear()                                
                                        #sessionStartTime = clock()
                                    
                                    

                                        
                                        
                                        if numero13 == 0:
                                            addSound("_ha adelantado a_%s_y ahora es_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 1:
                                            addSound("_ha pasado a_%s_y_es_%s_.wav"%(otherDriver, dicNumbers[keyNum]))
                                        elif numero13 == 2:
                                            addSound("_supera a_%s_y ya está en posición_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 3:
                                            addSound("_tras adelantar a_%s_se pone_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 4:
                                            addSound("_con su adelantamiento a_%s_se pone _%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 5:
                                            addSound("_gana la posición superando a_%s_y es_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 6:
                                            addSound("_le ha ganado la plaza a_%s_y se coloca_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 7:
                                            addSound("_mejora una plaza rebasando a_%s_y queda en p_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 8:
                                            addSound("_adelanta a_%s_y es_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 9:
                                            addSound("_pasó a_%s_y ahora ocupa la posición_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 10:
                                            addSound("_superó a_%s_y se situó en la posición_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 11:
                                            addSound("_acaba de adelantar a_%s_y se encuentra en la posición_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 12:
                                            addSound("_acaba de ganar una posición tras adelantar a_%s_y se encuentra en la posición_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 13:
                                            addSound("_acaba de adelantar a_%s_y se ha puesto en la posición_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 14:
                                            addSound("_se ha colocado en la posición_%d_tras adelantar a_%s_.wav"%(carPosition + 1, otherDriver))
                                        elif numero13 == 15:
                                            addSound("_acaba de superar a_%s_y se ha colocado en la posición_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 16:
                                            addSound("_se ha puesto en la posición_%d_tras adelantar a_%s_.wav"%(carPosition + 1, otherDriver))
                                        elif numero13 == 17:
                                            addSound("_acaba de ganar una posición tras adelantar a_%s_y ahora se encuentra en la posición_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 18:
                                            addSound("_se ha colocado en la posición_%d_después de adelantar a_%s_.wav"%(carPosition + 1, otherDriver))
                                        elif numero13 == 19:
                                            addSound("_acaba de adelantar a_%s_y se ha situado en la posición_%d_.wav"%(otherDriver, carPosition + 1))
                                        #variantes ojo
                                        elif numero13 == 20:
                                            addSound("¡Mira cómo  ha pasado a %s y ahora está en la posición %d!"%(otherDriver, carPosition + 1))
                                        elif numero13 == 21:
                                            addSound("¿Cómo ha conseguido %s adelantar a %s y colocarse en la posición %d?"%(otherDriver, carPosition + 1))
                                        elif numero13 == 22:
                                            addSound(" tras adelantar a %s, se ha puesto en la posición %d."%(otherDriver, carPosition + 1))
                                        elif numero13 == 23:
                                            addSound(" ha superado a %s y ya está en la posición %d."%(otherDriver, carPosition + 1))
                                        elif numero13 == 24:
                                            addSound(" ha pasado a %s y ahora es el piloto número %d."%(otherDriver, carPosition + 1))
                                        elif numero13 == 25:
                                            addSound(" ha adelantado a %s y ahora es el piloto número %d."%(otherDriver, carPosition + 1))
                                        elif numero13 == 26:
                                            addSound("ahora es %d tras adelantar a %s"%(otherDriver, carPosition + 1))
                                        #####
                                        elif numero13 == 27:
                                            addSound("_se ha colocado en la posición_%d_tras superar a_%s_.wav"%(carPosition + 1, otherDriver))
                                        elif numero13 == 28:
                                            addSound("_ha pasado a_%s_y ahora se encuentra en la posición_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 29:
                                            addSound("_ha adelantado a_%s_con una maniobra impresionante y ahora se encuentra en la posición_%d_.wav"%(otherDriver, carPosition + 1))
                                        elif numero13 == 30:
                                            addSound("_ha superado a_%s_y ahora se encuentra en la posición_%d_.wav"%(otherDriver, carPosition + 1))
                                        pVoiceTimeedu = clock()
                                    #edu
                                    #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                                    #cuando han pasado 15 segundos sin que se haya dicho nada




                                ###################addSound(dirABSounds + "..wav")


                            if not bChangeReported: #this is a more complex changing of the driver order, probably some other car off pace or in the pits
                                if randInRange(0, 1) == 0 or not keyNum in dicNumbers:
                                    e=1
                                    ########################################################addSound("_ahora mismo en posición %d.wav"%(carPosition + 1))
                                else:
                                    e=1
                                    #ConsoleLog("Speaking from dicNumbers 400")
                                    ########################################################addSound("_ahora es p%s_.wav"%(dicNumbers[keyNum]))
                            
                            savePositions()
                            del dic[tmpKey]
                            #focusCar needs to continue being in the new position for some length of time?
                            #announce the gap to the closest car?
                else:
                    tmpKey = "TrackingFocusCarPositionChange"
                    if tmpKey in dic:
                        if verbose:
                            ConsoleLog("Clearing TrackingFocusCarPositionChange")
                        del dic[tmpKey]
            else:
                tmpKey = "TrackingFocusCarPositionChange"
                if tmpKey in dic:
                    ConsoleLog("Clearing TrackingFocusCarPositionChange")
                    del dic[tmpKey]

            
        #ac.ext_perfEnd("focusedCarCheck")    
            

        #ConsoleLog("acUpdate 2000")
        
        #ac.ext_perfBegin("Looping All Cars")
        
        #second pass to report on conditions
        #ConsoleLog("looping cars to report on conditions")
        strFocusedCar = str(focusedCar)
        for car in range(0,ac.getCarsCount()):
            strCarId = str(car)
            carId = car
            #keyCarDriverName = "".join(["Car", strCarId, "DriverName"])
            driverName =  AppDic[keysCarDriverName[carId]]
            if AppDic[keysCarConnected[carId]] and not driverName in skipDrivers:
                
                keyCarPosition = keysCarPosition[carId] # "".join(["Car", strCarId, "Position"])
                #ConsoleLog("acUpdate 2010")
                position = AppDic[keyCarPosition] # getPosition(car)
                
                #keyCarSpeedKMH = "".join(["Car", strCarId, "SpeedKMH"])
                #keyCarLapCount = "".join(["Car", strCarId, "LapCount"])
                #keyCarPoT = "".join(["Car", strCarId, "PoT"])
                #keyCarLapTime = "".join(["Car", strCarId, "LapTime"])
                #keyCarDistance = "".join(["Car", strCarId, "Distance"])
                #keyCarInPits = "".join(["Car", strCarId, "InPits"])
                
                #ConsoleLog("acUpdate 2040")
                #driverName = AppDic[keyCarDriverName] # getABotDriverName(car)
                speedKMH = AppDic[keysCarSpeedKMH[carId]] #ac.getCarState(car,acsys.CS.SpeedKMH)
                ab_driverName = getABotDriverName(carId) # driverName #.replace("  ", "_").replace(" ", "_") #moved to the addSound routine
                #lapTimes for other cars are not available
                #lapTime = AppDic["".join(["Car", strCarId, "LapTime"])] # ac.getCarState(car, acsys.CS.LapTime)
                lapCount = AppDic[keysCarLapCount[carId]] # ac.getCarState(car, acsys.CS.LapCount)
                currPoT = AppDic[keysCarPoT[carId]] # ac.getCarState(car,acsys.CS.NormalizedSplinePosition)
                inPits = AppDic[keysCarInPits[carId]]
                distance = AppDic[keysCarDistance[carId]] * trackLength
                
                #ConsoleLog("lapTime for car %d is %0.4f"%(car, lapTime))
        
                #IS THIS LOGIC TOO EXPENSIVE? TRACER
                #OFF PACE MESSAGES.  Move this to the AppCom?
                if False: # dic["raceOver"] == 0:
                    kmhAvg = 0.0
                    #stop processing off pace messages once the race is over
                    keyPoTKMH = "KMH%0.3f"%(currPoT)
                    if keyPoTKMH in dicKMH:
                        kmhAvg = dicKMH[keyPoTKMH]
                        if kmhAvg < 1:
                            ConsoleLog("kmhAvg for PoT %0.3f = %0.1f"%(currPoT, kmhAvg))

                    #ConsoleLog("acUpdate 2100")
                    if not car == focusedCar and not bIsQually:
                        tmpKey = "Car%dOffPaceReported"%(car)
                        bReportOffPace = True
                        if not tmpKey in dic:
                            dic[tmpKey] = 0
                        else:
                            if time.clock() - dic[tmpKey] < repetitionDelay:
                                bReportOffPace = False
                        if (speedKMH < (kmhAvg * 0.2)) and bReportOffPace:
                            #ConsoleLog("Car %d Off Pace"%(car))
                            fname = dirABSounds + ab_driverName + ".wav"
                            if checkSound(fname) and (lapCount > 0 or AppDic["Car0LapTime"] > raceStartDelay) and not dic[tmpKey] and not inPits and qSpeech.qsize() < qSkipOffPace:
                                focusedCarCurrPoT = AppDic[keysCarPoT[focusedCar]] # ac.getCarState(focusedCar,acsys.CS.NormalizedSplinePosition)              
                                focusedCarDistance = AppDic[keysCarDistance[focusCar]] * trackLength # focusedCarCurrPoT * trackLength
                                otherCarDistance = distance #AppDic[keyCarDistance] # currPoT * trackLength

                                #report any car ahead within 300? meters that's off pace
                                if abs(otherCarDistance - focusedCarDistance) < 300.0 and currPoT > focusedCarCurrPoT:
                                    if verbose:
                                        ConsoleLog("Reporting Car %d Off Pace"%(car))
                                    dic[tmpKey] = time.clock()
                                    #we only care if it's ahead? skip announcing this on the first lap?
                                    addSound(fname)
                                    addSound(dirABSounds + "ahead.wav")
                                    addSound(dirABSounds + "is_off_pace.wav")                
                                    #add a period
                                    ###################addSound(dirABSounds + "..wav")
                        #elif dic[tmpKey] and (speedKMH > (kmhAvg * 0.7)):
                        #    #they have to be going at least 70% of pace to clear the message
                        #    if verbose:
                        #        ConsoleLog("Clearing Car %d Off Pace"%(car))
                        #    dic[tmpKey] = 0
                
                
                #ConsoleLog("acUpdate 2200")
                #What do we only report during a Qually session?
                #Report end of qually session?  Timer = 0?
                if bIsQually:
                    #skip this for now
                    #tmpKey = "startQually"
                    #if not tmpKey in dic:
                    #    dic[tmpKey] = 1
                    #    if True: #skip announcing that for now?
                    #        addSound(dirABSounds + "the_qualifying_session_is_now_underway.wav")
                    #    #add a period
                    #    ###################addSound(dirABSounds + "..wav")
                    #    if playedIntro == 0 and playIntro:
                    #        #only play the intro once
                    #        playedIntro = 1
                    #        if True: # serverIP in reportedIPs: #always play the intro?
                    #            #don't actually "play the intro" for non NAGP servers
                    #            ShiftCtrlI() #Hotkey for Playing Intro
                    #            ShiftCtrlM() #Hotkey for Muting Desktop Audio

                    tmpKey = "EndQually"
                    if timeLeft <= 0.0 and not tmpKey in dic:
                        ConsoleLog("la sesion de cualy acaba de terminar")
                        addSound(dirABSounds + "la sesión de cualy ha terminado. última oportunidad para los pilotos que aún estén en pista.wav")
                        pVoiceTimeedu = clock()
                        #add a period
                        ###################addSound(dirABSounds + "..wav")                        
                        dic[tmpKey] = 1

                    #how do we know the qually session is over?  this doesn't work  :(
                    #tmpKey = "endQually"
                    #if timeLeft <= 0.0 and not tmpKey in dic:
                    #    ConsoleLog("Qually session is Over")
                    #    addSound(dirABSounds + "the_qualifying_session_is_now_over.wav")
                    #    #add a period
                    #    ###################addSound(dirABSounds + "..wav")                        
                    #    dic[tmpKey] = 1
                        
                    #ConsoleLog("Is Qually")
                    #only report provisional pole after 3 laps?
                    #this value is for the current lap, not the last lap
                    lapInvalid = ac.getCarState(car,acsys.CS.LapInvalidated)
                    lastLapInvalid = 0
                    
                    tmpKey = "Car%dLap%dInvalid"%(car, lapCount)
                    if tmpKey in dic:
                        if not dic[tmpKey]:
                            dic[tmpKey] = lapInvalid
                    else:
                        dic[tmpKey] = lapInvalid
                        
                    tmpKey = "Car%dLap%dInvalid"%(car, lapCount - 1)
                    if tmpKey in dic:
                        lastLapInvalid = dic[tmpKey]
                    
                    #if the track is A2B then log and track all the best times to the various named locations on track, so we can report on the up/down for each driver
                    
                    perfMeter = AppDic[keysCarPerfMeter[focusedCar]] # ac.getCarState(focusedCar, acsys.CS.PerformanceMeter)
                    if car == focusedCar and not lapInvalid and perfMeter < -0.01 and perfMeter > - 29.0 and not AppDic[keysCarInPits[focusedCar]]:
                        #track the perf delta at various sections?
                        #ConsoleLog("tracking current section")
                        namedLocation = ""
                        sectionName = ""
                        #ConsoleLog("looping sections")
                        for section in trackSections:
                            try:
                                if currPoT > uiDic["%s_IN"%(section)] and currPoT < uiDic["%s_OUT"%(section)]:
                                    #namedLocation = uiDic["%s_TEXT"%(section)]
                                    sectionName = "%s_TEXT"%(section)
                                    
                                    if len(uiDic[sectionName]) == 1:
                                        #ConsoleLog("Only 1 NickName")
                                        namedLocation = uiDic[sectionName][0]
                                    elif len(uiDic[sectionName]) > 1:
                                        #ConsoleLog("More Than 1 NickName")
                                        namedLocation = uiDic[sectionName][randInRange(0, len(uiDic[sectionName])) - 1]
                                    
                                    if verbose:
                                        ConsoleLog("Qually focusCar in %s"%(namedLocation))
                            except:
                                pass


                        if trackLength > 0.0:
                            #carCurrPoT = AppDic[keysCarPoT[carId]] #  "".join(["Car", strCarId, "PoT"])]
                            #ConsoleLog("200")
                            carDistance = AppDic[keysCarPoT[carId]] * trackLength
                            #ConsoleLog("300")
                            #ac.console("currPoT = %0.3f, carDistance = %0.1f, trackLength = %0.1f"%(carCurrPoT, carDistance, trackLength))
                            #no need to announce being up at the very beginning or the very end of a lap
                            if carDistance > 600.0 and carDistance < (trackLength - 400.0):
                                #ConsoleLog("400")
                                #don't actually report this when they are close to S/F
                                #addSound("%sup_%s.wav"%(dirABSounds, strDelta))
                                tmpKey = "LastReportedLocation"
                                if not namedLocation == "":
                                    if tmpKey in dic:
                                        if not sectionName == dic[tmpKey]:
                                            dic[tmpKey] = sectionName
                                            bReport = True
                                            tmpKey = "namedLocationLastReported"
                                            if tmpKey in dic:
                                                if clock() -  dic[tmpKey] < perfMeterDelay:
                                                    bReport = False
                                            #perfMeterDelay
                                            #reportLocationAndPerfDelta(driverName, namedLocation, "%0.2f"%ac.getCarState(focusedCar, acsys.CS.PerformanceMeter))
                                            if bReport: # randInRange(0, 2) == 0:
                                                dic["namedLocationLastReported"] = clock()
                                                strDelta = "%0.2f"%perfMeter
                                                strDelta = strDelta.replace("-", "").strip()
                                                #edu numero5
                                                numero5 = randInRange(0, 30)
                                                if numero5 == 0:
                                                    addSound("%s%s_está en vuelta y va mejorando su tiempo delta en_%s_ segundos_pasando_por_la_curva de_%s.wav"%(dirABSounds, ab_driverName, strDelta, namedLocation))
                                                elif numero5 == 1:
                                                    addSound("%s%s_está mejorando su tiempo en_%s_ segundos_pasando_por_la_curva de_%s.wav"%(dirABSounds, ab_driverName, strDelta, namedLocation))
                                                elif numero5 == 2:
                                                    addSound("%s%s_está haciendo su mejor tiempo, y mejora en_%s_ segundos_pasando_por_la_curva de_%s.wav"%(dirABSounds, ab_driverName, strDelta, namedLocation))
                                                elif numero5 == 3:
                                                    addSound("%s%s_en vuelta rápida va mejorando su tiempo delta en_%s_ segundos_pasando_por_la_curva de_%s.wav"%(dirABSounds, ab_driverName, strDelta, namedLocation))
                                                elif numero5 == 4:
                                                    addSound("%s%s_marcando en morado sus tiempos y mejorando en_%s_ segundos_pasando_por_la_curva de_%s.wav"%(dirABSounds, ab_driverName, strDelta, namedLocation))
                                                elif numero5 == 5:
                                                    addSound("%s%s_rodando muy rápido, mejorando su tiempo en_%s_ segundos_pasando_por_la_curva de_%s.wav"%(dirABSounds, ab_driverName, strDelta, namedLocation))                
                                                elif numero5 == 6:
                                                    addSound("%s%s_va en vuelta lanzada, pintando de morado su tiempo por_%s_ segundos_pasando_por_la_curva de_%s.wav"%(dirABSounds, ab_driverName, strDelta, namedLocation))
                                                elif numero5 == 7:
                                                    addSound("%s%s_mejora su tiempo más rápido por_%s_ segundos_pasando_por_la_curva de_%s.wav"%(dirABSounds, ab_driverName, strDelta, namedLocation))
                                                elif numero5 == 8:
                                                    addSound("%s%s_en vuelta lanzada bajando sus tiempos en_%s_ segundos_pasando_por_la_curva de_%s.wav"%(dirABSounds, ab_driverName, strDelta, namedLocation))
                                                elif numero5 == 9:
                                                    addSound("%s%s_haciendo su mejor vuelta de clasi, bajando el tiempo en_%s_ segundos_pasando_por_la_curva de_%s.wav"%(dirABSounds, ab_driverName, strDelta, namedLocation))
                                                elif numero5 == 10:
                                                    addSound("%s%s_va en una vuelta rápida y mejora su tiempo en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 11:
                                                    addSound("%s%s_aumenta su velocidad y reduce su tiempo en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 12:
                                                    addSound("%s%s_corre a toda velocidad y reduce su tiempo en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 13:
                                                    addSound("%s%s_sale disparado en la vuelta y mejora su tiempo en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 14:
                                                    addSound("%s%s_sigue aumentando su velocidad y reduce su tiempo en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 15:
                                                    addSound("%s%s_acelera y mejora su tiempo en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 16:
                                                    addSound("%s%s_se mueve como un rayo y reduce su tiempo en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 17:
                                                    addSound("%s%s_aumenta la velocidad y mejora su tiempo en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 18:
                                                    addSound("%s%s_se desliza por la pista a toda velocidad y reduce su tiempo en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 19:
                                                    addSound("%s%s_se lanza en la vuelta y mejora su tiempo en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 20:
                                                    addSound("%s%s_está en una vuelta rápida y va mejorando su tiempo delta en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 21:
                                                    addSound("%s%s_va en una vuelta rápida y mejora su tiempo en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 22:
                                                    addSound("%s%s_está haciendo su mejor tiempo, y mejora en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 23:
                                                    addSound("%s%s_se desliza por la pista en vuelta rápida, mejorando su tiempo delta en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 24:
                                                    addSound("%s%s_marcando en morado sus tiempos y mejorando en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 25:
                                                    addSound("%s%s_rodando muy rápido, mejorando su tiempo en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 26:
                                                    addSound("%s%s_va en vuelta lanzada, pintando de morado su tiempo por_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 27:
                                                    addSound("%s%s_mejora su tiempo más rápido por_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 28:
                                                    addSound("%s%s_en vuelta lanzada bajando sus tiempos en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 29:
                                                    addSound("%s%s_haciendo su mejor vuelta de clasi, bajando el tiempo en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                elif numero5 == 30:
                                                    addSound("%s%s_en una vuelta rápida mejorando su tiempo en_%s_ segundos.wav"%(dirABSounds, ab_driverName, strDelta))
                                                pVoiceTimeedu = clock()



                                            #edu
                                            #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                                            #cuando han pasado 15 segundos sin que se haya dicho nada
                                           


                                    else:
                                        dic[tmpKey] = sectionName
                                elif tmpKey in dic:
                                    dic[tmpKey] = ""
                        
                    
                    #dirABSounds
                    fname = dirABSounds + ab_driverName + ".wav"
                    #ConsoleLog("Is Qually - 100")
                    #first check to see if lastLap information changed
                    bestLapTime = AppDic[keysCarBestLap[carId]] # ac.getCarState(car, acsys.CS.LastLap)
                    lapTime = AppDic["Car0LapTime"] # ac.getCarState(car, acsys.CS.LapTime)
                    
                    tmpKey = "Car%dLapTime"%(car)
                    if bestLapTime > 0 and not lastLapInvalid:
                        #ConsoleLog("Is Qually - 110")
                        if tmpKey in dic:
                            if bestLapTime < dic[tmpKey]:
                                #ConsoleLog("Fastest Lap")
                                tmpFast = "FastestLap"
                                bReported = False
                                if tmpFast in dic:
                                    if bestLapTime < dic[tmpFast]:
                                        dic[tmpFast] = bestLapTime
                                        if True: #lapCount > 0: #always report this?
                                            dic[tmpKey] = bestLapTime
                                            ConsoleLog("Reporting provisional pole")
                                            if checkSound(fname):
                                                bReported = True
                                                #addSound(fname)
                                                pole=0
                                                pole = random.randint(1, 10)

                                                if pole == 1:
                                                    addSound("¡Qué vuelta! ¡%s se lleva la pole position!" % fname)
                                                elif pole == 2:
                                                    addSound("%s logra la pole provisional, ¿podrá mantenerla hasta el final?" % fname)
                                                elif pole == 3:
                                                    addSound("¡Impresionante vuelta de %s, se coloca en la pole!" % fname)
                                                elif pole == 4:
                                                    addSound("%s se coloca en la pole position, pero la lucha por la primera posición promete ser dura" % fname)
                                                elif pole == 5:
                                                    addSound("¡Espectacular vuelta de %s, se lleva la pole position por muy poco!" % fname)
                                                elif pole == 6:
                                                    addSound("%s marca el tiempo más rápido en la sesión de clasificación y se lleva la pole" % fname)
                                                elif pole == 7:
                                                    addSound("¡Inmejorable vuelta de %s, se asegura la pole position provisional!" % fname)
                                                elif pole == 8:
                                                    addSound("%s se hace con la pole position en el último suspiro de la sesión de clasificación" % fname)
                                                elif pole == 9:
                                                    addSound("¡Qué emoción! %s se lleva la pole position por apenas unas décimas" % fname)
                                                elif pole == 10:
                                                    addSound("%s logra la pole position con una vuelta perfecta, ¿podrá repetirla en la carrera?" % fname)

                                                addSound(dirABSounds + "con_un_tiempo_de_%s.wav"%(formatLapTime3Digits(bestLapTime).replace(":", "_")))
                                                pVoiceTimeedu = clock()
                                                #break the time into smaller numbers 1 23 point 4 5 6
                                                #add a period
                                                ###################addSound(dirABSounds + "..wav")

                                else:
                                    dic[tmpFast] = bestLapTime
                                
                                if car == focusedCar and bReported == False:
                                    #Driver Name - improved thier LapTime - is in PNumber
                                    #ConsoleLog("May report better lap time")
                                    if delayTimer == 0.0:
                                        delayTimer = time.clock()
                                        
                                    if time.clock() - delayTimer > sortDelay: # lapTime > 100: #what's the delay before we get an updated sort order?
                                        delayTimer = 0.0
                                        if verbose:
                                            ConsoleLog("100 recording fastest lapTime for %d"%(car))
                                        dic[tmpKey] = bestLapTime
                                        if checkSound(fname):
                                            addSound(fname)
                                            addSound(dirABSounds + "ha mejorado su tiempo._.wav")
                                            
                                            position = AppDic[keysCarPosition[carId]] # getPosition(car)
                                            
                                            #ConsoleLog("Position 200")
                                            if verbose:
                                                ConsoleLog("200 - Driver %s is in position %d"%(safeName(car), position + 1))
                                            #addSound("%sis_p-%d.wav"%(dirABSounds, position + 1))
                                            keyNum = str(position + 1)
                                            if randInRange(0, 1) == 0 or not keyNum in dicNumbers:
                                                addSound("%sahora mismo en p%d.wav"%(dirABSounds, position + 1))
                                            else:
                                                #ConsoleLog("Speaking from dicNumbers 500")
                                                addSound("%sestá_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))
                                            
                                            addSound("%scon_%s.wav"%(dirABSounds, formatLapTime3Digits(bestLapTime).replace(":", "_")))
                                            #add a period
                                            ###################addSound(dirABSounds + "..wav")
                                            reportGapToFastest(car)
                                    #else:
                                    #    ConsoleLog("200 not reporting yet, current laptime = %d"%(lapTime))
                                elif not car == focusedCar:
                                    #ConsoleLog("300 recording fastest lapTime for %d"%(car))
                                    dic[tmpKey] = bestLapTime
                        else:
                            #ConsoleLog("400 recording fastest lapTime for %d"%(car))
                            dic[tmpKey] = bestLapTime
                    
                    #is provisional pole
                    #improved thier LapTime - is PNumber
                    #is up in sector one
                    #is up in sector two
                    #is up in sector three
                    #on personal best
                    #against the leader - how to track and report this?
                    #ConsoleLog("Is Qually - 200")
                    #then check the splits
                    
                    #can't use splits, have to use PoT 0.333 and 0.666 instead
                    #TTS is reporting when drivers are up in named locations
                    if not isVoiceTTS:
                        if currPoT < 0.1:
                            #clear both sector times
                            tmpKey = tmpKey = "Car%dSplit1"%(car)
                            dic[tmpKey] = 0
                            tmpKey = tmpKey = "Car%dSplit2"%(car)
                            dic[tmpKey] = 0                      

                        #need to do the PoT comparison in reverse order
                        elif currPoT > 0.666:
                            tmpKey = "Car%dSplit2"%(car)
                            if tmpKey in dic:
                                if dic[tmpKey] == 0:
                                    #ConsoleLog("Checking Split 2")
                                    dic[tmpKey] = lapTime
                                    tmpKey = "Car%dBestSplit2"%(car)
                                    if tmpKey in dic:
                                        if lapTime < dic[tmpKey]:
                                            bReported = False
                                            dic[tmpKey] = lapTime
                                            tmpKey = "BestSplit2"
                                            if tmpKey in dic:
                                                if lapTime < dic[tmpKey]:
                                                    dic[tmpKey] = lapTime
                                                    if lapCount > 2:
                                                        if checkSound(fname):
                                                            bReported = True                                                    
                                                            addSound(fname)
                                                            addSound(dirABSounds + "is_up_in_sector_2.wav")
                                                            addSound(dirABSounds + "against_the_leader.wav")                                                
                                                            #add a period
                                                            ###################addSound(dirABSounds + "..wav")
                                            else:
                                                dic[tmpKey] = lapTime
                                            if checkSound(fname) and bReported == False and focusedCar == car:
                                                addSound(fname)
                                                addSound(dirABSounds + "is_up_in_sector_2.wav")
                                                addSound(dirABSounds + "on_personal_best.wav")
                                                #add a period
                                                ###################addSound(dirABSounds + "..wav")
                                    else:
                                        dic[tmpKey] = lapTime
                            
                        elif currPoT > 0.333:
                            tmpKey = "Car%dSplit1"%(car)
                            if tmpKey in dic:
                                if dic[tmpKey] == 0:
                                    #ConsoleLog("Checking Split 1")
                                    dic[tmpKey] = lapTime
                                    tmpKey = "Car%dBestSplit1"%(car)
                                    if tmpKey in dic:
                                        if lapTime < dic[tmpKey]:
                                            bReported = False
                                            dic[tmpKey] = lapTime
                                            tmpKey = "BestSplit1"
                                            if tmpKey in dic:
                                                if lapTime < dic[tmpKey]:
                                                    dic[tmpKey] = lapTime
                                                    if lapCount > 2:
                                                        if checkSound(fname):
                                                            bReported = True                                                    
                                                            addSound(fname)
                                                            addSound(dirABSounds + "is_up_in_sector_1.wav")
                                                            addSound(dirABSounds + "against_the_leader.wav")                                                
                                                            #add a period
                                                            ###################addSound(dirABSounds + "..wav")
                                            else:
                                                dic[tmpKey] = lapTime
                                            if checkSound(fname) and bReported == False and focusedCar == car:
                                                addSound(fname)
                                                addSound(dirABSounds + "is_up_in_sector_1.wav")
                                                addSound(dirABSounds + "on_personal_best.wav")
                                                #add a period
                                                ###################addSound(dirABSounds + "..wav")
                                    else:
                                        dic[tmpKey] = lapTime
                        
                        
                        
                    if False:
                        splits = ac.getLastSplits(car)
                        splitCount = len(splits)
                        for x in range(0, splitCount):
                            tmpKey = "Car%dSplit%d"%(car, x)
                            #ConsoleLog("Is Qually - 210")
                            split_time = splits[x]
                            #ConsoleLog("Is Qually - 220")
                            if split_time > 0 and x < splitCount:
                                #ConsoleLog("Is Qually - 230")
                                #only care about the first two sectors, third sector time should compare fastLap
                                if tmpKey in dic:
                                    if split_time < dic[tmpKey]:
                                        dic[tmpKey] = split_time
                                        bReported = False
                                        #Driver Name - is up in sector NUMBER - on previous best
                                        if car == focusedCar:
                                            #ConsoleLog("Driver is better in this sector")
                                            if checkSound(fname):
                                                addSound(fname)
                                                addSound(dirABSounds + "is_up_in_sector_%d.wav"%(x + 1))
                                                addSound(dirABSounds + "on_personal_best.wav")
                                                #add a period
                                                ###################addSound(dirABSounds + "..wav")
                                else:
                                    #ConsoleLog("Is Qually - 300")
                                    dic[tmpKey] = split_time
                
                #ConsoleLog("acUpdate 2500")
                #has the race ended?
                if bIsRace and AppDic["RaceOver"]:
                    position = AppDic[keysCarPosition[carId]] # getPosition(car)
                    
                    #is race finished?  if so, report positions
                    carRaceOver = AppDic[keysCarRaceFinished[carId]] # ac.getCarState(car, acsys.CS.RaceFinished)
                    tmpKey = "raceOver"
                    if not dic[tmpKey] and carRaceOver:
                        dic[tmpKey] = carRaceOver
                        #the leader has just finished the race
                        #addSound(dirABSounds + "El líder está pasando por meta en este momento. Una Carrera patrocinada por sim tec pro.wav")

                        numero12 = randInRange(0, 16)	
                        if numero12 == 0:
                            addSound(dirABSounds + "El líder está pasando por meta en este momento..wav")
                        elif numero12 == 1:
                            addSound(dirABSounds + "Y el vencedor de esta apasionante carrera ve la bandera a cuadros..wav")
                        elif numero12 == 2:
                            addSound(dirABSounds + "Esto ha sido todo, Finaliza la carrera tras el paso por meta del líder..wav")
                        elif numero12 == 3:
                            addSound(dirABSounds + "Y el ganador de hoy pasa en este instante por línea de meta..wav")
                        elif numero12 == 4:
                            addSound(dirABSounds + "Victoria merecida sin duda para nuestro ganador de hoy, que en este momento ve la bandera de cuadros..wav")
                        elif numero12 == 5:
                            addSound(dirABSounds + "El líder está viendo en este momento la bandera de cuadros, una gran victoria, muy merecida, sin duda alguna..wav")
                        elif numero12 == 6:
                            addSound(dirABSounds + "En este momento el líder termina su carrera con su último paso por meta. Enhorabuena. una merecida victoria..wav")
                        elif numero12 == 7:
                            addSound(dirABSounds + "El líder de la carrera está pasando por meta en este momento..wav")
                        elif numero12 == 8:
                            addSound(dirABSounds + "El vencedor de la carrera está viendo la bandera a cuadros en este momento..wav")
                        elif numero12 == 9:
                            addSound(dirABSounds + "La carrera ha finalizado tras el paso por meta del líder..wav")
                        elif numero12 == 10:
                            addSound(dirABSounds + "El ganador de hoy está pasando en este instante por línea de meta..wav")
                        elif numero12 == 11:
                            addSound(dirABSounds + "El ganador de hoy está viendo la bandera de cuadros en este momento, una victoria bien merecida..wav")
                        elif numero12 == 12:
                            addSound(dirABSounds + "El líder está pasando por meta en este momento, una gran victoria..wav")
                        elif numero12 == 13:
                            addSound(dirABSounds + "El líder ha finalizado su carrera con su último paso por meta. Enhorabuena por la victoria..wav")
                        elif numero12 == 14:
                            addSound(dirABSounds + "El ganador de la carrera ha pasado por meta en este momento..wav")
                        elif numero12 == 15:
                            addSound(dirABSounds + "El líder de la carrera está viendo la bandera a cuadros en este momento..wav")
                        elif numero12 == 16:
                            addSound(dirABSounds + "La carrera ha finalizado tras el paso por meta del líder, quien se convierte en el ganador..wav")
                        #add a period
                        ###################addSound(dirABSounds + "..wav")
                        addSound(dirABSounds + "Una Carrera patrocinada por sim tec pro..wav")
                        pVoiceTimeedu = clock()
                    #edu
                    #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                    #cuando han pasado 15 segundos sin que se haya dicho nada
            


                    tmpKey = "Car%dRaceFinished"%(car)
                    if not tmpKey in dic:
                        dic[tmpKey] = 0
                    if carRaceOver and not dic[tmpKey] == carRaceOver:
                        dic[tmpKey] = carRaceOver
                        if True: #verbose:
                            ConsoleLog("carrera terminada en posición %d para %s"%(position, ac.getDriverName(car)))
                        #when closestCar is unknown then send a -1
                        reportDriverNameAndPosition(car, -1, -1)
                
                #inPits = AppDic["".join(["Car", str(car), "InPits"])] #ac.isCarInPitlane(car) or ac.isCarInPitlane(car)                
                lapsSincePit = 0
                try:
                    lapsSincePit =  AppDic[keysCarLapCount[carId]] - AppDic[keysCarPitLap[carId]]
                except:
                    pass
                
                #ConsoleLog("acUpdate 2700")
                #ABot has to track being in pits separately to make announcements about it





                #EDU AQUÍ VOY A COMPROBAR SI YA HAY ALGÚN COCHE EN PITS, SI HAY COCHE NO QUIERO QUE CANTE MÁS VOZ
                #problema, lo hace una vez
                tmpKey = "Car%dInPits"%(car)
                if tmpKey in dic and bIsRace:


                    # #si quiero borrarlo es desde aquí##############################################################

                    # inPitsCount = 0
                    # for value in dic.values():
                    #     if value == 2 or value == 3:
                    #         inPitsCount += 1
                    #         #ConsoleLog("c1oches en pits = {} ".format(inPitsCount))

                    # if inPitsCount >= 3:
                    #     # Ya hay dos coches en los pits, no ejecutar el resto del código
                    #     #ConsoleLog("coches en pits = {} ".format(inPitsCount))
                    #     inPitsCount = 0
                    #     continue
                    

                    # #hasta aqui   ##############################################################################     


                    


                    #y si no quiero que cante nada, símplemente activo el continue de abajo
                    #continue        #EDU IMPORTANTE: SÓLO CON PONER ESTA LÍNEA , YA SE SALTA LOS PITS los boxes. SALTAR PITS


                    #inPits can be 1 or 2 for the car being in pit lane or the pit stall
                    if not inPits == dic[tmpKey] and not AppDic["RaceOver"]:
                        valueWas = dic[tmpKey]
                        dic[tmpKey] = inPits
                        #already populated
                        #driverName = getABotDriverName(car)
                        #ab_driverName = driverName.replace(" ", "_")
                        
                        if verbose:
                            ConsoleLog("inPits = {} for {}".format(inPits, ab_driverName))
                        
                        #dirABSounds
                        fname = dirABSounds + ab_driverName + ".wav"
                        if qSpeech.qsize() < qSkipLength:
                            if checkSound(fname):
                                #ConsoleLog("saying %s"%(ab_driverName))
                                bReport = True
                                tmpKey = "Car%dInPitsReported"%(car)
                                #ConsoleLog("time.clock() = {}".format(time.clock()))
                                if tmpKey in dic:
                                    if time.clock() - dic[tmpKey] < pitsRepetitionDelay:
                                        bReport = False
                                        #ConsoleLog("bReport = False")
                                
                                if bReport:
                                    if inPits and valueWas == 0:
                                        
                                        if bReport and speedKMH < 82.0:
                                            dic[tmpKey] = time.clock()
                                            if verbose:
                                                ConsoleLog("{} entering the pits".format(ab_driverName))
                                            
                                            
                                            #edu SYSSY EL COCHE ESTÁ PARANDO EN BOXES
                                            #SOLO CANTAR CUANDO NO HAYA NADIE EN BOXES, SI HAY OTROS COCHES, NO CANTAR
                                            
                                            
                                            addSound(fname)





###############################################################################################################


                                            ##EDU BOX,BOX,BOX CON ESTO DIBUJO LA VENTANA
                                            #ac.addRenderCallback(appWindow1, appGLBOX)
                                            ##message = "PILOTO ENTRANDO EN BOXES: " + fname
                                            #label = Label(appWindow1).setText("BOX, BOX, BOX , Piloto : " + ab_driverName)
                                            #Label(appWindow1).setPosition(10,100)
                                            #Label(appWindow1).setFont("Formula")
                                            #Label(appWindow1).setFontSize(30)
                                            
                                            ##ac.addLabel(appWindow1, "PILOTO ENTRANDO EN BOXES: ", 100, 100, 20, (255, 0, 0))
                                            #ConsoleLog("DIBUJO VENTANA DE BOXES")


###############################################################################################################




                                            #generate a random number between 1 and 3#
                                            if lapCount < 5:
                                                #addSound(dirABSounds + "ha entrado en boxes, es demasiado pronto, probablemente tenga el coche dañado_,.wav")
                                                # Generamos un número aleatorio entre 1 y 10
                                                numero1 = random.randint(1, 17)


                                                #bIsMutedForIntro = True                
                                                #qSpeech.queue.clear()
                                                #dic.clear()                                
                                                #sessionStartTime = clock()
                                            


                                                #threading.Thread(target=playsound, args=("apps\\python\\AnnouncerBot\\boxboxbox.wav",)).start()
                                                threading.Thread(target=lambda: playsound("apps\\python\\AnnouncerBot\\boxboxbox.wav")).start()
                                                
                                                # Dependiendo del número generado, seleccionamos una frase
                                                if numero1 == 1:
                                                    addSound(dirABSounds + "ha entrado en boxes, es demasiado pronto, probáblemente tenga el coche dañado_,.wav")
                                                elif numero1 == 2:
                                                    addSound(dirABSounds + "ha entrado en boxes muy temprano, esto puede indicar un problema en su coche_,.wav")
                                                elif numero1 == 3:
                                                    addSound(dirABSounds + "entrando en boxes muy temprano, es posible que tenga daños en su coche_,.wav")
                                                elif numero1 == 4:
                                                    addSound(dirABSounds + "ha entrado en boxes muy temprano en la carrera, es posible que tenga problemas en su coche_,.wav")
                                                elif numero1 == 5:
                                                    addSound(dirABSounds + "ha entrado en boxes después de unas pocas vueltas, es posible que tenga daños en su coche_,.wav")
                                                elif numero1 == 6:
                                                    addSound(dirABSounds + "ha entrado en boxes muy temprano, esto puede ser una señal de problemas en su coche_,.wav")
                                                elif numero1 == 7:
                                                    addSound(dirABSounds + "ha entrado en boxes muy temprano, es posible que tenga daños en su coche_,.wav")
                                                elif numero1 == 8:
                                                    addSound(dirABSounds + "ha entrado en boxes muy pronto, es posible que haya tenido un accidente_,.wav")
                                                elif numero1 == 9:
                                                    addSound(dirABSounds + "ha entrado en boxes a pocas vuelta de comenzar la carrera, es posible que tenga daños en su coche_,.wav")
                                                elif numero1 == 10:
                                                    addSound(dirABSounds + "ha entrado en boxes muy temprano en la carrera, es posible que tenga problemas en su coche_,.wav")
                                                elif numero1 == 11:
                                                    addSound(dirABSounds + "Entrando en boxes cuando llevamos muy pocas vueltas, puede que tenga daños en su coche_,.wav")
                                                elif numero1 == 12:
                                                    addSound(dirABSounds + "hace una Parada en boxes prematura, puede ser que tenga problemas en su coche_,.wav")
                                                elif numero1 == 13:
                                                    addSound(dirABSounds + "entra en Pit stop muy temprano, puede que tenga daños en su coche_,.wav")
                                                elif numero1 == 14:
                                                    addSound(dirABSounds + "hace una Entrada en boxes antes de tiempo, puede ser un indicio de daños en su coche_,.wav")
                                                elif numero1 == 15:
                                                    addSound(dirABSounds + "haciendo Parada en boxes muy temprana, puede ser un signo de problemas en su coche_,.wav")
                                                elif numero1 == 16:
                                                    addSound(dirABSounds + "haciendo un Pit stop en las primeras vueltas, puede ser un indicio de daños en su coche_,.wav")
                                                elif numero1 == 17:
                                                    addSound(dirABSounds + "está Parando en boxes en las primeras vueltas, puede ser un signo de problemas en su coche_,.wav")                                            
                                                #edu quiero dibujar un mensaje en pantalla que diga quien está en boxes
                                                threading.Thread(target=lambda: playsound("apps\\python\\AnnouncerBot\\boxboxbox.wav")).start()
                                                #edu
                                                #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                                                #cuando han pasado 15 segundos sin que se haya dicho nada
                                                pVoiceTimeedu = clock()
                                                    
                                                    




                                            else:
                                                numero1 = random.randint(1, 8)
                                                #if numero1 is 1 then say "is entering the pits"
                                                if numero1 == 1:
                                                    addSound(dirABSounds + "entrando en pits.wav")
                                                    pVoiceTimeedu = clock()
                                                    ####################addSound(dirABSounds + "..wav")
                                                    
                                                    #addSound(fname)
                                                #if numero1 is 2 then say "is in the pits"
                                                if numero1 == 2:
                                                    addSound(dirABSounds + "haciendo su parada obligatoria.wav")
                                                    pVoiceTimeedu = clock()
                                                    ####################addSound(dirABSounds + "..wav")
                                                    
                                                    #addSound(fname)
                                                #if numero1 is 3 then say "is in the pits"
                                                if numero1 == 3:
                                                    addSound(dirABSounds + "_en_boxes.wav")
                                                    pVoiceTimeedu = clock()
                                                    ####################addSound(dirABSounds + "..wav")
                                                    
                                                    #addSound(fname)

                                                #if numero1 is 3 then say "is in the pits"
                                                if numero1 == 4:
                                                    addSound(dirABSounds + "_pasando por pits.wav")
                                                    pVoiceTimeedu = clock()
                                                    ####################addSound(dirABSounds + "..wav")
                                                    
                                                    #addSound(fname)

                                                #if numero1 is 3 then say "is in the pits"
                                                if numero1 == 5:
                                                    addSound(dirABSounds + "_haciendo trabajar a los mecánicos.wav")
                                                    pVoiceTimeedu = clock()
                                                    ####################addSound(dirABSounds + "..wav")
                                                    
                                                    #addSound(fname)

                                                #if numero1 is 3 then say "is in the pits"
                                                if numero1 == 6:
                                                    addSound(dirABSounds + "_visitando_boxes.wav")
                                                    pVoiceTimeedu = clock()
                                                    ####################addSound(dirABSounds + "..wav")
                                                    
                                                    #addSound(fname)

                                                #if numero1 is 3 then say "is in the pits"
                                                if numero1 == 7:
                                                    addSound(dirABSounds + "_circulando por pits.wav")
                                                    pVoiceTimeedu = clock()
                                                    ###################addSound(dirABSounds + "..wav")
                                                    
                                                    #addSound(fname)

                                                #if numero1 is 3 then say "is in the pits"
                                                if numero1 == 8:
                                                    addSound(dirABSounds + "_transita por pits.wav")
                                                    pVoiceTimeedu = clock()
                                                    ####################addSound(dirABSounds + "..wav")
                                                    
                                                    #addSound(fname)


                                            #edu
                                            #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                                            #cuando han pasado 15 segundos sin que se haya dicho nada
                                          





                                            if lapsSincePit > 0:
                                                fname = dirABSounds + "después de_%d_vueltas.wav"%(lapsSincePit + 1)
                                                pVoiceTimeedu = clock()
                                                if checkSound(fname):            
                                                    addSound(fname)
                                                    reportTyreCompoundAB(car)
                                                    #if ac.getCarTyreCompound(car) == "A":
                                                    #    addSound(dirABSounds + "on_alternates.wav")
                                                    #elif ac.getCarTyreCompound(car) == "P":
                                                    #    addSound(dirABSounds + "on_primaries.wav")
                                                        
                                            #tack on the drivers current position
                                            #ConsoleLog("Position 300")
                                            if verbose:
                                                ConsoleLog("300 - Driver %s is in position %d"%(safeName(car), position + 1))
                                            #addSound("%sis_p-%d.wav"%(dirABSounds, position + 1))
                                            keyNum = str(position + 1)
                                            #edu aqui es donde repite frase de pits quito el nombre del piloto, para que no lo repita
                                            if randInRange(0, 1) == 0 or not keyNum in dicNumbers:
                                                #addSound("%sha entrado al pitlein cuando iba el %d.wav"%(dirABSounds, position + 1))
                                                addSound("ha entrado al pitlein cuando iba en p %d.wav"%(position + 1))
                                                pVoiceTimeedu = clock()
                                            else:
                                                #ConsoleLog("Speaking from dicNumbers 600")
                                                #addSound("%sentró en boxes cuando estaba en p_%s_.wav"%(dirABSounds, dicNumbers[keyNum]))
                                                addSound("entró cuando estaba en p_%s_.wav"%(dicNumbers[keyNum]))
                                                pVoiceTimeedu = clock()
                                            
                                            #add a period
                                            ###################addSound(dirABSounds + "..wav")
                                            #edu hago que no repita nada de ese mismo piloto cuando este tío entre en pits
                                            norepetirenpits = 1
                                            ConsoleLog("repetir en pits ahora es verdadero")
                                    elif valueWas > 0 and not inPits:
                                    
                                        if AppDic["Car0LapTime"] > 0.1 and speedKMH > 0.1 and speedKMH < 90.0: #actually driving out of the pits
                                            dic[tmpKey] = time.clock()
                                            addSound(fname)
                                            #ConsoleLog("Exiting: lapTime = %0.2f and speedKMH = %0.2f"%(AppDic["Car0LapTime"], speedKMH))
                                            if verbose:
                                                ConsoleLog("{} exiting the pits".format(ab_driverName))
                                            
                                            
                                            #EDU SUSSY
                                            #leo el fichero de probabilidad de leer las frases
                                            # Lee el número del archivo externo
                                            Name_File = 'apps\\python\\AnnouncerBot\\probabilidadsusy.txt'
                                            with open(Name_File, 'r')as f:
                                                probabilidad = int(f.read())
                                                print(probabilidad)
                                                ConsoleLog("numero4: SALIR DE PITS probabilidad %s"%(probabilidad))
                                            # Si la probabilidad es mayor que 0 y menor que 100
                                            # Si la probabilidad es mayor que 0 y menor que 100
                                            if 0 < probabilidad < 101:
                                                # Ejecuta la sentencia if con la probabilidad correspondiente
                                                azarnum = random.uniform(0, 100)
                                                ConsoleLog("numeroazar: %s"%(azarnum))
                                                if azarnum < probabilidad :


                                                    
                                            
                                            
                                            
                                            
                                            
                                                    #generate a random number between 0 and 9
                                                    numero4 = randInRange(0, 51)
                                                    if numero4 == 0:
                                                        addSound(dirABSounds + "está saliendo de pits,.wav")
                                                    elif numero4 == 1:
                                                        addSound(dirABSounds + "abandona los pits,.wav")
                                                    elif numero4 == 2:
                                                        addSound(dirABSounds + "ya sale de pits._._veamos su posición final,.wav")
                                                    elif numero4 == 3:
                                                        addSound(dirABSounds + "consigue una buena parada y ya sale de boxes,.wav") 
                                                    elif numero4 == 4:
                                                        addSound(dirABSounds + "abandona los boxes tras una parada lenta,.wav") 
                                                    elif numero4 == 5:
                                                        addSound(dirABSounds + "cambia neumáticos y sale del pitlein,.wav") 
                                                    elif numero4 == 6:
                                                        addSound(dirABSounds + "escapando del pitlein,.wav") 
                                                    elif numero4 == 7:
                                                        addSound(dirABSounds + "saliendo del pitlein tras una parada regular,.wav") 
                                                    elif numero4 == 8:
                                                        addSound(dirABSounds + "ha llenado el depósito y sale de pits,.wav") 
                                                    elif numero4 == 9:
                                                        addSound(dirABSounds + "vuelve a pista.wav")   
                                                    elif numero4 == 10:
                                                        addSound(dirABSounds + "saliendo del pitlein tras una parada regular,.wav") 
                                                    elif numero4 == 11:
                                                        addSound(dirABSounds + "Se reincorpora a la carrera.wav") 
                                                    elif numero4 == 12:
                                                        addSound(dirABSounds + "Empieza nuevo estínt.wav")                                                              
                                                    elif numero4 == 13:
                                                        addSound(dirABSounds + "intenta recuperar posiciones después de una parada en boxes.wav")        
                                                    elif numero4 == 14:
                                                        addSound(dirABSounds + "se coloca en una buena posición después de una parada en boxes.wav")        
                                                    elif numero4 == 15:
                                                        addSound(dirABSounds + "sale de pits con neumáticos nuevos.wav")        
                                                    elif numero4 == 16:
                                                        addSound(dirABSounds + "pierde tiempo en su parada en boxes.wav")        
                                                    elif numero4 == 17:
                                                        addSound(dirABSounds + "se encuentra en una mala posición después de su parada en boxes.wav")        
                                                    elif numero4 == 18:
                                                        addSound(dirABSounds + "sale de pits con una nueva estrategia.wav")        
                                                    elif numero4 == 19:
                                                        addSound(dirABSounds + "regresa a pista después de una parada en boxes.wav")
                                                    elif numero4 == 20:
                                                        addSound(dirABSounds + "sale de los garajes después de una parada rápida.wav")
                                                    elif numero4 == 21:
                                                        addSound(dirABSounds + "se reincorpora a la carrera después de una parada en boxes.wav")
                                                    elif numero4 == 22:
                                                        addSound(dirABSounds + "sale de pits con un juego de neumáticos nuevos.wav")
                                                    elif numero4 == 23:
                                                        addSound(dirABSounds + "abandona los boxes tras una parada rápida.wav")
                                                    elif numero4 == 24:
                                                        addSound(dirABSounds + "vuelve a pista después de una parada en boxes.wav")
                                                    elif numero4 == 25:
                                                        addSound(dirABSounds + "sale de los garajes tras una parada prolongada.wav")
                                                    elif numero4 == 26:
                                                        addSound(dirABSounds + "se reincorpora a la carrera después de una parada en boxes.wav")
                                                    elif numero4 == 27:
                                                        addSound(dirABSounds + "sale de pits tras una parada rápida.wav") 
                                                    elif numero4 == 28:
                                                        addSound(dirABSounds + "sale de los garajes y se coloca en una buena posición en la pista.wav")
                                                    elif numero4 == 29:
                                                        addSound(dirABSounds + "sale de boxes con neumáticos nuevos y listo para seguir la carrera.wav")
                                                    elif numero4 == 30:
                                                        addSound(dirABSounds + "sale de los pits tras una parada rápida y se une a la lucha por la victoria.wav")
                                                    elif numero4 == 31:
                                                        addSound(dirABSounds + "reporta que su parada en boxes fue un desastre para el coche, perdiendo varias posiciones en el proceso.wav")
                                                    elif numero4 == 32:
                                                        addSound(dirABSounds + "sale de los pits y comienza a adelantar a sus rivales gracias a sus neumáticos frescos.wav")
                                                    elif numero4 == 33:
                                                        addSound(dirABSounds + "siguiendo una estrategia arriesgada en boxes, pero el coche consigue mantenerse en la pelea.wav")
                                                    elif numero4 == 34:
                                                        addSound(dirABSounds + "sale de los pits en última posición, pero con una estrategia agresiva busca recuperar terreno.wav")
                                                    elif numero4 == 35:
                                                        addSound(dirABSounds + "sale de boxes con una nueva estrategia y busca sorprender a sus rivales en la pista.wav")
                                                    elif numero4 == 36:
                                                        addSound(dirABSounds + "sale de los pits en una posición desafortunada, pero intentará hacer una carrera inteligente para recuperar terreno.wav")
                                                    elif numero4 == 37:
                                                        addSound(dirABSounds + "sale de los pits tras una parada regular y se coloca en una posición intermedia en la pista.wav")
                                                    elif numero4 == 38:
                                                        addSound(dirABSounds + "sale de boxes en una posición desventajosa, pero buscará adelantar a sus rivales en la pista.wav")
                                                    elif numero4 == 39:
                                                        addSound(dirABSounds + "consigue una buena parada en boxes y sale en una posición competitiva.wav")
                                                    elif numero4 == 40:
                                                        addSound(dirABSounds + "sale de pits en una posición intermedia y buscará mantenerse en la pelea.wav")
                                                    elif numero4 == 41:
                                                        addSound(dirABSounds + "sale de los garajes y se coloca en una buena posición en la pista.wav")
                                                    elif numero4 == 42:
                                                        addSound(dirABSounds + "regresa a la pista después de una parada en boxes.wav")
                                                    elif numero4 == 43:
                                                        addSound(dirABSounds + "sale de los garajes después de una parada rápida.wav")
                                                    elif numero4 == 44:
                                                        addSound(dirABSounds + "abandona los pits y se coloca en una posición intermedia en la pista.wav")
                                                    elif numero4 == 45:
                                                        addSound(dirABSounds + "sale de los pits con una estrategia agresiva y busca adelantar a sus rivales.wav")
                                                    elif numero4 == 46:
                                                        addSound(dirABSounds + "sale de los garajes en una posición desventajosa, pero no se rinde y sigue luchando.wav")
                                                    elif numero4 == 47:
                                                        addSound(dirABSounds + "sale de los pits con neumáticos nuevos y busca recuperar terreno en la pista.wav")
                                                    elif numero4 == 48:
                                                        addSound("el equipo de " + dirABSounds + " nos cuenta que La parada en boxes ha sido un éxito para el coche, que sale de los garajes en una buena posición.wav")
                                                    elif numero4 == 49:
                                                        addSound(dirABSounds + "sale de los pits con una nueva estrategia y busca sorprender a sus rivales.wav")
                                                    elif numero4 == 50:
                                                        addSound(dirABSounds + "sale de los pits tras una parada regular y busca mantener su posición en la pista.wav")
                                                    elif numero4 == 51:
                                                        addSound(dirABSounds + "sale de los garajes en una posición intermedia y lucha por mejorar su posición en la pista.wav")

                                                    pVoiceTimeedu = clock()

                                            #edu
                                            #con esto reiniciamos el contador de tiempo de voz, para las frases de relleno que tengo al final que suenan
                                            #cuando han pasado 15 segundos sin que se haya dicho nada
                                          




                                            reportTyreCompoundAB(car)
                                            #add a period
                                            ###################addSound(dirABSounds + "..wav")
                                            
                                            #if ac.getCarTyreCompound(car) == "A":
                                            #    addSound(dirABSounds + "exiting_pits_on_alternates.wav")
                                            #elif ac.getCarTyreCompound(car) == "P":
                                            #    addSound(dirABSounds + "exiting_pits_on_primaries.wav")
                                            #else:
                                            #    addSound(dirABSounds + "exiting_the_pits.wav")
                                        #I think we can skip this for now    
                                        elif False: # not "raceStart" in dic : #I THINK THIS WAS FIRING DURING THE RACE, so adding logic
                                            #TIRES DRIVER CHOSE TO START THE RACE WITH
                                            addSound(fname)
                                            ConsoleLog("On Grid: lapTime = %0.2f and speedKMH = %0.2f"%(lapTime, speedKMH))
                                            #IS STARTING P#?
                                            #ConsoleLog("Position 400")
                                            if verbose:
                                                ConsoleLog("500 - Driver %s is in position %d"%(safeName(car), position + 1))
                                            #addSound("%sis_p-%d.wav"%(dirABSounds, position + 1))
                                            keyNum = str(position + 1)
                                            if randInRange(0, 1) == 0 or not keyNum in dicNumbers:
                                                addSound("%ses_p_edu3-%d.wav"%(dirABSounds, position + 1))
                                            else:
                                                #ConsoleLog("Speaking from dicNumbers 700")
                                                addSound("%sen_edu4%s_.wav"%(dirABSounds, dicNumbers[keyNum]))
                                            
                                            reportTyreCompoundAB(car)
                                            #add a period
                                            ###################addSound(dirABSounds + "..wav")

                                            #if ac.getCarTyreCompound(car) == "A":
                                            #s    addSound(dirABSounds + "on_alternates.wav")
                                            #elif ac.getCarTyreCompound(car) == "P":
                                            #   addSound(dirABSounds + "on_primaries.wav")
                                
                else:
                    dic[tmpKey] = inPits
            
            
                #ConsoleLog("acUpdate 3000")
                #P2PStatus (OFF = 0, COOLING = 1,AVAILABLE = 2, ACTIVE = 3)
                #can we skip this for cars that don't have P2P?
                p2pStatus = ac.getCarState(car, acsys.CS.P2PStatus)
                tmpKey = "Car%dP2PStatus"%(car)
                p2pLastReported = "Car%dP2PStatusReported"%(car)
                if tmpKey in dic:
                    try:
                        #this may need to be initialized
                        varTemp = dic[p2pLastReported]
                    except:
                        dic[p2pLastReported] = 0
                        
                    #how do we track that car ahead or behind is also on P2P?  Any car within 2.5 seconds of lap and lap time?
                    #any car within X meters and 3 positions?
                    #only consider the 4 positions ahead and behind?
                    #ConsoleLog("acUpdate 3000")
                    if p2pStatus == 3 and dic[p2pLastReported] + p2pDelay < clock():
                        dic[p2pLastReported] = clock()
                        focusedPosition = AppDic[keysCarPosition[focusedCar]] # "Car{}Position".format(focusedCar)] # getPosition(focusedCar)
                        
                        if not car == focusedCar and not dic[tmpKey] == p2pStatus and p2pStatus == 3 and abs(position - focusedPosition) < 3: #(lapCount > 0 and 
                            #focusedLapTime = ac.getCarState(focusedCar, acsys.CS.LapTime)
                            #focusedLapCount = AppDic["".join(["Car", strFocusedCar, "LapCount"]) #ac.getCarState(focusedCar, acsys.CS.LapCount)
                            #focusedCarCurrPoT = AppDic["".join(["Car", strFocusedCar, "PoT"]) #ac.getCarState(focusedCar,acsys.CS.NormalizedSplinePosition)              
                            focusedCarDistance = AppDic[keysCarDistance[focusedCar]] * trackLength #(focusedLapCount + focusedCarCurrPoT) * trackLength

                            #otherCarLapCount = AppDic["".join(["Car", strCarId, "LapCount"]) # ac.getCarState(car, acsys.CS.LapCount)
                            #otherCarCurrPoT = AppDic["".join(["Car", strCarId, "PoT"]) #ac.getCarState(car,acsys.CS.NormalizedSplinePosition)              
                            otherCarDistance = AppDic[keysCarDistance[carId]] * trackLength #(otherCarLapCount + otherCarCurrPoT) * trackLength

                            #any car within 400 meters? at most 2 cars ahead and 2 behind
                            if abs(focusedCarDistance - otherCarDistance) < 400:
                                dic[tmpKey] = p2pStatus
                                fname = dirABSounds + ab_driverName + ".wav"
                                if checkSound(fname) and qSpeech.qsize() < qSkipLength and gapBetweenCars(car, focusedCar) < 1.5:
                                    focusedCurrPoT = AppDic[keysCarPoT[focusedCar]] #ac.getCarState(focusedCar,acsys.CS.NormalizedSplinePosition)
                                    if currPoT > focusedCurrPoT:
                                        addSound(fname)
                                        #ahead
                                        addSound(dirABSounds + "ahead.wav")
                                        if isVoiceTTS:                                            
                                            addSound(dirABSounds + "is_on_PToP.wav")
                                        else:
                                            addSound(dirABSounds + "is_on_p2p.wav")
                                        #add a period
                                        ###################addSound(dirABSounds + "..wav")                                    
                                    else:
                                        addSound(fname)
                                        #behind
                                        addSound(dirABSounds + "behind.wav")
                                        if isVoiceTTS:                                            
                                            addSound(dirABSounds + "is_on_PToP.wav")
                                        else:
                                            addSound(dirABSounds + "is_on_p2p.wav")
                                        #add a period
                                        ###################addSound(dirABSounds + "..wav")
                        
                        if car == focusedCar and not dic[tmpKey] == p2pStatus and p2pStatus == 3:
                            dic[tmpKey] = p2pStatus
                            
                            #already populated
                            #driverName = getABotDriverName(car)
                            #ab_driverName = driverName.replace(" ", "_")
                            
                            #dirABSounds
                            fname = dirABSounds + ab_driverName + ".wav"
                            if checkSound(fname):
                                #ConsoleLog("saying %s"%(ab_driverName))
                                addSound(fname)
                                if isVoiceTTS:                                            
                                    addSound(dirABSounds + "is_on_PToP.wav")
                                else:
                                    addSound(dirABSounds + "is_on_p2p.wav")
                                #add a period
                                ###################addSound(dirABSounds + "..wav")                            
                    else:
                        dic[tmpKey] = p2pStatus
                else:
                    dic[tmpKey] = p2pStatus



            lapCount = ac.getCarState(car, acsys.CS.LapCount)
            focusedCarLapCount = AppDic["".join(["Car", strCarId, "LapCount"])]
            if focusedCarLapCount != 0:  # Si es la primera vuelta

                if clock() - pVoiceTimeedu > 15:  # 15 segundos es buen valor 18

                    random_number = random.randint(1, 62)

                    carPosition = AppDic[keysCarPosition[focusedCar]]
                    carPosition = carPosition + 1
                    posicionenfocado = carPosition
                    posicionadelante = posicionenfocado - 1
                    posiciondetras = posicionenfocado + 1

                    otherCarIdDelante = AppDic[keysPositionCar[carPosition - 2]]
                    otherCarIdDetras = AppDic[keysPositionCar[carPosition]]
                    Driverenfocado = getABotDriverName(focusedCar)
                    DriverDelante = getABotDriverName(otherCarIdDelante)
                    DriverDetras = getABotDriverName(otherCarIdDetras)

                    ballast = ac.getCarBallast(focusedCar)
                    ballastDelante = ac.getCarBallast(otherCarIdDelante)
                    ballastDetras = ac.getCarBallast(otherCarIdDetras)

                    otherCarIdDelantegap = AppDic[keysPositionCar[carPosition - 1]]
                    otherCarIdDetrasgap = AppDic[keysPositionCar[carPosition - 1]]
                    GapDelante = round(AppDic[keysCarTimeGapAhead[otherCarIdDelantegap]], 1)
                    GapDetras = round(AppDic[keysCarTimeGapBehind[otherCarIdDetrasgap]], 1)

                    posicionSalidaDelante = getSavedPosition(otherCarIdDelante)
                    posicionSalida = getSavedPosition(focusedCar)
                    posicionSalidaDetras = getSavedPosition(otherCarIdDetras)

                    

                    ruedasenfocado = ac.getCarTyreCompound(focusedCar)
                    ruedasDelante = ac.getCarTyreCompound(otherCarIdDelante)
                    ruedasDetras = ac.getCarTyreCompound(otherCarIdDetras)
                    
                    ConsoleLog("las ruedas del enfocado son %s las del piloto de delante son %s y las del piloto de detrás son %s"%(ruedasenfocado, ruedasDelante,ruedasDetras))


                    if random_number == 1:             
                        addSound("Hay mucha acción en la pista en este momento, y %s y %s son los protagonistas"%(getABotDriverName(focusedCar), DriverDelante))
                        #addSound("El piloto enfocado %s salió en P%s, el piloto de delante %s en P%s y el piloto de detrás %s en P%s" % (Driverenfocado, posicionSalida, DriverDelante, posicionSalidaDelante, DriverDetras, posicionSalidaDetras)) 






                        # addSound("el piloto se llama %s y está en p %s"%(Driverenfocado,posicionenfocado))
                        # addSound("salió en p %s con %s kilos de lastre"%(posicionSalida,ballast))

                        # addSound("el piloto de delante se llama %s y está en posición %s"%(DriverDelante,posicionadelante))
                        # addSound("salió en p %s con %s kilos de lastre"%(posicionSalidaDelante,ballastDelante))

                        # addSound("el piloto de detras se llama %s y está en posición %s"%(DriverDetras,posiciondetras))
                        # addSound("salió en p %s con %s kilos de lastre"%(posicionSalidaDetras,ballastDetras))

                        #addSound("el piloto %s tiene un gap con el de delante de %s"%(getABotDriverName(focusedCar),GapDelante))
                        #addSound("el piloto %s tiene un gap con el de detrás de %s"%(getABotDriverName(focusedCar),GapDetras))
                                        
                        # ConsoleLog("el piloto se llama %s y está en p %s"%(getABotDriverName(focusedCar),posicionenfocado))
                        # ConsoleLog("salió en p %s con %s kilos de lastre"%(posicionSalida,ballast))
                        # ConsoleLog("el piloto de delante se llama %s y está en posición %s"%(DriverDelante,posicionadelante))
                        # ConsoleLog("salió en p %s con %s kilos de lastre"%(posicionSalidaDelante,ballastDelante))
                        # ConsoleLog("el piloto de detras se llama %s y está en posición %s"%(DriverDetras,posiciondetras))
                        # ConsoleLog("salió en p %s con %s kilos de lastre"%(posicionSalidaDetras,ballastDetras))
                        # ConsoleLog("el piloto %s tiene un gap con el de delante de %s"%(getABotDriverName(focusedCar),GapDelante))
                        # ConsoleLog("el piloto %s tiene un gap con el de detrás de %s"%(getABotDriverName(focusedCar),GapDetras))
                        

                    elif random_number == 2:            
                        addSound("%s y %s deberían vigilar a %s que está por detrás a %s segundos"%(Driverenfocado, DriverDelante, DriverDetras, GapDetras))

                    elif random_number == 3:
                        addSound("¡%s ha hecho una vuelta impresionante para intentar adelantar a %s ! ¡Eso es lo que se llama un buen manejo!"%(Driverenfocado, DriverDelante))

                    elif random_number == 4:
                        addSound("La carrera es emocionante. En estos momentos, %s ocupa la posición %s en la pista. Sin embargo, %s se encuentra justo detrás de él, mientras que %s saca ventaja a ambos."%(Driverenfocado, posicionenfocado, DriverDetras, DriverDelante))

                    elif random_number == 5:
                        addSound("veremos si La estrategia de neumáticos dará sus frutos. %s ha optado por un compuesto que parece dominar mejor que %s y eso le está permitiendo mantener una velocidad constante. ¿será un aviso?"%(Driverenfocado, DriverDelante))

                    elif random_number == 6:
                        addSound("Las emociones están al límite en la pista. %s ha estado presionando a %s durante varias vueltas"%(Driverenfocado, DriverDelante))

                    elif random_number == 7:
                        addSound("La pista se encuentra en excelentes condiciones, lo que ha permitido que los pilotos aumenten su velocidad. %s ha logrado mantener su posición en la p %s y se encuentra a poco tiempo de %s"%(Driverenfocado, posicionenfocado, DriverDelante))

                    elif random_number == 8:
                        addSound("La lucha por la posición que vemos en cámara está encendida. a %s le ha tocado defenderse de un agresivo %s que está a solo %s segundos detrás y no se dará por vencido hasta el final de la carrera"%(Driverenfocado, DriverDetras, GapDetras))

                    elif random_number == 9:
                        addSound("%s demostró su habilidad. antes le ha tocado evitar un choque con %s que había perdido ligéramente el control del coche"%(Driverenfocado, DriverDelante))

                    elif random_number == 10:
                        addSound("La tensión en la pista es palpable. %s está tratando de mantener su posición mientras que %s y %s están a sus espaldas, esperando cualquier fallo para adelantar"%(DriverDelante, Driverenfocado, DriverDetras))

                    elif random_number == 11:
                        addSound("%s está en los límites de la pista, y logra mantener la posición. %s y %s están esperando el fallo por detrás, tratando de aprovechar la situación"%(DriverDelante, DriverDetras, Driverenfocado))

                    elif random_number == 12:
                        addSound("El coche enfocado de %s tiene un lastre de %s kilos, clara desventaja para él, pero así es uve erre ese y sus malditos lastres"%(Driverenfocado, ballast))

                    elif random_number == 13:
                        addSound("%s está mostrando gran habilidad en las curvas, lo cual lo mantiene a salvo por ahora de los pilotos que lo siguen"%(Driverenfocado))

                    elif random_number == 14:
                        addSound("%s ha logrado reducir la ventaja que %s tenía sobre él en la última vuelta. ¡La lucha por la posición aún no ha terminado! queda carrera"%(DriverDetras, Driverenfocado))

                    elif random_number == 15:
                        addSound("La pista tiene mucho grip y %s pierde algo de tiempo. ¡Esto puede ser una oportunidad para %s y %s!"%(DriverDelante, DriverDetras, Driverenfocado))

                    elif random_number == 16:
                        addSound("%s ha logrado un buen ritmo en la última vuelta, confirmando su superioridad sobre  %s y %s"%(DriverDelante, Driverenfocado, DriverDetras))

                    elif random_number == 17:
                        addSound("%s está demostrando un gran desempeño,  %s no logra alcanzarle, pero si puede le va a relegar a la p%s"%(Driverenfocado, DriverDetras, posiciondetras))
                    
                    elif random_number == 18:
                        addSound("El lastre de %s kilos en el coche de %s está afectando su velocidad. Esto puede ser una oportunidad para %s"%(ballast, Driverenfocado, DriverDetras))

                    elif random_number == 19:
                        addSound("hemos visto que %s ha estado presionando a %s durante varias vueltas"%(DriverDetras, Driverenfocado))

                    elif random_number == 20:
                        addSound("La carrera ha estado muy pareja hasta ahora, pero %s logra crear una ventaja de %s segundos sobre sus perseguidores"%(Driverenfocado, GapDetras))
                    elif random_number == 21:
                        addSound("¡Es increíble lo que está haciendo %s en la pista! Ha logrado avanzar varias posiciones hoy."%(Driverenfocado))

                    elif random_number == 22:
                        addSound("%s por delante de %s ¡un tío muy rápido! .por Ahora tiene el camino libre."%(DriverDelante, Driverenfocado))

                    elif random_number == 23:
                        addSound("El público está enloquecido con la carrera que están dando estos pilotos. ¡Esto es automovilismo en estado puro!")

                    elif random_number == 24:
                        addSound("La tensión es palpable en la pista. %s y %s han luchado mucho por la misma posición, ¡incluso casi llegan al choque!"%(Driverenfocado, DriverDetras))

                    elif random_number == 25:
                        addSound("¡Esto es un festival!. %s, %s y %s están dando todo lo que tienen para subir posiciones."%(DriverDelante, Driverenfocado, DriverDetras))

                    elif random_number == 26:
                        addSound("La pista está cada vez con más grip, eso favorece a %s, que sigue adelante con valentía."%(Driverenfocado))

                    elif random_number == 27:
                        addSound("¡Vaya salto que ha dado %s en el último piano!. Eso es lo que se llama volar bajo, ¡y encima sin perder velocidad!"%(Driverenfocado))

                    elif random_number == 28:
                        addSound("La carrera continúa para  %s .Parece que nadie va a poder alcanzarle."%(Driverenfocado))

                    elif random_number == 29:
                        addSound("¡Se ha desatado el caos en la pista!. %s casi sufre un accidente . veremos si pierde mucho tiempo"%(DriverDelante))

                    elif random_number == 30:
                        addSound("¡Esto es espectacular!. %s ha logrado una buena posición .¡Qué carrera nos está regalando!"%(Driverenfocado))
                    elif random_number == 31:
                        addSound("¡Qué carrera más emocionante!. %s está luchando con uñas y dientes para mantener su posición, pero le sigue %s y %s más atrás, no se lo van a regalar."%(DriverDelante, Driverenfocado, DriverDetras))

                    elif random_number == 32:
                        addSound("El ritmo de carrera es frenético y los adelantamientos se han sucedido sin descanso. ¡Esto es lo que nos gusta ver a los aficionados del motor!")

                    elif random_number == 33:
                        addSound("¡Vaya pelea más intensa! %s y %s han estado intercambiando posiciones en cada curva. ¡una auténtica batalla campal!"%(Driverenfocado, DriverDelante))

                    elif random_number == 34:
                        addSound("¡Mira a %s! Ha hecho una rápida corrección para evitar una salida de pista y ha conseguido mantenerse en carrera. ¡Eso es lo que se llama habilidad al volante!"%(Driverenfocado))

                    elif random_number == 35:
                        addSound(" %s tiene una ventaja relativa. Pero no  puede bajar la guardia, porque cualquier error puede costarle la plaza."%(Driverenfocado))

                    elif random_number == 36:
                        addSound("¡Qué carrera más loca!. que se lo digan a %s "%(Driverenfocado))

                    elif random_number == 37:
                        addSound(" %s con un ojo puesto en %s , se la juega en cada curva para intentar llegar hasta él"%(Driverenfocado, DriverDelante))

                    elif random_number == 38:
                        addSound("¡Mira a %s! Está pilotando como un auténtico campeón. hoy ha adelantado a unos cuantos rivales sin piedad."%(Driverenfocado))

                    elif random_number == 39:
                        addSound("La tensión en la pista es máxima. %s y %s están separados por poco tiempo, y cada uno quiere la posición a toda costa."%(Driverenfocado, DriverDelante))





                    elif random_number == 40:    

                        delante_gana_pierde = posicionSalidaDelante - posicionadelante
                        delante_gana_pierde_final = "GANADO" if delante_gana_pierde > 0 else "PERDIDO" if delante_gana_pierde < 0 else "mantenido"
                        posiciones_ganadas_perdidas_delante = delante_gana_pierde

                        enfocado_gana_pierde = posicionSalida - posicionenfocado
                        enfocado_gana_pierde_final = "GANADO" if enfocado_gana_pierde > 0 else "PERDIDO" if enfocado_gana_pierde < 0 else "mantenido"
                        posiciones_ganadas_perdidas_enfocado = enfocado_gana_pierde

                        if posiciones_ganadas_perdidas_enfocado > posiciones_ganadas_perdidas_delante:
                            nombreGanador = Driverenfocado
                        elif posiciones_ganadas_perdidas_enfocado < posiciones_ganadas_perdidas_delante:
                            nombreGanador = DriverDelante
                        else:
                            nombreGanador = "ninguno de los dos"

                        if abs(posiciones_ganadas_perdidas_enfocado) == 1:
                            posiciones_enfocado_str = "posición"
                        elif posiciones_ganadas_perdidas_enfocado == 0:
                            posiciones_enfocado_str = "su posición"
                        else:
                            posiciones_enfocado_str = "posiciones"

                        if abs(posiciones_ganadas_perdidas_delante) == 1:
                            posiciones_delante_str = "posición"
                        elif posiciones_ganadas_perdidas_delante == 0:
                            posiciones_delante_str = "su posición"
                        else:
                            posiciones_delante_str = "posiciones"
                        
                        if posiciones_ganadas_perdidas_enfocado == 0 and posiciones_ganadas_perdidas_delante == 0:
                            addSound("%s y %s en las mismas posiciones de salida. el ritmo de carrera de ambos parece ser similar y la posición va a depender de un error de cualquiera de los dos." % (Driverenfocado, DriverDelante))
                        else:
                            if abs(posiciones_ganadas_perdidas_enfocado) == 1:
                                posiciones_enfocado_str = "posición"
                            else:
                                posiciones_enfocado_str = "posiciones"

                            if abs(posiciones_ganadas_perdidas_delante) == 1:
                                posiciones_delante_str = "posición"
                            else:
                                posiciones_delante_str = "posiciones"

                            addSound("%s ha %s %d %s desde la salida, y %s ha %s %d %s. Por lo tanto, el ritmo de carrera de %s parece ser mayor y todo indica que esta lucha terminará ganándola él." % (Driverenfocado, enfocado_gana_pierde_final, abs(posiciones_ganadas_perdidas_enfocado), posiciones_enfocado_str, DriverDelante, delante_gana_pierde_final, abs(posiciones_ganadas_perdidas_delante), posiciones_delante_str, nombreGanador))






                    # elif random_number == 41:    

                    #     delante_gana_pierde = posicionSalidaDelante - posicionadelante
                    #     delante_gana_pierde_final = "GANADO" if delante_gana_pierde > 0 else "PERDIDO" if delante_gana_pierde < 0 else "mantenido"
                    #     posiciones_ganadas_perdidas_delante = delante_gana_pierde

                    #     enfocado_gana_pierde = posicionSalida - posicionenfocado
                    #     enfocado_gana_pierde_final = "GANADO" if enfocado_gana_pierde > 0 else "PERDIDO" if enfocado_gana_pierde < 0 else "mantenido"
                    #     posiciones_ganadas_perdidas_enfocado = enfocado_gana_pierde

                    #     if posiciones_ganadas_perdidas_enfocado > posiciones_ganadas_perdidas_delante:
                    #         nombreGanador = Driverenfocado
                    #     elif posiciones_ganadas_perdidas_enfocado < posiciones_ganadas_perdidas_delante:
                    #         nombreGanador = DriverDelante
                    #     else:
                    #         nombreGanador = "ninguno de los dos"

                    #     if abs(posiciones_ganadas_perdidas_enfocado) == 1:
                    #         posiciones_enfocado_str = "posición"
                    #     elif posiciones_ganadas_perdidas_enfocado == 0:
                    #         posiciones_enfocado_str = "su posición"
                    #     else:
                    #         posiciones_enfocado_str = "posiciones"

                    #     if abs(posiciones_ganadas_perdidas_delante) == 1:
                    #         posiciones_delante_str = "posición"
                    #     elif posiciones_ganadas_perdidas_delante == 0:
                    #         posiciones_delante_str = "su posición"
                    #     else:
                    #         posiciones_delante_str = "posiciones"
                        
                    #     if posiciones_ganadas_perdidas_enfocado == 0 and posiciones_ganadas_perdidas_delante == 0:
                    #         addSound("%s y %s mantienen sus posiciones desde la salida. Por lo tanto, el ritmo de carrera de ambos parece ser similar y la lucha por la posición continuará." % (Driverenfocado, DriverDelante))
                    #     else:
                    #         if abs(posiciones_ganadas_perdidas_enfocado) == 1:
                    #             posiciones_enfocado_str = "posición"
                    #         else:
                    #             posiciones_enfocado_str = "posiciones"

                    #         if abs(posiciones_ganadas_perdidas_delante) == 1:
                    #             posiciones_delante_str = "posición"
                    #         else:
                    #             posiciones_delante_str = "posiciones"

                    #         addSound("%s ha %s %d %s desde la salida, y %s ha %s %d %s. Por lo tanto, el ritmo de carrera de %s parece ser mayor y todo indica que esta lucha terminará ganándola él." % (Driverenfocado, enfocado_gana_pierde_final, abs(posiciones_ganadas_perdidas_enfocado), posiciones_enfocado_str, DriverDelante, delante_gana_pierde_final, abs(posiciones_ganadas_perdidas_delante), posiciones_delante_str, nombreGanador))




                    # elif random_number == 42:    

                    #     delante_gana_pierde = posicionSalidaDelante - posicionadelante
                    #     delante_gana_pierde_final = "GANADO" if delante_gana_pierde > 0 else "PERDIDO" if delante_gana_pierde < 0 else "mantenido"
                    #     posiciones_ganadas_perdidas_delante = delante_gana_pierde

                    #     enfocado_gana_pierde = posicionSalida - posicionenfocado
                    #     enfocado_gana_pierde_final = "GANADO" if enfocado_gana_pierde > 0 else "PERDIDO" if enfocado_gana_pierde < 0 else "mantenido"
                    #     posiciones_ganadas_perdidas_enfocado = enfocado_gana_pierde

                    #     if posiciones_ganadas_perdidas_enfocado > posiciones_ganadas_perdidas_delante:
                    #         nombreGanador = Driverenfocado
                    #     elif posiciones_ganadas_perdidas_enfocado < posiciones_ganadas_perdidas_delante:
                    #         nombreGanador = DriverDelante
                    #     else:
                    #         nombreGanador = "ninguno de los dos"

                    #     if abs(posiciones_ganadas_perdidas_enfocado) == 1:
                    #         posiciones_enfocado_str = "posición"
                    #     elif posiciones_ganadas_perdidas_enfocado == 0:
                    #         posiciones_enfocado_str = "su posición"
                    #     else:
                    #         posiciones_enfocado_str = "posiciones"

                    #     if abs(posiciones_ganadas_perdidas_delante) == 1:
                    #         posiciones_delante_str = "posición"
                    #     elif posiciones_ganadas_perdidas_delante == 0:
                    #         posiciones_delante_str = "su posición"
                    #     else:
                    #         posiciones_delante_str = "posiciones"
                        
                    #     if posiciones_ganadas_perdidas_enfocado == 0 and posiciones_ganadas_perdidas_delante == 0:
                    #         addSound("%s y %s están manteniendo su posición desde el comienzo de la carrera. mismos tiempos y mismo ritmo para ambos." % (Driverenfocado, DriverDelante))
                    #     else:
                    #         if abs(posiciones_ganadas_perdidas_enfocado) == 1:
                    #             posiciones_enfocado_str = "posición"
                    #         else:
                    #             posiciones_enfocado_str = "posiciones"

                    #         if abs(posiciones_ganadas_perdidas_delante) == 1:
                    #             posiciones_delante_str = "posición"
                    #         else:
                    #             posiciones_delante_str = "posiciones"

                    #         addSound("%s ha %s %d %s desde el comienzo, en cambio,  %s ha %s %d %s. El ritmo de carrera de %s es superior y parece que ganará esta batalla." % (Driverenfocado, enfocado_gana_pierde_final, abs(posiciones_ganadas_perdidas_enfocado), posiciones_enfocado_str, DriverDelante, delante_gana_pierde_final, abs(posiciones_ganadas_perdidas_delante), posiciones_delante_str, nombreGanador))






                    # elif random_number == 43:    

                    #     delante_gana_pierde = posicionSalidaDelante - posicionadelante
                    #     delante_gana_pierde_final = "GANADO" if delante_gana_pierde > 0 else "PERDIDO" if delante_gana_pierde < 0 else "mantenido"
                    #     posiciones_ganadas_perdidas_delante = delante_gana_pierde

                    #     enfocado_gana_pierde = posicionSalida - posicionenfocado
                    #     enfocado_gana_pierde_final = "GANADO" if enfocado_gana_pierde > 0 else "PERDIDO" if enfocado_gana_pierde < 0 else "mantenido"
                    #     posiciones_ganadas_perdidas_enfocado = enfocado_gana_pierde

                    #     if posiciones_ganadas_perdidas_enfocado > posiciones_ganadas_perdidas_delante:
                    #         nombreGanador = Driverenfocado
                    #     elif posiciones_ganadas_perdidas_enfocado < posiciones_ganadas_perdidas_delante:
                    #         nombreGanador = DriverDelante
                    #     else:
                    #         nombreGanador = "ninguno de los dos"

                    #     if abs(posiciones_ganadas_perdidas_enfocado) == 1:
                    #         posiciones_enfocado_str = "posición"
                    #     elif posiciones_ganadas_perdidas_enfocado == 0:
                    #         posiciones_enfocado_str = "su posición"
                    #     else:
                    #         posiciones_enfocado_str = "posiciones"

                    #     if abs(posiciones_ganadas_perdidas_delante) == 1:
                    #         posiciones_delante_str = "posición"
                    #     elif posiciones_ganadas_perdidas_delante == 0:
                    #         posiciones_delante_str = "su posición"
                    #     else:
                    #         posiciones_delante_str = "posiciones"
                        
                    #     if posiciones_ganadas_perdidas_enfocado == 0 and posiciones_ganadas_perdidas_delante == 0:
                    #         addSound("%s y %s mantienen sus posiciones ganadas en cualy. su ritmo de carrera es casi idéntico y la lucha por la posición va a durar un buen rato." % (Driverenfocado, DriverDelante))
                    #     else:
                    #         if abs(posiciones_ganadas_perdidas_enfocado) == 1:
                    #             posiciones_enfocado_str = "posición"
                    #         else:
                    #             posiciones_enfocado_str = "posiciones"

                    #         if abs(posiciones_ganadas_perdidas_delante) == 1:
                    #             posiciones_delante_str = "posición"
                    #         else:
                    #             posiciones_delante_str = "posiciones"

                    #         addSound("%s ha %s %d %s desde que comenzó la carrera,  %s ha %s %d %s. parece que %s tiene más ritmo y ganará esta batalla." % (Driverenfocado, enfocado_gana_pierde_final, abs(posiciones_ganadas_perdidas_enfocado), posiciones_enfocado_str, DriverDelante, delante_gana_pierde_final, abs(posiciones_ganadas_perdidas_delante), posiciones_delante_str, nombreGanador))




                    # elif random_number == 44:    

                    #     delante_gana_pierde = posicionSalidaDelante - posicionadelante
                    #     delante_gana_pierde_final = "GANADO" if delante_gana_pierde > 0 else "PERDIDO" if delante_gana_pierde < 0 else "mantenido"
                    #     posiciones_ganadas_perdidas_delante = delante_gana_pierde

                    #     enfocado_gana_pierde = posicionSalida - posicionenfocado
                    #     enfocado_gana_pierde_final = "GANADO" if enfocado_gana_pierde > 0 else "PERDIDO" if enfocado_gana_pierde < 0 else "mantenido"
                    #     posiciones_ganadas_perdidas_enfocado = enfocado_gana_pierde

                    #     if posiciones_ganadas_perdidas_enfocado > posiciones_ganadas_perdidas_delante:
                    #         nombreGanador = Driverenfocado
                    #     elif posiciones_ganadas_perdidas_enfocado < posiciones_ganadas_perdidas_delante:
                    #         nombreGanador = DriverDelante
                    #     else:
                    #         nombreGanador = "ninguno de los dos"

                    #     if abs(posiciones_ganadas_perdidas_enfocado) == 1:
                    #         posiciones_enfocado_str = "posición"
                    #     elif posiciones_ganadas_perdidas_enfocado == 0:
                    #         posiciones_enfocado_str = "su posición"
                    #     else:
                    #         posiciones_enfocado_str = "posiciones"

                    #     if abs(posiciones_ganadas_perdidas_delante) == 1:
                    #         posiciones_delante_str = "posición"
                    #     elif posiciones_ganadas_perdidas_delante == 0:
                    #         posiciones_delante_str = "su posición"
                    #     else:
                    #         posiciones_delante_str = "posiciones"
                        
                    #     if posiciones_ganadas_perdidas_enfocado == 0 and posiciones_ganadas_perdidas_delante == 0:
                    #         addSound("%s y %s mantienen las posiciones en las que salieron. Por lo tanto,  la lucha por la posición continuará." % (Driverenfocado, DriverDelante))
                    #     else:
                    #         if abs(posiciones_ganadas_perdidas_enfocado) == 1:
                    #             posiciones_enfocado_str = "posición"
                    #         else:
                    #             posiciones_enfocado_str = "posiciones"

                    #         if abs(posiciones_ganadas_perdidas_delante) == 1:
                    #             posiciones_delante_str = "posición"
                    #         else:
                    #             posiciones_delante_str = "posiciones"

                    #         addSound("%s ha %s %d %s , y %s ha %s %d %s. es obvio que  %s tiene mejor ritmo de carrera." % (Driverenfocado, enfocado_gana_pierde_final, abs(posiciones_ganadas_perdidas_enfocado), posiciones_enfocado_str, DriverDelante, delante_gana_pierde_final, abs(posiciones_ganadas_perdidas_delante), posiciones_delante_str, nombreGanador))




                    elif random_number == 45:
                        addSound("algunos incidentes han hecho estragos en la pista, pero eso no frena a los pilotos. %s está gestionando la carrera con maestría, a pesar de las adversidades."%(Driverenfocado))

                    elif random_number == 46:
                        addSound("¡Qué carrera más apasionante! %s, al que vemos en pantalla, %s , por delante  y %s por detás, están luchando por la posición en una carrera que no deja respiro."%(Driverenfocado, DriverDelante, DriverDetras))

                    elif random_number == 47:
                        addSound("¡Mira a %s! Está dando todo lo que tiene para llegar hasta %s en cada vuelta, ¡y lo está consiguiendo! Esto es un auténtico duelo de titanes."%(Driverenfocado, DriverDelante))

                    elif random_number == 48:
                         addSound("¡La emoción está al límite! %s está lidiando con %s , qu está apretando fuerte para no perder posición."%(Driverenfocado, DriverDelante))

                    elif random_number == 49:
                        addSound("La estrategia de boxes está siendo clave en esta carrera. veremos cuando entra %s a cambiar neumáticos , podría ganar varias posiciones."%(Driverenfocado))

                    elif random_number == 50:
                        addSound("¡Esto es una auténtica locura! %s ha conseguido adelantar a varios coches en esta carrera ¡esto es increíble!"%(Driverenfocado))
                    elif random_number == 51:
                        addSound("¡Mira a %s! está logrando mantener la posición después del ¡duro duelo con %s, ¡esto es lo que se llama casi pilotar con el codo afuera!"%(DriverDelante, Driverenfocado))

                    elif random_number == 52:
                        addSound("La carrera está avanzando y %s sigue corriendo con autoridad, pero cuidado, porque %s está acortando la distancia poco a poco, ¡esto puede acabar en un final de infarto!"%(Driverenfocado, DriverDetras))

                    elif random_number == 53:
                         addSound("¡Vaya lucha entre %s y %s!"%(Driverenfocado, DriverDelante))

                    elif random_number == 54:
                        addSound("La pista está cada vez sumando más grip,  %s sigue apretando fuerte para conseguir subir una posición."%(Driverenfocado))

                    elif random_number == 55:
                        addSound("¡Vaya duelo más espectacular! %s y %s están luchando por la posición, y ninguno de los dos quiere ceder terreno."%(Driverenfocado, DriverDelante))

                    elif random_number == 56:
                        addSound("La estrategia de boxes va a ser decisiva en la carrera. %s y %s deberían gastar el menor tiempo posible en cada entrada a boxes."%(Driverenfocado, DriverDelante))

                    elif random_number == 57:
                        addSound("¡Qué paso más increíble ha hecho %s por el interior de la curva, rozando el piano!, ¡esto es una auténtica obra maestra!"%(Driverenfocado))

                    elif random_number == 58:
                        addSound("La tensión en la pista es máxima. %s y %s están luchando por la misma posición, y cualquier error puede costarles caro."%(Driverenfocado, DriverDelante))

                    elif random_number == 59:
                        addSound("¡Esto es un auténtico duelo de titanes! %s y %s están luchando por la posición, y ninguno de los dos quiere ceder terreno."%(Driverenfocado, DriverDelante))

                    elif random_number == 60:
                        addSound("¡Qué carrera más emocionante estamos viendo!. Los pilotos están dando lo mejor de sí en la pista, y el público está disfrutando de cada adelantamiento y maniobra arriesgada.")
                    elif random_number == 61:
                        addSound("La temperatura de la pista está afectando a los neumáticos. Los pilotos tienen que ser cuidadosos si quieren llegar a la meta sin problemas.")

                    elif random_number == 62:
                        addSound("¡buena maniobra de %s! pasando por el exterior de la curva, ganando unas milésimas con el movimiento."%(Driverenfocado))









                    elif random_number == 63:
                        addSound("La carrera está llegando a su fin y %s sigue liderando con una ventaja cómoda. Pero %s y %s no se dan por vencidos, y están luchando hasta el final."%(Driverenfocado, DriverDelante, DriverDetras))

                    elif random_number == 64:
                        addSound("¡Qué emoción estamos viviendo en la pista! %s y %s están luchando por la misma posición, y cada uno está poniendo todo su talento y habilidad en juego."%(Driverenfocado, DriverDelante))

                    elif random_number == 65:
                        addSound("La lluvia ha vuelto a aparecer en la pista, y eso está cambiando por completo el desarrollo de la carrera. Los pilotos tienen que ser más cuidadosos si no quieren acabar en la hierba."%(Driverenfocado))

                    elif random_number == 66:
                        addSound("¡Qué bonito espectáculo nos están regalando estos pilotos! %s, %s y %s están luchando por la victoria en una carrera que no deja respiro."%(Driverenfocado, DriverDelante, DriverDetras))

                    elif random_number == 67:
                        addSound("La estrategia de boxes está siendo decisiva en esta carrera. %s ha optado por una estrategia diferente y eso le está dando resultados, ¡acaba de adelantar a %s!"%(Driverenfocado, DriverDelante))

                    elif random_number == 68:
                        addSound("¡Esto es una auténtica batalla campal! %s, %s y %s están luchando por las posiciones de cabeza, y ninguno de los tres quiere ceder terreno."%(Driverenfocado, DriverDelante, DriverDetras))

                    elif random_number == 69:
                        addSound("¡Vaya adelantamiento más espectacular ha hecho %s! Ha pasado por el interior de la curva a toda velocidad, ¡y ha conseguido ganar varias posiciones en un solo movimiento!"%(Driverenfocado))

                    elif random_number == 70:
                        addSound("La pista está cada vez más resbaladiza, y eso está haciendo que los pilotos tengan que ser más cuidadosos. Pero %s está arriesgando al máximo para conseguir la victoria."%(Driverenfocado))
                    elif random_number == 71:
                        addSound("¡Mira a %s! Ha conseguido adelantar a dos coches en la recta, ¡y lo ha hecho con un solo movimiento! Esto es una auténtica exhibición de pilotaje."%(Driverenfocado))

                    elif random_number == 72:
                        addSound("La tensión en la pista es máxima. %s y %s están luchando por la primera posición, ¡y cualquier error puede costarle caro!"%(Driverenfocado, DriverDelante))

                    elif random_number == 73:
                        addSound("La carrera está llegando a su fin y %s sigue liderando con una ventaja cómoda. Pero %s y %s no se dan por vencidos, y están luchando hasta el final."%(Driverenfocado, DriverDelante, DriverDetras))

                    elif random_number == 74:
                        addSound("¡Vaya duelo más espectacular estamos viviendo en la pista! %s y %s están luchando por la primera posición, y ninguno de los dos quiere ceder terreno."%(Driverenfocado, DriverDelante))

                    elif random_number == 75:
                        addSound("La lluvia está haciendo de las suyas en la pista, pero eso no detiene a %s, que sigue apretando fuerte para conseguir la victoria."%(Driverenfocado))

                    elif random_number == 76:
                        addSound("¡Qué adelantamiento más impresionante ha hecho %s! Ha pasado por el exterior de la curva, ganando varias posiciones en un solo movimiento."%(Driverenfocado))

                    elif random_number == 77:
                        addSound("¡Vaya susto que nos ha dado %s! Ha tocado el piano en la curva y ha salido disparado hacia la hierba, pero ha conseguido mantener el control del coche."%(Driverenfocado))

                    elif random_number == 78:
                        addSound("La estrategia de boxes está siendo clave en esta carrera. %s ha optado por una estrategia diferente y eso le está dando resultados, ¡acaba de adelantar a %s!"%(Driverenfocado, DriverDelante))

                    elif random_number == 79:
                        addSound("La carrera está llegando a su fin y %s sigue liderando con autoridad. Pero %s y %s están acortando la distancia, ¡esto puede acabar en un final de infarto!"%(Driverenfocado, DriverDelante, DriverDetras))

                    elif random_number == 80:
                        addSound("La emoción está al límite en la pista. %s está liderando la carrera por una mínima ventaja, pero %s y %s están apretando fuerte para arrebatarle la primera posición."%(Driverenfocado, DriverDelante, DriverDetras))
                    elif random_number == 81:
                        addSound("¡Esto es una auténtica batalla campal! %s, %s y %s están luchando por las posiciones de cabeza, y ninguno de los tres quiere ceder terreno."%(Driverenfocado, DriverDelante, DriverDetras))

                    elif random_number == 82:
                        addSound("La carrera está llegando a su fin y %s sigue liderando con autoridad. Pero %s y %s están acortando la distancia, ¡esto puede acabar en un final de infarto!"%(Driverenfocado, DriverDelante, DriverDetras))

                    elif random_number == 83:
                        addSound("¡Vaya adelantamiento más impresionante ha hecho %s! Ha pasado por el interior de la curva a toda velocidad, ¡y ha conseguido ganar varias posiciones en un solo movimiento!"%(Driverenfocado))

                    elif random_number == 84:
                        addSound("La pista está cada vez más resbaladiza, y eso está haciendo que los pilotos tengan que ser más cuidadosos. Pero %s está arriesgando al máximo para conseguir la victoria."%(Driverenfocado))

                    elif random_number == 85:
                        addSound("La estrategia de neumáticos está siendo decisiva en esta carrera. %s ha optado por un compuesto más duro, lo que le está permitiendo mantener el ritmo en la segunda mitad de la carrera."%(Driverenfocado))

                    elif random_number == 86:
                        addSound("La lucha por la posición en la pista está siendo espectacular. %s, %s y %s están intercambiando posiciones en cada curva, ¡esto es un espectáculo para los aficionados!"%(Driverenfocado, DriverDelante, DriverDetras))

                    elif random_number == 87:
                        addSound("¡Qué carrera más emocionante estamos viviendo! Los pilotos están dando lo mejor de sí en la pista, y el público está disfrutando de cada adelantamiento y maniobra arriesgada."%(Driverenfocado))

                    elif random_number == 88:
                        addSound("La carrera está llegando a su fin y %s está liderando con una ventaja cómoda. Pero %s y %s no se dan por vencidos, y están luchando hasta el final."%(Driverenfocado, DriverDelante, DriverDetras))

                    elif random_number == 89:
                        addSound("¡Vaya maniobra más espectacular ha hecho %s! Ha pasado por el exterior de la curva, rozando el piano, ¡esto es una auténtica obra maestra!"%(Driverenfocado))

                    elif random_number == 90:
                        addSound("La tensión en la pista es máxima. %s y %s están luchando por la primera posición, ¡y cualquier error puede costarle caro!"%(Driverenfocado, DriverDelante))
                    elif random_number == 91:
                        addSound("La pista está cada vez más sucia, y eso está haciendo que los pilotos tengan que buscar nuevas trazadas. %s está liderando la carrera, ¡pero nada está decidido aún!"%(Driverenfocado))

                    elif random_number == 92:
                        addSound("La estrategia de pits está siendo crucial en esta carrera. %s ha conseguido adelantar a varios coches gracias a una parada en boxes rápida y eficiente."%(Driverenfocado))

                    elif random_number == 93:
                        addSound("La lluvia está haciendo de las suyas en la pista, y eso está poniendo a prueba la habilidad de los pilotos. %s está arriesgando al máximo para conseguir la victoria."%(Driverenfocado))

                    elif random_number == 94:
                        addSound("La lucha por la posición en la pista está siendo intensa. %s, %s y %s están intercambiando posiciones en cada vuelta, ¡y esto no se acaba hasta que se cruza la meta!"%(Driverenfocado, DriverDelante, DriverDetras))

                    elif random_number == 95:
                        addSound("La estrategia de neumáticos está siendo decisiva en esta carrera. %s ha optado por un compuesto más blando, lo que le está permitiendo marcar vueltas más rápidas en el tramo final de la carrera."%(Driverenfocado))

                    elif random_number == 96:
                        addSound("¡Vaya maniobra más espectacular ha hecho %s! Ha pasado por el interior de la curva, rozando el piano, ¡esto es una auténtica obra maestra!"%(Driverenfocado))

                    elif random_number == 97:
                        addSound("¡La tensión está en el aire en la pista! %s y %s están luchando por la primera posición, y ninguno de los dos quiere ceder terreno. ¡Esto es una carrera épica!"%(Driverenfocado, DriverDelante))

                    elif random_number == 98:
                        addSound("La carrera está llegando a su fin y %s está liderando con autoridad. Pero %s y %s no se dan por vencidos, y están acelerando al máximo para recortar la distancia."%(Driverenfocado, DriverDelante, DriverDetras))

                    elif random_number == 99:
                        addSound("La pista está cada vez más caliente, y eso está afectando a los neumáticos. Los pilotos tienen que ser cuidadosos si quieren llegar a la meta sin problemas."%(Driverenfocado))

                    elif random_number == 100:
                        addSound("La carrera está siendo una verdadera montaña rusa de emociones. Los pilotos están demostrando todo su talento y habilidad en la pista, ¡y el público no puede pedir más!"%(Driverenfocado))




                    #este funciona, los otros los he puesto para probar.
                    pVoiceTimeedu = clock()



        
        if timer < 0.1:
            #only update every tenth of a second
            return
            
        timer = 0.0  

        ac.setBackgroundOpacity(appWindow, backgroundOpacity)
        ac.drawBorder(appWindow, drawBorderVar)

        #END AppCom.dic CHECK
                
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ac.console('AnnouncerBot Update Error (logged to file)')
        ac.log(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))

def loadDriverNationalitiesFromFile():
    ConsoleLog("loadDriverNationalitiesFromFile")
    nationINIs = "apps\\python\\AnnouncerBot\\DriverTracking\\"
    for nationFile in os.listdir(nationINIs):
        if verbose:
            ConsoleLog("Checking %s"%(nationFile))
        if nationFile.endswith('.ini'):
            nationFile = nationINIs + nationFile
            #print(os.path.join("/mydir", file))
            with open(nationFile, 'r', encoding='utf-8') as file:
                if verbose:
                    ConsoleLog(nationFile)
                #get the nationcode from the filename
                nation = os.path.basename(nationFile).replace('.ini', '')
                if verbose:
                    ConsoleLog("Nation Code = %s"%(nation))
                #load the data to the driversByNation dictionary
                driversByNation[nation] = file.read().replace('\n', '')
        
def writeDriverNationaliesToFile():
    nationINI = "apps\\python\\AnnouncerBot\\DriverTracking\\NATION.ini"
    for nation in driversByNation:
        try:
            #with open(nationINI.replace('NATION', nation), "w") as text_file:
            with open(nationINI.replace('NATION', nation), "w", encoding="utf-8") as text_file:
                text_file.write(driversByNation[nation])
        except:
            pass


def ac_extDispose(*args):
    acShutdown()

def acShutdown(*args):
    #WriteLogsToFile()
    ConsoleLog("AnnouncerBot shutting down")
    #writeDriverNationaliesToFile()

    if True:
        ConsoleLog("Cleaning up voice.exe processes")
        os.system('wmic process where name="voice.exe" call terminate')
        ConsoleLog("All Done")
    
    #check if the new sector bests are better than the old sector bests?
    
def hotkey_offset():
    global soundsOn

    ConsoleLog("Ctrl+F2 hotkey called")
    
    if soundsOn:
        ConsoleLog("Toggling AutoBot Reporting OFF")
        ac.setText(btnToggle, "ABot OFF")
        soundsOn = 0
    else:
        ConsoleLog("Toggling AutoBot Reporting ON")
        ac.setText(btnToggle, "ABot ON")
        soundsOn = 1
            
# Define una función que se encargará de dibujar el texto en pantalla
def appGLBOX():
    # Dibuja el texto "BOX" en la posición (100, 100) con el color rojo
    ac.setText(appWindow1, "BOX", 100, 100, (255, 0, 0))


def listen_key():
    byref = ctypes.byref
    user32 = ctypes.windll.user32

    #ConsoleLog("Fuel Usage Key Listener")
    #Modifiers (MOD_SHIFT, MOD_ALT, MOD_CONTROL, MOD_WIN)    
    HOTKEYS = {
        1: (win32con.VK_F2, win32con.MOD_CONTROL),
    }

    def handle_f2():
        hotkey_offset()

    HOTKEY_ACTIONS = {
        1: handle_f2,
    }

    for id, (vk, modifiers) in HOTKEYS.items():
        user32.RegisterHotKey(None, id, modifiers, vk)

    try:
        msg = wintypes.MSG()
        while user32.GetMessageA(byref(msg), None, 0, 0) != 0:
            if msg.message == win32con.WM_HOTKEY:
                action_to_take = HOTKEY_ACTIONS.get (msg.wParam)
                if action_to_take:
                    action_to_take()
            user32.TranslateMessage(byref(msg))
            user32.DispatchMessageA(byref(msg))

    finally:
        for id in HOTKEYS.keys():
            user32.UnregisterHotKey(None, id)
    