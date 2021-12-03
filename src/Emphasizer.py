from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import uic
import qtawesome as qta


def addIcon(name, icon, layout):
    icon = qta.IconWidget(icon, color='white')
    icon.setSizePolicy(qtw.QSizePolicy.Policy.Maximum, qtw.QSizePolicy.Policy.Maximum)
    icon.setIconSize(qtc.QSize(32, 32))
    icon.setToolTip(name)
    icon.update()
    layout.addWidget(icon)


class Emphasizer(qtw.QWidget):
    changed = qtc.pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/emphasizer.ui", self)

        self.sliders = {"Piano": [self.piano_slider, "mdi.piano", self.piano_icon, 0],
                        "Piccolo": [self.piccolo_slider, "ph.magic-wand-thin", self.piccolo_icon, 0],
                        "Snare": [self.snare_slider, "fa5s.drum", self.snare_icon, 0]}

        for slider_name in self.sliders.keys():
            slider = self.sliders[slider_name]
            addIcon(slider_name, slider[1], slider[2])

        self.sliders["Piano"][0].sliderReleased.connect(lambda: self.emphasize(self.sliders["Piano"][0].value(), "Piano"))
        self.sliders["Snare"][0].sliderReleased.connect(lambda: self.emphasize(self.sliders["Snare"][0].value(), "Snare"))
        self.sliders["Piccolo"][0].sliderReleased.connect(lambda: self.emphasize(self.sliders["Piccolo"][0].value(), "Piccolo"))

    def emphasize(self, value, slider_name):
        slider = self.sliders[slider_name]
        slider[3] = value
        self.changed.emit(self.getSlidersGains())

    def getSlidersGains(self):
        gains = {}
        for slider_name in self.sliders.keys():
            gain = self.sliders[slider_name][3]
            gains[slider_name] = gain
        return gains
