import numpy as np
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
        self.player.played.connect(lambda msg: self.play(msg))
        self.player.paused.connect(self.pause)
        self.player.stopped.connect(self.stop)

        # self.equalizer.changed.connect(self.update)
        self.loaded_songs.song_selected.connect(lambda name: self.changeSong(name))
        self.stream.audioEnded.connect(self.endAudio)
        self.timer.timeout.connect(self.updateSong)

    def endAudio(self, msg):
        self.state = "stopped"
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

        self.stream.start()
        self.timer.start(self.timeout)
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

    def updateSong(self):
        chunk_arr, chunk_segment = self.stream.getChunk()
        processed_segment = scipy_effects.eq(chunk_segment, 5000, bandwidth=1000, gain_dB=-20, order=8)
        processed_segment = scipy_effects.eq(processed_segment, 10000, bandwidth=1000, gain_dB=20, order=8)
        processed_segment = scipy_effects.eq(processed_segment, 15000, bandwidth=1000, gain_dB=-20, order=8)
        chunk_arr = np.array(processed_segment.get_array_of_samples())
        self.viewer.update_chunk(chunk_arr)
        self.spectrogram.update_chunk(chunk_arr)

        self.player.update_chunk(chunk_segment)

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
