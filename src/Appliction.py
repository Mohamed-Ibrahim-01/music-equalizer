import sys
import random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import  Slider
import numpy as np
import pandas as pd
import pyqtgraph as pg
from scipy.io import wavfile

matplotlib.use('Qt5Agg')
from matplotlib.pyplot import isinteractive
from PyQt5 import QtCore, QtWidgets

import sounddevice as sd



class Main_window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        AudioName = "mixkit-guitar2338.wav"
        self.fs, Audiodata = wavfile.read(AudioName)
        if Audiodata.shape[1] == 2:
            self.audio = Audiodata[:, 0]
        else:
            self.audio = Audiodata

        self.time = np.linspace(0, len(self.audio) / self.fs, num=len(self.audio))

        self.dx = 0.03
        self.pos = 0

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = Main_window()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
