import  numpy as np
from Player import Player
from Viewer import Viewer
from Spectrogram import Spectrogram
from Equalizer import Equalizer

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import uic
from SignalsStore import SignalsStore
from SoundList import SoundList


class EQ(qtw.QWidget):
    stateChanged = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/EQ.ui", self)

        self.sound_store = SignalsStore()
        self.loaded_songs = SoundList()
        self.spectrogram = Spectrogram()
        self.player = Player()
        self.viewer = Viewer()
        self.equalizer = Equalizer()
        self.timer = qtc.QTimer()

        self.state = "stopped"
        self.curr_song = None
        self.chunk_size = 1024
        self.curr_song_samplerate = 44100
        self.song_chunks = []
        self.curr_chunk = 0
        self.timeout = self.chunk_size / self.curr_song_samplerate

        self.initBody()
        self.initActions()

    def initActions(self):
        self.player.played.connect(lambda msg: self.play(msg))
        self.player.paused.connect(self.pause)
        self.player.stopped.connect(self.stop)

        # self.equalizer.changed.connect(self.update)
        self.loaded_songs.song_selected.connect(lambda name: self.changeSongName(name))

    def initBody(self):
        self.viewer_layout.addWidget(self.viewer)
        self.specgram_layout.addWidget(self.spectrogram)
        self.player_layout.addWidget(self.player)
        self.equalizer_layout.addWidget(self.equalizer)
        self.loaded_songs_layout.addWidget(self.loaded_songs)

    def play(self, msg):
        print(msg)
        if self.loaded_songs.songsNum() < 1 or self.state == "playing":
            return
        if self.state == "stopped":
            self.song_chunks = self.sound_store.getChunks(self.curr_song)
            self.curr_song_samplerate = self.sound_store.getSampleRate(self.curr_song)

        self.timer.timeout.connect(self.updateSong)
        self.timer.start(self.timeout)
        self.stateChanged.emit("Playing music...")
        self.state = "playing"

    def pause(self):
        self.timer.stop()
        self.stateChanged.emit("Music paused...")

    def stop(self):
        self.timer.stop()
        self.viewer.clear()
        self.spectrogram.clear()
        self.curr_chunk = 0
        self.stateChanged.emit("Music stopped...")

    def updateSong(self):
        #chunk = self.stream.getChunk()
        chunk = self.song_chunks[self.curr_chunk].get_array_of_samples()
        chunk = np.array(chunk)
        self.curr_chunk += 1
        self.viewer.update(chunk)
        # self.player.update(chunk)
        # self.spectrogram.update(chunk)

    def addNewSong(self, name):
        self.loaded_songs.addNewSong(name)

    def changeSongName(self, name):
        self.curr_song = name
