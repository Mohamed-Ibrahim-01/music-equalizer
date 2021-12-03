import numpy as np
from PyQt5 import QtWidgets, uic
import sounddevice as sd
from PyQt5 import QtWidgets as qtw


class Drums(qtw.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('src/ui/bongos.ui', self)

        self.left_drum = self.findChild(QtWidgets.QPushButton, 'left')  # Find the button
        self.right_drum = self.findChild(QtWidgets.QPushButton, 'right')  # Find the button

        self.bongos_buttons = [self.left_drum, self.right_drum]
        self.frequency_tons = {"1": 40, "2": 40}
        self.bongos_func = [lambda: self.play(self.frequency_tons["1"]),
                            lambda: self.play(self.frequency_tons["2"])]

        for i in range(len(self.bongos_buttons)):
            self.bongos_buttons[i].clicked.connect(self.bongos_func[i])

        self.show()

    def karplus_strong_drum(self, wavetable, n_samples, prob):
        samples = []
        current_sample = 0
        previous_value = 0
        while len(samples) < n_samples:
            r = np.random.binomial(1, prob)
            sign = float(r == 1) * 2 - 1
            wavetable[current_sample] = sign * 0.5 * (wavetable[current_sample] + previous_value)
            samples.append(wavetable[current_sample])
            previous_value = samples[-1]
            current_sample += 1
            current_sample = current_sample % wavetable.size
        return np.array(samples)

    def play(self, freq):
        fs = 8000
        wavetable_size = fs // freq
        wavetable = np.ones(wavetable_size)

        sample = self.karplus_strong_drum(wavetable, 1 * fs, 0.3)
        sd.play(sample, fs)
