import numpy as np
import time
from Player import Player
from Viewer import Viewer
from Spectrogram import Spectrogram
from Equalizer import Equalizer
from pydub import scipy_effects

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import uic
from SignalsStore import SignalsStore
from SoundList import SoundList
from AudioStream import AudioStream
from lauda import stopwatch


class EQ(qtw.QWidget):
    stateChanged = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/EQ.ui", self)

        self.sound_store = SignalsStore()
        self.loaded_songs = SoundList()
        self.spectrogram = Spectrogram()
        self.stream = AudioStream()
        self.player = Player()
        self.viewer = Viewer()
        self.equalizer = Equalizer()
        self.timer = qtc.QTimer()

        self.state = "stopped"

        self.curr_song = None
        self.chunk_size = 1024
        self.curr_song_samplerate = 44100
        self.curr_song_sample_width = 2
        self.curr_song_channels = 1

        self.timeout = int(1000*self.chunk_size / self.curr_song_samplerate)

        self.initBody()
        self.initActions()

    def initActions(self):
        self.player.played.connect(self.play)
        self.player.paused.connect(self.pause)
        self.player.stopped.connect(self.stop)

        # self.equalizer.changed.connect(self.update)
        self.loaded_songs.song_selected.connect(self.changeSong)
        self.stream.audioEnded.connect(self.endAudio)
        self.timer.timeout.connect(self.updateSong)

    def endAudio(self, msg):
        self.state = "stopped"
        self.timer.stop()
        self.player.stop()
        print("audio ended")

    def initBody(self):
        self.viewer_layout.addWidget(self.viewer)
        self.specgram_layout.addWidget(self.spectrogram)
        self.player_layout.addWidget(self.player)
        self.equalizer_layout.addWidget(self.equalizer)
        self.loaded_songs_layout.addWidget(self.loaded_songs)

    def play(self, msg):
        if self.loaded_songs.songsNum() < 1 or self.state == "playing":
            return
        if self.state == "stopped":
            print(self.curr_song)
            self.stream.setSong(self.curr_song)

        self.timer.start(self.timeout)
        self.spectrogram.start()
        self.stateChanged.emit("Playing music...")
        self.state = "playing"

    def pause(self):
        self.stream.stop()
        self.timer.stop()
        self.state = "paused"
        self.stateChanged.emit("Music paused...")

    def stop(self):
        self.timer.stop()
        self.stream.stop()
        self.player.stop()
        self.spectrogram.clear()
        self.state = "stopped"
        self.stateChanged.emit("Music stopped...")

    @stopwatch
    def updateSong(self):
        stream_chunk = self.stream.getChunk()
        if stream_chunk is None:
            self.timer.stop()
            return
        chunk_arr, chunk_segment = stream_chunk
        processed_segment = scipy_effects.eq(
            chunk_segment, 5000, bandwidth=1000, gain_dB=10, order=8
        )
        chunk_arr = np.array(processed_segment.get_array_of_samples())
        self.player.update_chunk(chunk_segment)
        self.viewer.update_chunk(chunk_arr)
        self.spectrogram.update_chunk(chunk_arr)

    def addNewSong(self, name):
        self.loaded_songs.addNewSong(name)

    def changeSong(self, name):
        seg = self.sound_store.getAudioSegment(name)
        chunk_time = self.sound_store.getChunkTime(name)
        self.curr_song_samplerate = seg.frame_rate
        self.curr_song_sample_width = seg.sample_width
        self.curr_song_channels = seg.channels
        self.curr_song = name
        self.player.setCurrSong(name, seg.frame_rate, seg.channels, len(seg), chunk_time)
