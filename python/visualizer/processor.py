from __future__ import division, print_function

import time

import numpy as np
from scipy.ndimage.filters import gaussian_filter1d

from output import led
from audio import dsp, microphone
from settings import config
from visualizer.effects import spectrum


class Processor():
    _time_prev = time.time() * 1000.0
    """The previous time that the frames_per_second() function was called"""

    _fps = dsp.ExpFilter(val=config.FPS, alpha_decay=0.2, alpha_rise=0.2)
    """The low-pass filter used to estimate frames-per-second"""

    # Number of audio samples to read every time frame
    samples_per_frame = int(config.MIC_RATE / config.FPS)

    # Array containing the rolling audio sample window
    y_roll = np.random.rand(config.N_ROLLING_HISTORY, samples_per_frame) / 1e16

    fft_plot_filter = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                                    alpha_decay=0.5, alpha_rise=0.99)
    mel_gain = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                             alpha_decay=0.01, alpha_rise=0.99)
    mel_smoothing = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                                  alpha_decay=0.5, alpha_rise=0.99)
    volume = dsp.ExpFilter(config.MIN_VOLUME_THRESHOLD,
                           alpha_decay=0.02, alpha_rise=0.02)
    fft_window = np.hamming(int(config.MIC_RATE / config.FPS)
                            * config.N_ROLLING_HISTORY)
    prev_fps_update = time.time()


    def __init__(self, parent):
        self.parent = parent
        self.visualization_effect = self.parent.visualization_effect

    def frames_per_second(self):
        """Return the estimated frames per second

        Returns the current estimate for frames-per-second (FPS).
        FPS is estimated by measured the amount of time that has elapsed since
        this function was previously called. The FPS estimate is low-pass filtered
        to reduce noise.

        This function is intended to be called one time for every iteration of
        the program's main loop.

        Returns
        -------
        fps : float
            Estimated frames-per-second. This value is low-pass filtered
            to reduce noise.
        """
        time_now = time.time() * 1000.0
        dt = time_now - self._time_prev
        self._time_prev = time_now
        if dt == 0.0:
            return self._fps.value
        return self._fps.update(1000.0 / dt)



    def __call__(self, audio_samples):
        self.visualization_effect = self.parent.visualization_effect
        # Normalize samples between 0 and 1
        y = audio_samples / 2.0**15
        # Construct a rolling window of audio samples
        self.y_roll[:-1] = self.y_roll[1:]
        self.y_roll[-1, :] = np.copy(y)
        y_data = np.concatenate(self.y_roll, axis=0).astype(np.float32)

        vol = np.max(np.abs(y_data))
        if vol < config.MIN_VOLUME_THRESHOLD:
            print('No audio input. Volume below threshold. Volume:', vol)
            led.pixels = np.tile(0, (3, config.N_PIXELS))
            led.update()
        else:
            # Transform audio input into the frequency domain
            N = len(y_data)
            N_zeros = 2**int(np.ceil(np.log2(N))) - N
            # Pad with zeros until the next power of two
            y_data *= self.fft_window
            y_padded = np.pad(y_data, (0, N_zeros), mode='constant')
            YS = np.abs(np.fft.rfft(y_padded)[:N // 2])
            # Construct a Mel filterbank from the FFT data
            mel = np.atleast_2d(YS).T * dsp.mel_y.T
            # Scale data to values more suitable for visualization
            # mel = np.sum(mel, axis=0)
            mel = np.sum(mel, axis=0)
            mel = mel**2.0
            # Gain normalization
            self.mel_gain.update(np.max(gaussian_filter1d(mel, sigma=1.0)))
            mel /= self.mel_gain.value
            mel = self.mel_smoothing.update(mel)
            # Map filterbank output onto LED strip
            output = self.visualization_effect(mel) 
            led.pixels = output
            led.update()
            if config.USE_GUI:
                # Plot filterbank output
                x = np.linspace(config.MIN_FREQUENCY,
                                config.MAX_FREQUENCY, len(mel))
                self.parent.mel_curve.setData(x=x, y=self.fft_plot_filter.update(mel))
                # Plot the color channels
                self.parent.r_curve.setData(y=led.pixels[0])
                self.parent.g_curve.setData(y=led.pixels[1])
                self.parent.b_curve.setData(y=led.pixels[2])
        if config.DISPLAY_FPS:
            fps = self.frames_per_second()
            if time.time() - 0.5 > self.prev_fps_update:
                self.prev_fps_update = time.time()
                print('FPS {:.0f} / {:.0f}'.format(fps, config.FPS))
