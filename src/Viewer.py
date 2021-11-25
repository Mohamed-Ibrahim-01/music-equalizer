import pyqtgraph as pg
import numpy as np
from SignalsStore import SignalsStore

class Viewer(pg.PlotWidget):
    def __init__(self,color=(255, 127, 0)):
        super().__init__()
        self.pen = pg.mkPen(color=color)
        self.signals_store = SignalsStore()


    def loadData(self, audio, fs, time):
        self.audio = audio
        self.fs = fs
        self.time = time

    def plotGraph(self):
        self.plot( self.time, np.float32(self.audio), pen=self.pen)
        self.plotItem.setLimits(
            xMin=min(self.time),
            xMax=max(self.time),
            yMin=min(self.audio),
            yMax=max(self.audio)
        )
        self.curser = pg.mkPen(width=4, color='b')
        self.zero_marker = pg.InfiniteLine(angle=90, movable=False, pen=self.curser)
        self.addItem(self.zero_marker, ignoreBounds=True)

    def play(self):
        _, (audio, fs) = self.signals_store.getSignal("strings_trompet")
        time = np.linspace(0, len(audio) / fs, num=len(audio))
        self.loadData(audio, fs, time)
        self.plotGraph()


