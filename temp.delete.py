# NOTE: Creating my own tool as MonkeyRunner provides approx. 4 fps in others experiments
from threading import Thread
import subprocess as sp 
import array
import numpy as np 
import cv2

# SAMPLE COMMAND
# adb shell screenrecord --bit-rate=16m --output-format=h264 --size 540x960 - | ffplay -framerate 60 -probesize 32 -sync video -
class Android(Thread):    
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.fps = 0.0
        self.screen = np.zeros((3,3))
        self.screen_shape = (1075, 2215)
        adbCmd = ['adb', 'exec-out', 'screenrecord', '--output-format=h264', '--bit-rate=16m', '-']#  '--size 540x960',
        stream = sp.Popen(adbCmd, stdout = sp.PIPE)
        
        ffmpegCmd =['ffmpeg', '-i', '-',
        '-f', 'rawvideo', '-vf', 'scale=324:576',
        '-framerate','60',
        '-vcodec', 'bmp',  '-']
        self.__ffmpeg = sp.Popen(ffmpegCmd, stdin = stream.stdout, stdout = sp.PIPE)
        # TODO: Remove Time Limit --time-limit 
        self.start()
    def touch(self, pos):
        # SAMPLE: adb shell input tap 500 500
        # NOTE: pos are passed in as percentages of x,y 
        x = int((self.screen_shape[0]/100)*pos[0])
        y = int((self.screen_shape[1]/100)*pos[1])
        touchCmd = ["adb", "exec-out", "input", "tap", x, y]
        sp.Popen(touchCmd,shell=True)
        #sp.call(,shell=True)
        pass
    def swipe(self,start_pos,end_pos):
        # NOTE: start_pos are passed in as percentages of x,y 
        x1 = int((self.screen_shape[0]/100)*start_pos[0])
        y1 = int((self.screen_shape[1]/100)*start_pos[1])
        # NOTE: end_pos are passed in as percentages of x,y 
        x2 = int((self.screen_shape[0]/100)*end_pos[0])
        y2 = int((self.screen_shape[1]/100)*end_pos[1])
        sp.call(["adb", "shell", "input", "touchscreen", "swipe", x1, y1, x2, y2], shell=True)

    def read_screen(self):
        # Reads in latest frame to 'screen' variable
        fileSizeBytes = self.__ffmpeg.stdout.read(6)
        fileSize = 0
        for i in range(4):
            fileSize += array.array('B',fileSizeBytes[i + 2])[0] * 256 ** i
        bmpData = fileSizeBytes + self.__ffmpeg.stdout.read(fileSize - 6)
        
        self.screen = cv2.imdecode(np.fromstring(bmpData, dtype = np.uint8), 1)
    def run(self):
        while True:
            self.read_screen()
if __name__ == "__main__":
    droid = Android()
    try:
        while True:
            cv2.imshow("Phone Screen",droid.screen) 
            if cv2.waitKey(0) & 0xFF == ord('q'):
                droid.touch((50,50))
    except:
        pass
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