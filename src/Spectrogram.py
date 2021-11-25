from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
plt.style.use('dark_background')
class Spectrogram(FigureCanvas):
    def __init__(self, width=100, height=5):
        self.fig, self.ax = plt.subplots(
            figsize=(width, height), facecolor="#000000"
        )
        self.fig.set_tight_layout({"rect":(-0.01, -0.05, 1.01, 1.05)})
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['bottom'].set_color('#969696')
        self.ax.spines['left'].set_color('#969696')
        self.ax.tick_params(axis='x', colors='#969696')
        self.ax.tick_params(axis='y', colors='#969696')
        super().__init__(self.fig)

    def updateSpectogram(self, signal, palate, sampling_freq):
        self.ax.cla()
        specgram_image = self.ax.spectrogram(signal, Fs=sampling_freq, cmap=palate)[3]
        self.colorbar(specgram_image).set_label('Intensity [dB]')
        left, right = self.ax.get_xlim();
        self.ax.set_xlim(right=(right-left)/40)
        self.draw()
