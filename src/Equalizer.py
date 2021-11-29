from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import uic
import qtawesome as qta


class Equalizer(qtw.QWidget):
    changed = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/equalizer.ui", self)

        low_freq_icon_set = {"Piano": "mdi.piano",
                             "Electric Instruments": "mdi.guitar-electric",
                             "Violin": "mdi.violin",
                             "Male Voice": "mdi6.face-man-outline"
                             }

        mid_freq_icon_set = {"Guitar": "fa5s.guitar",
                             "Trumpet": "mdi.trumpet",
                             "SaxPhone": "mdi.saxophone",
                             "Female Voice": "mdi.face-woman-outline"
                             }

        high_freq_icon_set = {"Piano": "mdi.piano",
                              "Electric Instruments": "mdi.guitar-electric",
                              "Flute": "ph.magic-wand-thin",
                              }

        self.icons_group = (self.low_freq_icons, self.mid_freq_icons, self.high_freq_icons)
        self.icons = (low_freq_icon_set, mid_freq_icon_set, high_freq_icon_set)

        for (icon_group, icons_set) in zip(self.icons_group, self.icons):
            for icon_name in icons_set.keys():
                icon = qta.IconWidget(icons_set[icon_name], color='white')
                icon.setSizePolicy(qtw.QSizePolicy.Policy.Maximum, qtw.QSizePolicy.Policy.Maximum)
                icon.setIconSize(qtc.QSize(32, 32))
                icon.setToolTip(icon_name)
                icon.update()
                icon_group.addWidget(icon)
