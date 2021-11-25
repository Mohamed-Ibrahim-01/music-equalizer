import numpy as np
from PyQt5 import QtWidgets, uic
import sounddevice as sd
import sys

class Guitar(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('src/ui/guitar.ui', self)

        self.button_E1 = self.findChild(QtWidgets.QPushButton, 'E1') # Find the button
        self.button_A = self.findChild(QtWidgets.QPushButton, 'A') # Find the button
        self.button_D = self.findChild(QtWidgets.QPushButton, 'D') # Find the button
        self.button_G = self.findChild(QtWidgets.QPushButton, 'G') # Find the button
        self.button_B = self.findChild(QtWidgets.QPushButton, 'B') # Find the button
        self.button_E2 = self.findChild(QtWidgets.QPushButton, 'E2') # Find the button

        self.guitar_buttons = [self.button_E1,self.button_A,self.button_D,self.button_G,self.button_B,self.button_E2]
        self.frequincy_tons = {"E1":82,"A":110,"D":147 ,"G":196 ,"B":247 ,"E2":330 }
        self.guitar_func = [lambda :self.play(self.frequincy_tons["E1"]),lambda :self.play(self.frequincy_tons["A"]),
                            lambda :self.play(self.frequincy_tons["D"]),lambda :self.play(self.frequincy_tons["G"]),
                            lambda :self.play(self.frequincy_tons["B"]),lambda :self.play(self.frequincy_tons["E2"])]

        for i in range(len(self.guitar_buttons)):
            self.guitar_buttons[i].clicked.connect(self.guitar_func[i])


        # self.button_E1.clicked.connect(self.printButtonPressed) # Remember to pass the definition/method, not the return value!
        # self.button_A.clicked.connect(self.printButtonPressed)
        # self.button_D.clicked.connect(self.printButtonPressed)
        # self.button_G.clicked.connect(self.printButtonPressed)
        # self.button_B.clicked.connect(self.printButtonPressed)
        # self.button_E2.clicked.connect(self.printButtonPressed)


        self.frequincy_tons = {"E1":82,"A":110,"D":147 ,"G":196 ,"B":247 ,"E2":330 }

    def karplus_strong(self,wavetable, n_samples):
        """Synthesizes a new waveform from an existing wavetable, modifies last sample by averaging."""
        samples = []
        current_sample = 0
        previous_value = 0
        while len(samples) < n_samples:
            wavetable[current_sample] = 0.5 * (wavetable[current_sample] + previous_value)
            samples.append(wavetable[current_sample])
            previous_value = samples[-1]
            current_sample += 1
            current_sample = current_sample % wavetable.size
        return np.array(samples)

    def play(self,freq):
        fs = 30000
        wavetable_size = fs // freq

        wavetable = (2 * np.random.randint(0, 2, wavetable_size) - 1).astype(np.float64)
        sample1 = self.karplus_strong(wavetable, 2 * fs)
        sd.play(sample1, fs)
