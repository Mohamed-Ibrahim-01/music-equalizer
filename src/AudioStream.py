from pydub import AudioSegment
from SignalsStore import SignalsStore
from PyQt5 import QtCore as qtc
import pyaudio
import numpy as np
import threading
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
import atexit
from collections import deque


class AudioStream(qtw.QWidget):
    audioEnded = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.sound_store = SignalsStore()
        self.frames = deque(maxlen=5)

        self.chunks = []
        self.bigChunks = []
        self.chunksize = 0
        self.sample_rate = 0
        self.curr_chunk = 0
        self.stream = None
        self.song = None

        # self.stream_timer = qtc.QTimer()
        # self.stream_timer.timeout.connect(self.new_chunk)
        # self.stream_timeout = 0

    def setSong(self, song_name, chunksize=1024):
        self.song = self.sound_store.getAudioSegment(song_name)
        self.chunks = self.sound_store.getChunks(song_name)
        self.chunksize = chunksize
        self.sample_rate = self.song.frame_rate
        # self.stream_timeout = int(1000*self.chunksize / self.sample_rate)

    def setChunks(self, chunks):
        self.chunks = chunks

    def new_chunk(self):
        if self.curr_chunk == len(self.chunks):
            self.audioEnded.emit("ended")
            self.stop()
            return
        data = np.array(self.chunks[self.curr_chunk].get_array_of_samples())
        self.frames.append(data)
        self.curr_chunk += 1

    def getChunk(self):
        self.new_chunk()
        return self.frames[-1], self.chunks[self.curr_chunk]

    def getBigChunk(self):
        print(self.curr_chunk)
        return self.bigChunks[self.curr_chunk]

    def start(self):
        pass
        # self.stream_timer.start(self.stream_timeout)

    def stop(self):
        self.curr_chunk = 0
        self.stream_timer.stop()
