from pydub import AudioSegment
from SignalsStore import SignalsStore
from PyQt5 import QtCore as qtc
import pyaudio
import numpy as np
import threading
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from collections import deque


class AudioStream(qtw.QWidget):
    audioEnded = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.sound_store = SignalsStore()
        self.frames = deque(maxlen=10)

        self.chunks = []
        self.chunksize = 0
        self.sample_rate = 0
        self.curr_chunk = 0
        self.song = None

    def setSong(self, song_name, chunksize=512):
        self.song = self.sound_store.getAudioSegment(song_name)
        self.chunks = self.sound_store.getChunks(song_name)
        self.chunksize = chunksize
        self.sample_rate = self.song.frame_rate

    def setChunks(self, chunks):
        self.chunks = chunks

    def _newChunk(self):
        if self.curr_chunk >= len(self.chunks)-1:
            self.stop()
            return False
        data = np.array(self.chunks[self.curr_chunk].get_array_of_samples())
        self.frames.append(data)
        self.curr_chunk += 1
        return True

    def getChunk(self):
        if self._newChunk():
            print(len(self.frames), self.curr_chunk, len(self.chunks))
            return self.frames[-1], self.chunks[self.curr_chunk]

    def stop(self):
        print("*****************************************ENDED***************************************")
        self.audioEnded.emit("ended")
        self.curr_chunk = 0
