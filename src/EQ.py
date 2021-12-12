import numpy as np
import time
from Player import Player
from Viewer import Viewer
from Spectrogram import Spectrogram
from pydub import scipy_effects

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import uic
from SignalsStore import SignalsStore
from SoundList import SoundList
from AudioStream import AudioStream
from lauda import stopwatch
from Emphasizer import Emphasizer


class EQ(qtw.QWidget):
    stateChanged = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/EQ.ui", self)

        self.chunk_size = 1024
        self.curr_song = None
        self.curr_song_samplerate = 44100
        self.curr_song_sample_width = 2
        self.curr_song_channels = 1
        self.curr_volume_gain = 0
        self.sliders_gains = {"Snare": 0, "Piano": 0, "Piccolo": 0}

        self.stream = AudioStream()
        self.sound_store = SignalsStore()

        self.loaded_songs = SoundList()
        self.spectrogram = Spectrogram()
        self.player = Player()
        self.viewer = Viewer(chunk_size=self.chunk_size)
        self.emphasizer = Emphasizer()

        self.timer = qtc.QTimer()
        self.timeout = int(1000*self.chunk_size / self.curr_song_samplerate)

        self.state = "stopped"

        self.initBody()
        self.initActions()

    def initActions(self):
        self.player.played.connect(self.play)
        self.player.stopped.connect(self.stop)

        self.loaded_songs.song_selected.connect(self.changeSong)
        self.stream.audioEnded.connect(self.endAudio)
        self.timer.timeout.connect(self.updateSong)
        self.loaded_songs.volumeChanged.connect(self.updateVolume)
        self.emphasizer.changed.connect(self.updateFrequencies)

    def updateFrequencies(self, sliders_gains):
        self.sliders_gains = sliders_gains

    def updateVolume(self, volume_gain):
        self.curr_volume_gain = volume_gain

    def endAudio(self, msg):
        self.state = "stopped"
        self.timer.stop()
        self.spectrogram.stop()
        print("audio ended")

    def initBody(self):
        self.viewer_layout.addWidget(self.viewer)
        self.specgram_layout.addWidget(self.spectrogram)
        self.player_layout.addWidget(self.player)
        self.emphasizer_layout.addWidget(self.emphasizer)
        self.loaded_songs_layout.addWidget(self.loaded_songs)

    def play(self, msg):
        self.stream.setSong(self.curr_song)
        self.timer.start(self.timeout)
        self.spectrogram.start()
        self.state = "playing"
        self.stateChanged.emit("Playing music...")

    def stop(self):
        self.timer.stop()
        self.stream.stop()
        self.spectrogram.stop()
        self.state = "stopped"
        self.stateChanged.emit("Music stopped...")

    def updateSong(self):
        if self.state == "stopped":
            self.timer.stop()
            return
        stream_chunk = self.stream.getChunk()
        if stream_chunk is None:
            self.timer.stop()
            return

        chunk_arr, chunk_segment = stream_chunk
        processed_segment = self.processChunk(chunk_segment)
        if self.curr_volume_gain != 0:
            processed_segment = processed_segment.apply_gain(self.curr_volume_gain)

        chunk_arr = np.array(processed_segment.get_array_of_samples())
        self.player.update_chunk(processed_segment)
        self.viewer.update_chunk(chunk_arr)
        if self.player.radioButton.isChecked():
            self.spectrogram.update_chunk(chunk_arr)

    def processChunk(self, chunk_segment):
        processed_segment = chunk_segment
        if self.sliders_gains["Snare"] != 0:
            processed_segment = scipy_effects.eq(
                chunk_segment, 1000, bandwidth=100, gain_dB=self.sliders_gains["Snare"], order=8
            )
        if self.sliders_gains["Piano"] != 0:
            processed_segment = scipy_effects.eq(
                processed_segment, 10000, bandwidth=2000, gain_dB=self.sliders_gains["Piano"], order=8
            )
        if self.sliders_gains["Piccolo"] != 0:
            processed_segment = scipy_effects.eq(
                processed_segment, 5000, bandwidth=1000, gain_dB=self.sliders_gains["Piccolo"], order=8
            )
        return processed_segment

    def addNewSong(self, name):
        self.loaded_songs.addNewSong(name)

    def changeSong(self, name):
        seg = self.sound_store.getAudioSegment(name)
        chunk_time = self.sound_store.getChunkTime(name, self.chunk_size)
        self.curr_song_samplerate = seg.frame_rate
        self.curr_song_sample_width = seg.sample_width
        self.curr_song_channels = seg.channels
        self.curr_song = name
        self.player.setCurrSong(name, seg.frame_rate, seg.channels, len(seg), chunk_time)
