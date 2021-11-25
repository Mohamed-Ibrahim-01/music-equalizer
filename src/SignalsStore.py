from singleton_decorator import singleton
from PyQt5 import QtMultimedia as qtm
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from scipy.io import wavfile
import io

@singleton
class SignalsStore:
    def __init__(self):
        self._signals = {}

    def addSignal(self, signal):
        if isinstance(signal, tuple):
            name, path, data = signal
            self._signals[name] = (path, data)
            return len(self._signals)-1

    def getSignal(self, name):
        return self._signals.get(name)

    def getNumSignals(self):
        return len(self._signals)

    def getSignalsNames(self):
        return [channel[0] for channel in self._signals]

    def getMedia(self, name):
        path = self.getSignal(name)[0]
        return qtm.QMediaContent(qtc.QUrl.fromLocalFile(path))
