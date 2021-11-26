import pyqtgraph as pg
import numpy as np


class Viewer(pg.PlotWidget):
    def __init__(self, sr=44100, chunk_size=1024, color=(255, 127, 0)):
        super().__init__()
        self.sr = sr
        self.chunk_size = chunk_size

        self.audio = []
        self.time = np.arange(int(int(1000*chunk_size/self.sr)*self.sr/1000)) / self.sr

        self.pen = pg.mkPen(color=color)
        self.showGrid(x=True, y=True)
        self.setLabel('left', "Song", units='A.U.')
        self.setLabel('bottom', "Time", units='s')
        self.setYRange(-2 ** 15, 2 ** 15 - 1)
        self.setXRange(self.time.min(), self.time.max())
        self.enableAutoRange('xy', False)
        self.curve = self.plot(pen=self.pen)


    def updateGraph(self):
        print("--------------------------------------")
        print(len(self.audio), len(self.time))
        print(self.audio[0], len(self.time))
        print("--------------------------------------")
        self.curve.setData(x=self.time, y=np.float32(self.audio))

    def update(self, chunk):
        self.audio = chunk
        self.updateGraph()

    def clear(self):
        self.graph.clear()
