from PyQt5 import uic
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from SignalsStore import SignalsStore
from pydub import AudioSegment
from collections import deque
import sounddevice as sd
from pydub import AudioSegment, utils
import threading


class Player(qtw.QWidget):
    played = qtc.pyqtSignal(str)
    paused = qtc.pyqtSignal(str)
    stopped = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/player.ui", self)
        self.button_pause.setIcon(self.style().standardIcon(qtw.QStyle.StandardPixmap.SP_MediaPause))
        self.button_play.setIcon(self.style().standardIcon(qtw.QStyle.StandardPixmap.SP_MediaPlay))
        self.button_stop.setIcon(self.style().standardIcon(qtw.QStyle.StandardPixmap.SP_MediaStop))

        self.button_play.clicked.connect(lambda: self.played.emit("played"))
        self.button_stop.clicked.connect(lambda: self.stopped.emit("stopped"))
        self.button_pause.clicked.connect(lambda: self.stopped.emit("stopped"))

        self.curr_song = ""
        self.samplerate = 44100
        self.channels = 1
        self.chunk_time = 23
        self.song_duration = 50000  # 50 sec

        self.signals_store = SignalsStore()
        self.song_segments = []
        self.song_segments.append(AudioSegment.silent(duration=23))

        self._player = AudioPlayer(chunks=self.song_segments)
        self.state = "stopped"

    def setCurrSong(self, song_name, samplerate, channels, duration, chunk_time):
        self.samplerate = samplerate
        self.channels = channels
        self.song_duration = duration
        self.curr_song = song_name
        self.chunk_time = chunk_time
        self._player.setAudio(samplerate, channels, duration)

    def update_chunk(self, segment):
        self.song_segments.append(segment)
        if self.state != "playing":
            self._player.play()
            self.state = "playing"

    def play(self):
        self.played.emit("played")

    def stop(self):
        self._player.stop()
        self.played.emit("stopped")
        self.state = "stopped"

    def pause(self):
        self._player.stop()
        self.played.emit("paused")
        self.state = "paused"


class AudioPlayer:
    def __init__(self, chunks):
        self.stopped = True
        self.chunks = chunks
        self.curr_chunk = 0
        self.samplerate = 44100
        self.channels = 1
        self.chunk_time = 23
        self.song_duration = 50000

    def setAudio(self, samplerate, channels, duration):
        self.curr_chunk = 0
        self.samplerate = samplerate
        self.channels = channels
        self.song_duration = duration

    def _resize(self, outdata, chunk_data):
        diff = len(outdata) - len(chunk_data.raw_data)
        if diff == 0:
            return chunk_data.raw_data
        if diff < 0:
            return chunk_data.raw_data[:len(outdata)]
        else:
            diff_duration = int(diff * 1100 / self.samplerate)
            silent = AudioSegment.silent(duration=diff_duration, frame_rate=self.samplerate)
            chunk_data = chunk_data.append(silent, crossfade=0)
            return chunk_data.raw_data[:len(outdata)]

    def _play(self, samplerate, chunk_time):
        def __callback(indata, outdata, frames, time, status):
            print("I'm here th call back")
            chunk_data = self.chunks[self.curr_chunk]
            print(len(chunk_data))
            raw_data = self._resize(outdata, chunk_data)
            outdata[:] = raw_data
            self.curr_chunk += 1
            if self.stopped:
                print("TRYYYYYYYYYYYYy")
                raise sd.CallbackStop()
            if self.curr_chunk == len(self.chunks):
                raise sd.CallbackStop()

        with sd.RawStream(channels=self.channels,
                          dtype='int16',
                          callback=__callback,
                          blocksize=int(samplerate * chunk_time / 1000),
                          dither_off=True):

            print("Hey i'm sleeping here")
            sd.sleep(self.song_duration * 1000)

    def play(self):
        self.stopped = False
        print("Hey Another world starts from here")
        playing_thread = threading.Thread(target=self._play, args=(self.samplerate, self.chunk_time))
        try:
            playing_thread.start()
        finally:
            print("Done")

    def stop(self):
        self.stopped = True
