import time

import librosa
import pyqtgraph as pg
import matplotlib.pyplot as plt
import numpy as np
import threading
from collections import deque
from PyQt5 import QtCore as qtc
from lauda import stopwatch
from thread_decorator import threaded


def generatePgColormap(cm_name):
    colormap = plt.get_cmap(cm_name)
    colormap._init()
    lut = (colormap._lut * 255).view(np.ndarray)
    return lut


CHUNKSIZE = 512
SAMPLE_RATE = 44100
TIME_VECTOR = np.arange(CHUNKSIZE) / SAMPLE_RATE
N_FFT = 4096
FREQ_VECTOR = np.fft.rfftfreq(N_FFT, d=TIME_VECTOR[1] - TIME_VECTOR[0])
WATERFALL_FRAMES = int(1000 * 1024 // N_FFT)


class Spectrogram(pg.PlotWidget):
    dataChanged = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.spectrogram_data = deque(maxlen=WATERFALL_FRAMES)
        self.spectrogram_chunks = deque(maxlen=WATERFALL_FRAMES)
        self.lut = generatePgColormap('plasma')
        self.setLabel('left', "Frequency", units='Hz')
        self.setLabel('bottom', "Time", units='s')
        self.setXRange(0, WATERFALL_FRAMES * TIME_VECTOR.max())

        self.spectrogram_image = pg.ImageItem()
        self.spectrogram_image.setLookupTable(self.lut)
        self.spectrogram_image.scale(CHUNKSIZE / SAMPLE_RATE, FREQ_VECTOR.max() * 2. / N_FFT)
        self.addItem(self.spectrogram_image)

        self.timeout = int(1000*CHUNKSIZE / SAMPLE_RATE)
        self.plotting_timer = qtc.QTimer()
        self.spectrogram_processing = qtc.QTimer()

        self.spectrogram_processing.timeout.connect(self.compute_spectrogram)
        self.plotting_timer.timeout.connect(self.update_image)

    @stopwatch
    def update_image(self):
        arr = np.c_[self.spectrogram_data]
        if arr.size > 0:
            if arr.ndim == 1:
                arr = arr[:, np.newaxis]
            max_value = arr.max()
            min_value = max_value / 10
            self.spectrogram_image.setImage(arr, levels=(min_value, max_value))

    def compute_spectrogram(self):
        data = np.zeros((CHUNKSIZE,), dtype=int) if not self.spectrogram_chunks else self.spectrogram_chunks.pop()
        if len(data) > 0 and data.max() > 1:
            stft = np.abs(np.fft.rfft(np.hanning(data.size) * data, n=N_FFT))
            self.spectrogram_data.append(np.log10(stft + 1e-12))

    @stopwatch
    def update_chunk(self, chunk_samples):
        self.spectrogram_chunks.append(chunk_samples)

    def start(self):
        self.spectrogram_processing.start(self.timeout)
        self.plotting_timer.start(2*self.timeout)

    def clear(self):
        pass
