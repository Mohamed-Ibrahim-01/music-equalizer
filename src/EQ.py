import numpy as np
import io
import scipy.io.wavfile
from loguru import logger
from Player import Player
from Viewer import Viewer
from Spectrogram import Spectrogram
from pydub import AudioSegment

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import uic
from SignalsStore import SignalsStore
from SoundList import SoundList
from AudioStream import AudioStream
from Emphasizer import Emphasizer


class EQ(qtw.QWidget):
    stateChanged = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/EQ.ui", self)

        self.chunk_size = 1024
        self.curr_song = None
        self.curr_song_samplerate = 44100
        self.curr_song_sample_width = 2
        self.curr_song_channels = 1

        self.curr_volume_gain = 0
        self.sliders_gains = {"Snare": 0, "Piano": 0, "Piccolo": 0}

        self.stream = AudioStream()
        self.sound_store = SignalsStore()

        self.loaded_songs = SoundList()
        self.spectrogram = Spectrogram()
        self.player = Player(self.loaded_songs)
        self.viewer = Viewer(chunk_size=self.chunk_size)
        self.emphasizer = Emphasizer()

        self.timer = qtc.QTimer()
        self.timeout = int(1000*self.chunk_size / self.curr_song_samplerate)

        self.state = "stopped"

        self.initBody()
        self.initActions()

    def initActions(self):
        self.player.played.connect(self.play)
        self.player.stopped.connect(self.stop)

        self.loaded_songs.song_selected.connect(self.changeSong)
        self.loaded_songs.volumeChanged.connect(self.updateVolume)
        self.stream.audioEnded.connect(self.endAudio)
        self.emphasizer.changed.connect(self.updateFrequencies)

        self.timer.timeout.connect(self.updateSong)

    def updateFrequencies(self, sliders_gains):
        self.sliders_gains = sliders_gains

    def updateVolume(self, volume_gain):
        self.curr_volume_gain = volume_gain

    def endAudio(self, msg):
        self.state = "stopped"
        self.timer.stop()
        self.spectrogram.stop()
        logger.info("Audio ended")

    def initBody(self):
        self.viewer_layout.addWidget(self.viewer)
        self.specgram_layout.addWidget(self.spectrogram)
        self.player_layout.addWidget(self.player)
        self.emphasizer_layout.addWidget(self.emphasizer)
        self.loaded_songs_layout.addWidget(self.loaded_songs)

    def play(self):
        self.stream = AudioStream()
        self.stream.setSong(self.curr_song)
        self.timer.start(self.timeout)
        self.spectrogram.start()
        self.player.start()

        self.state = "playing"
        self.stateChanged.emit("Playing music...")

    def stop(self):
        self.stream.stop()
        self.timer.stop()
        self.spectrogram.stop()

        self.state = "stopped"
        self.stateChanged.emit("Music stopped...")

    def changeVolume(self, segment):
        gain = self.curr_volume_gain
        chunk_segment = segment.apply_gain(gain)
        chunk_arr = np.array(chunk_segment.get_array_of_samples())

        return chunk_arr, chunk_segment

    def updateSong(self):
        if self.state == "stopped":
            self.timer.stop()
            return
        stream_chunk = self.stream.getChunk()
        if stream_chunk is None:
            self.timer.stop()
            return

        processed_arr, processed_segment = self.processChunk(stream_chunk)

        self.viewer.update_chunk(processed_arr)
        if self.player.radioButton.isChecked():
            self.spectrogram.update_chunk(processed_arr)
        else: self.player.update_chunk(processed_segment)


    def equalize(self, signal, fs, limits, gain):
        min_freq, max_freq = limits
        signal_fft = np.fft.rfft(signal)
        freq_range = np.fft.rfftfreq(len(signal), 1 / fs)

        to_equalize_range = (freq_range > min_freq) & (freq_range < max_freq)
        signal_fft[to_equalize_range] *= 1.3**(gain) if gain > -8 else 0

        equalized = np.fft.irfft(signal_fft)
        equalized = np.asanyarray(equalized, dtype=np.int16)

        equalized_segment = self.writeSegment(equalized, fs)

        return equalized, equalized_segment

    def writeSegment(self, chunk_arr, sample_rate):
        wav_io = io.BytesIO()
        scipy.io.wavfile.write(wav_io, sample_rate, chunk_arr)
        wav_io.seek(0)
        segment = AudioSegment.from_wav(wav_io)
        return segment

    def processChunk(self, stream_chunk):
        _, chunk_segment = stream_chunk
        processed_arr, processed_segment = self.changeVolume(chunk_segment)

        equalizing_dict = {
            "Snare": (0, 1100),
            "Piano": (1200, 2700),
            "Piccolo": (2750, 20000)
        }

        for instrument in equalizing_dict:
            gain = self.sliders_gains[instrument]
            processed_arr, processed_segment = self.equalize(processed_arr, 44100, equalizing_dict[instrument], gain)

        return processed_arr, processed_segment

    def addNewSong(self, name):
        self.loaded_songs.addNewSong(name)

    def changeSong(self, name):
        seg = self.sound_store.getAudioSegment(name)
        chunk_time = self.sound_store.getChunkTime(name, self.chunk_size)
        self.curr_song_samplerate = seg.frame_rate
        self.curr_song_sample_width = seg.sample_width
        self.curr_song_channels = seg.channels
        self.curr_song = name
        self.player.setCurrSong(name, seg.frame_rate, seg.channels, chunk_time)
