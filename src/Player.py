import matplotlib.pyplot as plt
import sounddevice as sd
from enum import Enum
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtMultimedia as qtm
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import uic
from SignalsStore import SignalsStore

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

        self.button_play.clicked.connect(lambda : self.played.emit("played"))
        self.button_stop.clicked.connect(self.stop)
        self.button_pause.clicked.connect(self.pause)

        self.signals_store = SignalsStore()

    def play(self):
        pass

    def stop(self):
        pass

    def pause(self):
        pass

    def update(self):
        pass
