# NOTE: Creating my own tool as MonkeyRunner provides approx. 4 fps in others experiments
from threading import Thread
import subprocess as sp 
import array
import numpy as np 
from PIL import ImageGrab

import winGuiAuto
import win32gui
import win32con
import win32api 
from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect
import cv2

# SAMPLE COMMAND
# adb shell screenrecord --bit-rate=16m --output-format=h264 --size 540x960 - | ffplay -framerate 60 -probesize 32 -sync video -
class Android(Thread):    
    #TODO: Add proper kill function 
    def __init__(self,debug = False):
        Thread.__init__(self)
        self.debug = debug 
        self.daemon = True
        self.fps = 0.0
        self.kill = False
        self.screen = np.zeros((3,3))
        self.screen_shape = (1075, 2215) # Add Code to get from phone 
        if (not debug):
            self._start_pipe()
        else:
            pass
	    # NOTE: Limit is unknown
        # TODO: Remove Time Limit --time-limit 
        self.start()
    def _start_pipe(self):
        adbCmd = ['adb', 'exec-out', 'screenrecord', '--output-format=h264',  '-']
	    #  '--size 540x960', '--bit-rate=16m',
        stream = sp.Popen(adbCmd, stdout = sp.PIPE)#,shell=True)
        
        ffmpegCmd =['ffmpeg', '-i', '-',
        '-f', 'rawvideo', '-vf', 'scale=324:576',
        '-framerate','60',
        '-vcodec', 'bmp',  '-']
        self.__ffmpeg = sp.Popen(ffmpegCmd, stdin = stream.stdout, stdout = sp.PIPE)#,shell=True)
    def __adb_touch(self, pos):
        # SAMPLE: adb shell input tap 500 500
        # NOTE: pos are passed in as percentages of x,y 
        x = int((self.screen_shape[0]/100)*pos[0])
        y = int((self.screen_shape[1]/100)*pos[1])
        touchCmd = ["adb", "exec-out", "input", "tap", x, y]
        sp.Popen(touchCmd,shell=True)
        #sp.call(,shell=True)
    def __mouse_touch(self,pos):
        x1, y1, x2, y2 = GetWindowRect(self.window)
        self.screen_shape = (x2-x1,y1-y2)
        # NOTE: pos is passed in as percentages of x,y 
        X1 = int((self.screen_shape[0]/100)*pos[0])
        Y1 = int((self.screen_shape[1]/100)*pos[1])
        x , y = (x2 - X1,y1-Y1)
        win32api.SetCursorPos((x2 - X1,y1-Y1))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
        pass
    def touch(self,pos):
        if self.debug:
            self.__mouse_touch(pos)
        else:
            self.__adb_touch(pos)
        pass
    def __adb_swipe(self,start_pos,end_pos):
        # NOTE: start_pos are passed in as percentages of x,y 
        x1 = int((self.screen_shape[0]/100)*start_pos[0])
        y1 = int((self.screen_shape[1]/100)*start_pos[1])
        # NOTE: end_pos are passed in as percentages of x,y 
        x2 = int((self.screen_shape[0]/100)*end_pos[0])
        y2 = int((self.screen_shape[1]/100)*end_pos[1])
        sp.call(["adb", "shell", "input", "touchscreen", "swipe", x1, y1, x2, y2], shell=True)

    def read_adb_screen(self):
        # TODO: Add Stack Overflow Link
        # Reads in latest frame to 'screen' variable
        try:
                fileSizeBytes = self.__ffmpeg.stdout.read(6)
                fileSize = 0
                for i in range(4):
                    fileSize += array.array('B',fileSizeBytes[i + 2])[0] * 256 ** i
                bmpData = fileSizeBytes + self.__ffmpeg.stdout.read(fileSize - 6)
                self.screen = cv2.imdecode(np.fromstring(bmpData, dtype = np.uint8), 1)
        except Exception as e:
            print(e)
            print("Screen Capture Failed")
            self.kill = True
            #self.screen = np.zeros((500,500))
    def read_local_screen(self):
        self.window = winGuiAuto.findTopWindow("NoxPlayer")
        win32gui.SetWindowPos(self.window, win32con.HWND_TOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        rect = win32gui.GetWindowPlacement(self.window)[-1]
        self.screen = np.array(ImageGrab.grab(rect))
        
        pass
    def run(self):	
        while True:
            if self.kill == True:
                break
            if self.debug:
                self.read_local_screen()
            else:
                self.read_adb_screen()
if __name__ == "__main__":
    from time import sleep
    droid = Android(debug=True)
    try:
        for _ in range(1000):#while True:
            cv2.imshow("Phone Screen",droid.screen)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                droid.touch((60,60))
            sleep(.02)
    except:
        exit()
## Capture
# adb exec-out screenrecord --bit-rate=16m --output-format=h264 --size 800x600 - |
# adb shell screenrecord --bit-rate=16m --output-format=h264 --size 540x960 - |
## Play
# ffplay -
# ffplay -framerate 60 -probesize 32 -sync video -
# ffplay -framerate 60 -framedrop -bufsize 16M -
# vlc --demux h264 --h264-fps=60 --clock-jitter=0 -
# mplayer -demuxer h264es -
# mplayer -framedrop -fps 6000 -cache 512 -demuxer h264es -
