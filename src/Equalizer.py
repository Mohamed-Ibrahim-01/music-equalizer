import matplotlib.pyplot as plt
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import uic
import qtawesome as qta

class Equalizer(qtw.QWidget):
    changed = qtc.pyqtSignal(str)
    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/equalizer.ui", self)


        piano = qta.IconWidget('mdi.piano', color='white')
        piano.setSizePolicy(qtw.QSizePolicy.Policy.Maximum, qtw.QSizePolicy.Policy.Maximum)
        piano.setIconSize(qtc.QSize(32, 32))
        piano.setToolTip("piano")
        piano.update()

        guitar = qta.IconWidget('fa5s.guitar', color='white')
        guitar.setSizePolicy(qtw.QSizePolicy.Policy.Maximum, qtw.QSizePolicy.Policy.Maximum)
        guitar.setIconSize(qtc.QSize(32, 32))
        guitar.setToolTip("Guitar")
        guitar.update()

        low_freq_icons = {"Piano":"mdi.piano", "Guitar":"mdi.guitar", "Violin":"mdi.violin"}


        self.low_freq_icons.addWidget(piano)
        self.low_freq_icons.addWidget(guitar)
