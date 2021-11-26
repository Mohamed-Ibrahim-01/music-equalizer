from pydub import AudioSegment
from SignalsStore import SignalsStore
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
        self.audio = pyaudio.PyAudio()
        self.lock = threading.Lock()
        self.stream = None
        self.stop = False
        self.frames = deque(maxlen=5)
        self.chunks = []
        self.chunksize = 0
        self.song = None
        self.curr_chunk = 0
        # atexit.register(self.close)

    def setSong(self, song_name, chunksize=1024):
        self.song = self.sound_store.getAudioSegment(song_name)
        self.chunks = self.sound_store.getChunks(song_name)
        self.chunksize = chunksize

        self.stream = self.audio.open(format=self.audio.get_format_from_width(self.song.sample_width),
                                      channels=self.song.channels,
                                      rate=self.song.frame_rate,
                                      input=True,
                                      start=False,
                                      frames_per_buffer=self.chunksize,
                                      stream_callback=self.new_frame)

    def setChunks(self, chunks):
        self.chunks = chunks

    def new_frame(self, in_data, frame_count, time_info, status):
        try:
            if self.curr_chunk >= len(self.chunks):
                self.close()
                self.audioEnded.emit("Ended")
            data = np.array(self.chunks[self.curr_chunk].get_array_of_samples())
            self.curr_chunk += 1

            with self.lock:
                self.frames.append(data)
                if self.stop:
                    return None, pyaudio.paComplete
            return None, pyaudio.paContinue
        except:
            self.audioEnded.emit("Ended")

    def getChunk(self):
        with self.lock:
            return self.frames[-1]

    def start(self):
        self.stream.start_stream()

    def close(self):
        with self.lock:
            self.stop = True
        self.stream.close()
        self.audio.terminate()
