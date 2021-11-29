from singleton_decorator import singleton
from PyQt5 import QtMultimedia as qtm
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from pydub import AudioSegment
from pydub import utils as AudioUtils
import wave


@singleton
class SignalsStore(qtw.QWidget):
    newSignalAdded = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._audioSegments = {}

    def addSignal(self, signal):
        if isinstance(signal, tuple):
            name, path = signal
            segment = AudioSegment.from_wav(path)
            self._audioSegments[name] = segment
            self.newSignalAdded.emit(name)
            return len(self._audioSegments) - 1

    def getSignal(self, name):
        return self._audioSegments.get(name)

    def getSampleRate(self, name):
        segment = self._audioSegments.get(name)
        return segment.frame_rate

    def getAudioSegment(self, name):
        return self._audioSegments.get(name)

    def getChunks(self, name, chunksize=1024):
        segment = self._audioSegments.get(name)
        sample_rate = segment.frame_rate
        chunk_time = int(1000.0*chunksize/sample_rate)
        chunks = AudioUtils.make_chunks(segment, chunk_length=chunk_time)
        return chunks

    def getChunkTime(self, name, chunksize=1024):
        segment = self._audioSegments.get(name)
        sample_rate = segment.frame_rate
        chunk_time = int(1000.0*chunksize/sample_rate)
        return chunk_time

    def getBigChunks(self, name):
        segment = self._audioSegments.get(name)
        chunks = AudioUtils.make_chunks(segment, chunk_length=2000)
        return chunks

    def getNumSignals(self):
        return len(self._audioSegments)

    def getSignalsNames(self):
        return [channel[0] for channel in self._audioSegments]

    def getWave(self, name):
        path = self.getSignal(name)[0]
        return wave.open(path, 'rb')

    def getMedia(self, name):
        path = self.getSignal(name)[0]
        return qtm.QMediaContent(qtc.QUrl.fromLocalFile(path))
