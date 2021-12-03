from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import uic
from VirtualInstruments import VirtualInstruments
from SignalsStore import SignalsStore
from EQ import EQ


class Page(qtw.QTabWidget):
    stateChanged = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/page.ui", self)
        self.setMinimumSize(1000, 500)

        self.curr_sound = None
        self.sound_store = SignalsStore()
        self.equalizer = EQ()
        self.instruments = VirtualInstruments()

        self.initBody()
        self.initActions()

    def initBody(self):
        eq_tab = self.findChild(qtw.QWidget, "EQ")
        eq_tab.layout().addWidget(self.equalizer)
        instruments_tab = self.findChild(qtw.QWidget, "virtualInstruments")
        instruments_tab.layout().addWidget(self.instruments)

    def initActions(self):
        self.equalizer.stateChanged.connect(
            lambda msg: self.stateChanged.emit(msg)
        )
        self.sound_store.newSignalAdded.connect(self.equalizer.addNewSong)
