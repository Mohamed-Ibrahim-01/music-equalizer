from Player import Player
from Viewer import Viewer
from Spectrogram import Spectrogram
from Equalizer import Equalizer

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import uic
from SignalsStore import SignalsStore


class EQ(qtw.QWidget):
    stateChanged = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/EQ.ui", self)

        self.sound_store = SignalsStore()
        self.timer = qtc.QTimer()
        self.player = Player()
        self.viewer = Viewer()
        self.spectrogram = Spectrogram()
        self.equalizer = Equalizer()
        self.dx = 0.03
        self.pos = 0

        self.initBody()
        self.initActions()

    def initActions(self):
        self.player.played.connect(self.play)
        self.player.paused.connect(self.pause)
        self.player.stopped.connect(self.stop)
        self.equalizer.changed.connect(self.update)

    def initBody(self):
        self.viewer_layout.addWidget(self.viewer)
        self.specgram_layout.addWidget(self.spectrogram)
        self.player_layout.addWidget(self.player)
        self.equalizer_layout.addWidget(self.equalizer)

    def play(self):
        self.viewer.play()
        # self.specgram.play()
        self.stateChanged.emit("Playing music...")

    def pause(self):
        # self.viewer.pause()
        # self.specgram.pause()
        self.stateChanged.emit("Music paused...")

    def stop(self):
        # self.viewer.pause()
        # self.specgram.pause()
        self.stateChanged.emit("Music stopped...")
