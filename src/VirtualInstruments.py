import numpy as np
import matplotlib as plt
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import uic
from Piano import Keyboard
from Guitar import Guitar
import qtawesome as qta

class QIconClickable(qta.IconWidget):
    clicked = qtc.pyqtSignal(str)
    def __init__(self,name, icon, color="white"):
        super().__init__(icon, color=color)
        self.name = name

    def mousePressEvent(self, event):
            self.clicked.emit(self.name)

class VirtualInstruments(qtw.QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/instruments.ui", self)
        self.instruments_stack = qtw.QStackedWidget()
        self.loaded_instrument_layout.addWidget(self.instruments_stack)


        piano = Keyboard()
        guitar = Guitar()
        drum = None

        self.instruments= {
            "Piano":("mdi.piano", piano, 0),
            "Guitar":("fa5s.guitar", guitar, 1),
            "Drum":("fa5s.drum", drum, 2)
        }
        self.initInstrumnets()

    def initInstrumnets(self):
        for inst_name in self.instruments.keys():
            inst_icon = QIconClickable(inst_name, self.instruments[inst_name][0], color='white')
            inst_icon.setSizePolicy(qtw.QSizePolicy.Policy.Maximum, qtw.QSizePolicy.Policy.Maximum)
            inst_icon.setIconSize(qtc.QSize(64, 64))
            inst_icon.setToolTip(inst_name)
            inst_icon.update()
            self.instruments_icons_layout.addWidget(inst_icon)
            if self.instruments[inst_name][1] :
                self.instruments_stack.addWidget(self.instruments[inst_name][1])
            inst_icon.clicked.connect(
                lambda name:
                    self.instruments_stack.setCurrentIndex(self.instruments[name][2])
            )


