from pydub import AudioSegment
import pyaudio
import numpy as np
import threading
import atexit
import wave


class AudioStream(object):

    def __init__(self, sound, sample_rate=44100, chunksize=1024):
        self.wf = wave.open('src/sine_sweep.wav', 'rb')
        self.sample_rate = sample_rate
        self.chunksize = chunksize
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                                  channels=self.wf.getnchannels(),
                                  rate=self.wf.getframerate(),
                                  input=True,
                                  frames_per_buffer=self.chunksize,
                                  stream_callback=self.new_frame)
        self.lock = threading.Lock()
        self.stop = False
        self.frames = []
        atexit.register(self.close)

    def new_frame(self, in_data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        data = np.frombuffer(data, 'int16')
        with self.lock:
            self.frames.append(data)
            if self.stop:
                return None, pyaudio.paComplete
        return None, pyaudio.paContinue

    def get_frames(self):
        with self.lock:
            frames = self.frames
            self.frames = []
            return frames

    def start(self):
        self.stream.start_stream()

    def close(self):
        with self.lock:
            self.stop = True
        self.stream.close()
        self.p.terminate()
