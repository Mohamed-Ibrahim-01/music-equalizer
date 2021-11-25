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

    class Error(Enum):
        none = qtm.QMediaPlayer.Error.NoError
        unsupported_format = qtm.QMediaPlayer.Error.FormatError
        access_denied = qtm.QMediaPlayer.Error.AccessDeniedError


    played = qtc.pyqtSignal(str)
    paused = qtc.pyqtSignal(str)
    stopped = qtc.pyqtSignal(str)
    error_occurred = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/player.ui", self)
        self.button_pause.setIcon(self.style().standardIcon(qtw.QStyle.StandardPixmap.SP_MediaPause))
        self.button_play.setIcon(self.style().standardIcon(qtw.QStyle.StandardPixmap.SP_MediaPlay))
        self.button_stop.setIcon(self.style().standardIcon(qtw.QStyle.StandardPixmap.SP_MediaStop))

        self.button_play.clicked.connect(self.play)
        self.button_stop.clicked.connect(self.stop)
        self.button_pause.clicked.connect(self.pause)

        self.signals_store = SignalsStore()
        self._player = qtm.QMediaPlayer()
        self._player.stateChanged.connect(self._state_changed)
        self._player.mediaStatusChanged.connect(self._media_status_changed)


    def play(self):
        if not self._player.isAudioAvailable():
            self._player.setMedia(self.signals_store.getMedia("strings_trompet"))
        self._player.play()
        self.played.emit("played")

    def stop(self):
        self._player.stop()
        self.stopped.emit("stopped")

    def pause(self):
        self._player.pause()
        self.paused.emit("closed")

    def _media_status_changed(self, state):
        if state == qtm.QMediaPlayer.MediaStatus.BufferedMedia:
            self._error = qtm.QMediaPlayer.Error.NoError
            print("HEllO ")
            #self.playing.emit(self._playlist[0])
        elif state == qtm.QMediaPlayer.MediaStatus.InvalidMedia:
            self._error = qtm.QMediaPlayer.Error.FormatError
            print("invalid media buffer input")

    @property
    def error(self):
        return qtm.QMediaPlayer.Error(self._player.error() or self._error)

    def _state_changed(self, state):
        if state == qtm.QMediaPlayer.State.StoppedState :
            print("stopped")
        elif state == qtm.QMediaPlayer.State.PlayingState:
            print("playing")
        elif state == qtm.QMediaPlayer.State.PausedState:
            print("paused")
