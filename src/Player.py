
from loguru import logger
from PyQt5 import uic
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from SignalsStore import SignalsStore
import sounddevice as sd
from pydub import AudioSegment, utils
import threading
logger.add("file_{time}.log")


class Player(qtw.QWidget):
    played = qtc.pyqtSignal(str)
    paused = qtc.pyqtSignal(str)
    stopped = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        uic.loadUi("src/ui/player.ui", self)
        self.button_play.setIcon(self.style().standardIcon(qtw.QStyle.StandardPixmap.SP_MediaPlay))
        self.button_stop.setIcon(self.style().standardIcon(qtw.QStyle.StandardPixmap.SP_MediaStop))

        self.button_play.clicked.connect(self.play_handler)
        self.button_stop.clicked.connect(self.stop_handler)

        self.curr_song = ""
        self.samplerate = 44100
        self.channels = 1
        self.chunk_time = 23
        self.song_duration = 50000  # 50 sec

        self.signals_store = SignalsStore()
        self.song_segments = []
        self.song_segments.append(AudioSegment.silent(duration=23))

        self._player = AudioPlayer(chunks=self.song_segments)
        self.state = "stopped"

    def play_handler(self):
        logger.debug("Sound Played")
        logger.info(f"Sound Sample rate is {self.samplerate}")
        self.played.emit("played")
        self.state = "playing"
        self._player.start()
        self._player.play()

    def stop_handler(self):
        logger.debug("Sound Stopped")
        self.stopped.emit("stopped")
        self.state = "stopped"
        self._player.stop()
        self.song_segments = [AudioSegment.silent(duration=23)]
        self._player.chunks = self.song_segments
        print("stopped")

    def setCurrSong(self, song_name, samplerate, channels, duration, chunk_time):
        self.samplerate = samplerate
        self.channels = channels
        self.song_duration = duration
        self.curr_song = song_name
        self.chunk_time = chunk_time
        self._player.setAudio(samplerate, channels, duration)

    def update_chunk(self, segment):
        self.song_segments.append(segment)


class AudioPlayer:
    def __init__(self, chunks):
        self.stopped = True
        self.chunks = chunks
        self.curr_chunk = 0
        self.samplerate = 44100
        self.channels = 1
        self.chunk_time = 23
        self.song_duration = 50000
        self.playing_thread = threading.Thread(target=self._play, args=(self.samplerate, self.chunk_time))

    def setAudio(self, samplerate, channels, duration):
        logger.debug(f"New sound selected")
        self.curr_chunk = 0
        self.samplerate = samplerate
        self.channels = channels
        self.song_duration = duration

    def _resize(self, outdata, chunk_data):
        diff = len(outdata) - len(chunk_data.raw_data)
        if diff == 0:
            return chunk_data.raw_data
        if diff < 0:
            return chunk_data.raw_data[:len(outdata)]
        else:
            diff_duration = int(diff * 1100 / self.samplerate)
            silent = AudioSegment.silent(duration=diff_duration, frame_rate=self.samplerate)
            chunk_data = chunk_data.append(silent, crossfade=0)
            return chunk_data.raw_data[:len(outdata)]

    def _play(self, samplerate, chunk_time):
        def __callback(outdata, frames, time, status):
            if self.stopped:
                print("Player has stopped")
                raise sd.CallbackStop()

            if self.curr_chunk == len(self.chunks):
                print("No chunks available")
                raise sd.CallbackStop()

            chunk_data = self.chunks[self.curr_chunk]
            raw_data = self._resize(outdata, chunk_data)
            outdata[:] = raw_data
            self.curr_chunk += 1

        with sd.RawOutputStream(channels=self.channels,
                                dtype='int16',
                                callback=__callback,
                                blocksize=int(samplerate * chunk_time / 1000),
                                latency=False,
                                dither_off=False):

            sd.sleep(self.song_duration * 1000)

    def play(self):
        self.playing_thread = threading.Thread(target=self._play, args=(self.samplerate, self.chunk_time))
        try:
            self.playing_thread.daemon = True
            self.playing_thread.start()
        finally:
            print("Done")

    def stop(self):
        self.stopped = True
        self.curr_chunk = 0

    def start(self):
        self.stopped = False
