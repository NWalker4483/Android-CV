
from threading import Thread
import subprocess as sp 
import array
import numpy as np 
import cv2
# NOTE: Creating my own tool as MonkeyRunner provides approx. 4 fps in others experiments
class Android(Thread):    
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.fps = 0.0
        self.screen = np.zeros((3,3))
        
        #self.__reader = cap = cv2.VideoCapture('temp.h264')
        # TODO: Remove Time Limit --time-limit 
        "sudo apt-get install ffmpeg"
        # Capture
        "adb exec-out screenrecord --bit-rate=16m --output-format=h264 --size 800x600 - |"
        "adb shell screenrecord --bit-rate=16m --output-format=h264 --size 540x960 - |"
        # Play
        "ffplay -"
        "ffplay -framerate 60 -probesize 32 -sync video -"
        "ffplay -framerate 60 -framedrop -bufsize 16M -"
        "vlc --demux h264 --h264-fps=60 --clock-jitter=0 -"
        "mplayer -demuxer h264es -"
        "mplayer -framedrop -fps 6000 -cache 512 -demuxer h264es -"
        self.start()
    def touch(self, pos):
        # NOTE: pos are passed in as percentages of x,y 
        print(self.screen.shape)
        pass
    def swipe(self,start_pos,end_pos):
        "adb shell input touchscreen swipe 530 1420 530 1120"
        pass
    def get_screen(self):
        # Reads in latest frame to 'screen' variable
        #self.__reader.set(cv2.CAP_PROP_POS_FRAMES, self.__reader.get(cv2.CAP_PROP_FRAME_COUNT)-1)
        #self.screen = self.__reader.read()[1]
        pass
    def run(self):
        self.get_screen()
        pass
    def __delattr__(self, name):
        return super().__delattr__(name)
if __name__ == "__main__":
    adbCmd = ['adb', 'exec-out', 'screenrecord', '--output-format=h264', '-']
    stream = sp.Popen(adbCmd, stdout = sp.PIPE)

    ffmpegCmd =['ffmpeg', '-i', '-', '-f', 'rawvideo', '-vf', 'scale=324:576', 
    '-vcodec', 'bmp',  '-']
    ffmpeg = sp.Popen(ffmpegCmd, stdin = stream.stdout, stdout = sp.PIPE)

    while True:
        fileSizeBytes = ffmpeg.stdout.read(6)
        fileSize = 0
        for i in range(4):
            fileSize += array.array('B',fileSizeBytes[i + 2])[0] * 256 ** i
        bmpData = fileSizeBytes + ffmpeg.stdout.read(fileSize - 6)
        image = cv2.imdecode(np.fromstring(bmpData, dtype = np.uint8), 1)
        cv2.imshow("im",image) 
        cv2.waitKey(25)
