from loguru import logger
from PyQt5 import uic
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from SignalsStore import SignalsStore
import sounddevice as sd
from pydub import AudioSegment, utils
import threading
logger.add("src/logs/file_{time}.log")


class Player(qtw.QWidget):
    played = qtc.pyqtSignal(str)
    paused = qtc.pyqtSignal(str)
    stopped = qtc.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.radioButton = parent.findChild(qtw.QRadioButton, "radioButton")
        self.button_play = parent.findChild(qtw.QPushButton, "button_play")
        self.button_stop = parent.findChild(qtw.QPushButton, "button_stop")

        self.button_play.setIcon(self.style().standardIcon(qtw.QStyle.StandardPixmap.SP_MediaPlay))
        self.button_stop.setIcon(self.style().standardIcon(qtw.QStyle.StandardPixmap.SP_MediaStop))

        self.curr_song = ""
        self.samplerate = 44100
        self.channels = 1
        self.chunk_time = 23

        self.signals_store = SignalsStore()
        self.song_segments = []
        self.song_segments.append(AudioSegment.silent(duration=23))

        self._player = AudioPlayer(chunks=self.song_segments)
        self.playing_thread = qtc.QThread(parent=self)
        self.state = "stopped"

        self._player.ended.connect(self.stop_handler)
        self.button_play.clicked.connect(self.play_handler)
        self.button_stop.clicked.connect(self.stop_handler)

    def play_handler(self):
        logger.debug("Sound Played")
        logger.info(f"Sound Sample rate is {self.samplerate}")
        self.played.emit("played")
        self.state = "playing"

    def stop_handler(self):
        logger.debug("Sound Stopped")
        self._player.stop()
        self.playing_thread.quit()
        self.playing_thread.wait()
        self.song_segments = [AudioSegment.silent(duration=23)]
        self._player.chunks = self.song_segments
        self.stopped.emit("stopped")
        self.state = "stopped"

    def start(self):
        self._player.start()
        self.playing_thread.started.connect(self._player.play)
        self._player.moveToThread(self.playing_thread)
        self.playing_thread.start()

    def setCurrSong(self, song_name, samplerate, channels, chunk_time):
        self.samplerate = samplerate
        self.channels = channels
        self.curr_song = song_name
        self.chunk_time = chunk_time
        self._player.setAudio(samplerate, channels)

    def update_chunk(self, segment):
        self.song_segments.append(segment)


class AudioPlayer(qtc.QObject):
    ended = qtc.pyqtSignal(str)

    def __init__(self, chunks):
        super().__init__()
        self.stopped = True
        self.chunks = chunks
        self.curr_chunk = 0
        self.samplerate = 44100
        self.channels = 1
        self.chunk_time = 23

    def setAudio(self, samplerate, channels):
        logger.debug(f"New sound selected")
        self.curr_chunk = 0
        self.samplerate = samplerate
        self.channels = channels

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
        event = threading.Event()
        def __callback(outdata, frames, time, status):
            logger.debug("Still Calling")
            if self.stopped:
                logger.debug("Player has stopped")
                self.ended.emit("ended")
                raise sd.CallbackAbort()

            if self.curr_chunk == len(self.chunks):
                logger.debug("No chunks available")
                #self.ended.emit("ended")
                raise sd.CallbackAbort()

            chunk_data = self.chunks[self.curr_chunk]
            raw_data = self._resize(outdata, chunk_data)
            outdata[:] = raw_data
            self.curr_chunk += 1

        with sd.RawOutputStream(channels=self.channels,
                                dtype='int16',
                                callback=__callback,
                                blocksize=int(samplerate * chunk_time / 1000),
                                latency=False,
                                dither_off=False,
                                finished_callback=event.set):
            event.wait()
            logger.debug("Released")

    @qtc.pyqtSlot()
    def play(self):
        self._play(self.samplerate, self.chunk_time)

    @qtc.pyqtSlot()
    def stop(self):
        self.stopped = True
        self.curr_chunk = 0

    def start(self):
        self.stopped = False
