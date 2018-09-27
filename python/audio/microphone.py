import time
import numpy as np
import pyaudio
from settings import config

import threading

class AudioInputProcess(threading.Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None):
        super(AudioInputProcess, self).__init__(group=group, target=target,
                                              name=name, args=args)
        self._stop_event = threading.Event()
        self.kwargs = kwargs
        self.args=args
        return

    def stop(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stop_event.set()

    def run(self):
        callback = self.args[0]
        selected_device = None
        update = lambda *args: None
        try:
            selected_device = self.args[1]
            update =self.args[2]
        except:            
            selected_device = None
        p = pyaudio.PyAudio()
        frames_per_buffer = int(config.MIC_RATE / config.FPS)
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=config.MIC_RATE,
                        input=True,
                        frames_per_buffer=frames_per_buffer, 
                        input_device_index=selected_device)
        overflows = 0
        prev_ovf_time = time.time()
        while not self._stop_event.is_set():
            try:
                y = np.fromstring(stream.read(
                    frames_per_buffer), dtype=np.int16)
                y = y.astype(np.float32)
                callback(y)                
                update()
            except IOError:
                overflows += 1
                if time.time() > prev_ovf_time + 1:
                    prev_ovf_time = time.time()
                    print('Audio buffer has overflowed {} times'.format(overflows))
        stream.stop_stream()
        stream.close()
        p.terminate()

