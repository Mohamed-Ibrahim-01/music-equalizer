import pyqtgraph as pg
import matplotlib.pyplot as plt
import numpy as np
from collections import deque


def generatePgColormap(cm_name):
    colormap = plt.get_cmap(cm_name)
    colormap._init()
    lut = (colormap._lut * 255).view(np.ndarray)
    return lut


CHUNKSIZE = 1024
SAMPLE_RATE = 44100
TIME_VECTOR = np.arange(CHUNKSIZE) / SAMPLE_RATE
N_FFT = 4096
FREQ_VECTOR = np.fft.rfftfreq(N_FFT, d=TIME_VECTOR[1] - TIME_VECTOR[0])
WATERFALL_FRAMES = int(1000 * 2048 // N_FFT)


class Spectrogram(pg.PlotWidget):
    def __init__(self):
        super().__init__()
        self.spectrogram_data = deque(maxlen=WATERFALL_FRAMES)
        self.lut = generatePgColormap('plasma')
        self.setLabel('left', "Frequency", units='Hz')
        self.setLabel('bottom', "Time", units='s')
        self.setXRange(0, WATERFALL_FRAMES * TIME_VECTOR.max())

        self.spectrogram_image = pg.ImageItem()
        self.spectrogram_image.setLookupTable(self.lut)
        self.spectrogram_image.scale(CHUNKSIZE / SAMPLE_RATE, FREQ_VECTOR.max() * 2. / N_FFT)
        self.addItem(self.spectrogram_image)

    def update_image(self):
        arr = np.c_[self.spectrogram_data]
        if arr.size > 0:
            if arr.ndim == 1:
                arr = arr[:, np.newaxis]
            max_value = arr.max()
            min_value = max_value / 10
            self.spectrogram_image.setImage(arr, levels=(min_value, max_value))

    def update_chunk(self, chunk_samples):
        data = chunk_samples
        if len(data) > 0 and data.max() > 1:
            X = np.abs(np.fft.rfft(np.hanning(data.size) * data, n=N_FFT))
            self.spectrogram_data.append(np.log10(X + 1e-12))
        self.update_image()

    def clear(self):
        pass
