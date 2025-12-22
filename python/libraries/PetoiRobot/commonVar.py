import platform
import sys
import os

try:
    from . import config
except (ImportError, ValueError):
    # When running directly as a script or relative import fails, use absolute imports
    import config

if config.SHOW_GUI:
    from tkinter import *
    from tkinter import messagebox
    from PIL import ImageTk, Image
    # Check if running in a bundled application (PyInstaller or py2app)
    if getattr(sys, 'frozen', False):
        # Running in a bundled application
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller bundle
            # For Windows, use executable directory for resources (avrdudeWin, esptoolWin, etc.)
            # This ensures we use the resources folder next to the .exe file
            if platform.system() == "Windows":
                # Get executable directory and change working directory to it
                executable_dir = os.path.dirname(os.path.abspath(sys.executable))
                os.chdir(executable_dir)
                # Use relative paths for Windows
                resourcePath = '.\\resources\\'
                releasePath = '.\\release\\'
            else:
                # Linux or other platforms (macOS uses py2app, not PyInstaller)
                _base_path = sys._MEIPASS
                os.chdir(_base_path)
                resourcePath = './resources/'
                releasePath = './release/'
        else:
            # py2app bundle (macOS)
            # In py2app, resources are in .app/Contents/Resources/
            if platform.system() == "Darwin":  # macOS
                # Get the path to the .app bundle
                # sys.executable is typically .app/Contents/MacOS/Petoi Desktop App
                executable_path = os.path.abspath(sys.executable)
                if '.app/Contents/MacOS' in executable_path:
                    # Running from .app bundle
                    # Navigate up from MacOS to Contents, then to Resources
                    macos_dir = os.path.dirname(executable_path)  # MacOS directory
                    contents_dir = os.path.dirname(macos_dir)     # Contents directory
                    _base_path = os.path.join(contents_dir, 'Resources')
                else:
                    # Fallback: use sys.executable directory
                    _base_path = os.path.dirname(executable_path)
                # Change working directory to Resources folder
                os.chdir(_base_path)
                # Use relative paths for macOS
                resourcePath = './resources/'
                releasePath = './release/'
            else:
                # Other platforms with py2app (shouldn't happen, but fallback)
                _base_path = os.path.dirname(os.path.abspath(sys.executable))
                os.chdir(_base_path)
                resourcePath = './resources/'
                releasePath = './release/'
    else:
        # Running as normal Python script
        # Get the directory where this file (commonVar.py) is located
        # commonVar.py is in pyUI/PetoiRobot/, so we need to go up one level to pyUI/
        _current_dir = os.path.dirname(os.path.abspath(__file__))
        _pyui_dir = os.path.dirname(_current_dir)  # Go up from PetoiRobot to pyUI
        
        # Change working directory to pyUI folder
        os.chdir(_pyui_dir)
        
        if platform.system() == "Windows":    # for Windows
            resourcePath = '.\\resources\\'
            releasePath = '.\\release\\'
        # elif platform.system() == "Linux":    # for Linux OS already installed the desktop app
        #     resourcePath = '/usr/share/petoi-opencat/resources/'
        #     releasePath = '/usr/share/petoi-opencat/release/'
        else:
            resourcePath = './resources/'
            releasePath = './release/'
    # Convert relative path to absolute path for sys.path.append
    _resource_abs_path = os.path.abspath(resourcePath)
    sys.path.append(_resource_abs_path)
else:
    class Tk:
        pass
    class messagebox:
        @staticmethod
        def showwarning(*args, **kwargs):
            print("Warning:", args, kwargs)

import threading
import random
import datetime
import logging

FORMAT = '%(asctime)-15s %(name)s - %(levelname)s - %(message)s'
'''
Level: The level determines the minimum priority level of messages to log. 
Messages will be logged in order of increasing severity: 
DEBUG is the least threatening, 
INFO is also not very threatening, 
WARNING needs attention, 
ERROR needs immediate attention, 
and CRITICAL means “drop everything and find out what’s wrong.” 
The default starting point is INFO, 
which means that the logging module will automatically filter out any DEBUG messages.
'''
# logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

NyBoard_version = 'NyBoard_V1_2'
verNumber = sys.version.split('(')[0].split()[0]
verNumber = verNumber.split('.')
logger.info(f"Python version is {verNumber}")
#verNumber = [2,1,1] #for testing
supportHoverTip = True
if int(verNumber[0])<3 or int(verNumber[1])<7:
    print("Please upgrade your Python to 3.7.1 or above!")
    if config.SHOW_GUI:
        root = Tk()
        root.overrideredirect(1)
        root.withdraw()
        messagebox.showwarning(title='Warning', message='Please upgrade your Python\nto 3.7.1 or above\nto show hovertips!')
        root.destroy()
    supportHoverTip = False
#    exit(0)
    
try:
    from idlelib.tooltip import Hovertip
except Exception as e:
    logger.info("Cannot import hovertip!")
    supportHoverTip = False
    
modelOptions = [
    'Nybble',
    'Nybble Q',
    'Bittle',
    'Bittle X',
    'Bittle X+Arm',
    'DoF16',
    'Chero'
]

NaJoints = {
    'Nybble': [3, 4, 5, 6, 7],
    'Bittle': [1, 2, 3, 4, 5, 6, 7],
#    'BittleX': [1, 2, 3, 4, 5, 6, 7],
    'BittleX+Arm': [3, 4, 5, 6, 7],
    'DoF16' : [],
    'Chero' : []
}

BittleRScaleNames = [
    'Claw Pan', 'Claw Lift', 'Claw Open', 'N/A',
    'Shoulder', 'Shoulder', 'Shoulder', 'Shoulder',
    'Arm', 'Arm', 'Arm', 'Arm',
    'Knee', 'Knee', 'Knee', 'Knee']

RegularScaleNames = [
    'Head Pan', 'Head Tilt', 'Tail Pan', 'N/A',
    'Shoulder', 'Shoulder', 'Shoulder', 'Shoulder',
    'Arm', 'Arm', 'Arm', 'Arm',
    'Knee', 'Knee', 'Knee', 'Knee']

scaleNames = {
    'Nybble': RegularScaleNames,
    'Bittle': RegularScaleNames,
    'BittleX+Arm': BittleRScaleNames,
    'DoF16': RegularScaleNames,
    'Chero': RegularScaleNames
}

sideNames = ['Left Front', 'Right Front', 'Right Back', 'Left Back']

ports = []

def displayName(name):
    if 'Bittle' in name and 'Bittle' != name:
        s = name.replace(' ','')
        name = 'Bittle'+' '+s[6:]
    return name

def makeDirectory(path):
    # delete spaces in the path string
    path = path.strip()
    # delete the '\' at the end of path string
    path = path.rstrip("\\").rstrip("/")
    # path = path.rstrip("/")
	
    # check whether the path exists
    isExists = os.path.exists(path)
    
    if not isExists:
        # Create the directory if it does not exist
        os.makedirs(path)
        print(path + ' creat successfully')
        return True
    else:
        # If the directory exists, it will not be created and prompt that the directory already exists.
        print(path + ' already exists')
        return False

if platform.system() == "Windows":    # for Windows
    separation = '\\'
    homeDri = os.getenv('HOMEDRIVE') 
    homePath = os.getenv('HomePath') 
    configDir = homeDri + homePath
else:  # for Linux & macOS
    separation = '/'
    home = os.getenv('HOME') 
    configDir = home 
configDir = configDir + separation +'.config' + separation +'Petoi'
makeDirectory(configDir)
defaultConfPath = configDir + separation + 'defaultConfig.txt'
print(defaultConfPath)

def saveConfigToFile(configuration, filename):
        # 读取现有内容
        lines = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception as e:
                print(f'* Error reading config file: {e}')

        # 确保现有的每一行都以换行符结尾（修复文件格式问题）
        for i in range(len(lines)):
            if not lines[i].endswith('\n'):
                lines[i] += '\n'
        
        # 确保至少有10行
        while len(lines) < 10:
            lines.append('\n')
        
        # 更新界面中的相关配置信息
        for i in range(len(configuration)):
            lines[i] = configuration[i] + '\n'
        
        # 写回文件
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        except Exception as e:
            print(f'* Error writing config file: {e}')

def createImage(frame, imgFile, imgW):
    if not config.SHOW_GUI:
        raise ImportError("GUI libraries (tkinter/PIL) are required for createImage function")
    img = Image.open(imgFile)
    ratio = img.size[0] / imgW
    img = img.resize((imgW, round(img.size[1] / ratio)))
    image = ImageTk.PhotoImage(img)
    imageFrame = Label(frame, image=image)
    imageFrame.image = image
    return imageFrame

def tip(item, note):
    if supportHoverTip:
        Hovertip(item,note)
#    else:
#        print(note)
