from __future__ import division, print_function

import time

import numpy as np
from scipy.ndimage.filters import gaussian_filter1d

import led
from audio import dsp, microphone
from settings import config
from visualizer.effects import energy, scroll, spectrum

_time_prev = time.time() * 1000.0
"""The previous time that the frames_per_second() function was called"""

_fps = dsp.ExpFilter(val=config.FPS, alpha_decay=0.2, alpha_rise=0.2)
"""The low-pass filter used to estimate frames-per-second"""


def frames_per_second():
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
    global _time_prev, _fps
    time_now = time.time() * 1000.0
    dt = time_now - _time_prev
    _time_prev = time_now
    if dt == 0.0:
        return _fps.value
    return _fps.update(1000.0 / dt)


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


def microphone_update(audio_samples):
    global y_roll, prev_rms, prev_exp, prev_fps_update
    # Normalize samples between 0 and 1
    y = audio_samples / 2.0**15
    # Construct a rolling window of audio samples
    y_roll[:-1] = y_roll[1:]
    y_roll[-1, :] = np.copy(y)
    y_data = np.concatenate(y_roll, axis=0).astype(np.float32)

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
        y_data *= fft_window
        y_padded = np.pad(y_data, (0, N_zeros), mode='constant')
        YS = np.abs(np.fft.rfft(y_padded)[:N // 2])
        # Construct a Mel filterbank from the FFT data
        mel = np.atleast_2d(YS).T * dsp.mel_y.T
        # Scale data to values more suitable for visualization
        # mel = np.sum(mel, axis=0)
        mel = np.sum(mel, axis=0)
        mel = mel**2.0
        # Gain normalization
        mel_gain.update(np.max(gaussian_filter1d(mel, sigma=1.0)))
        mel /= mel_gain.value
        mel = mel_smoothing.update(mel)
        # Map filterbank output onto LED strip
        output = visualization_effect(mel)
        led.pixels = output
        led.update()
        if config.USE_GUI:
            # Plot filterbank output
            x = np.linspace(config.MIN_FREQUENCY,
                            config.MAX_FREQUENCY, len(mel))
            mel_curve.setData(x=x, y=fft_plot_filter.update(mel))
            # Plot the color channels
            r_curve.setData(y=led.pixels[0])
            g_curve.setData(y=led.pixels[1])
            b_curve.setData(y=led.pixels[2])
    if config.USE_GUI:
        app.processEvents()

    if config.DISPLAY_FPS:
        fps = frames_per_second()
        if time.time() - 0.5 > prev_fps_update:
            prev_fps_update = time.time()
            print('FPS {:.0f} / {:.0f}'.format(fps, config.FPS))


# Number of audio samples to read every time frame
samples_per_frame = int(config.MIC_RATE / config.FPS)

# Array containing the rolling audio sample window
y_roll = np.random.rand(config.N_ROLLING_HISTORY, samples_per_frame) / 1e16

visualization_effect = spectrum
"""Visualization effect to display on the LED strip"""


def run_gui():
    import pyqtgraph as pg
    from pyqtgraph.Qt import QtGui, QtCore
    # Mel filterbank plot
    fft_plot = layout.addPlot(title='Filterbank Output', colspan=3)
    fft_plot.setRange(yRange=[-0.1, 1.2])
    fft_plot.disableAutoRange(axis=pg.ViewBox.YAxis)
    x_data = np.array(range(1, config.N_FFT_BINS + 1))
    mel_curve = pg.PlotCurveItem()
    mel_curve.setData(x=x_data, y=x_data*0)
    fft_plot.addItem(mel_curve)
    # Visualization plot
    layout.nextRow()
    led_plot = layout.addPlot(title='Visualization Output', colspan=3)
    led_plot.setRange(yRange=[-5, 260])
    led_plot.disableAutoRange(axis=pg.ViewBox.YAxis)
    # Pen for each of the color channel curves
    r_pen = pg.mkPen((255, 30, 30, 200), width=4)
    g_pen = pg.mkPen((30, 255, 30, 200), width=4)
    b_pen = pg.mkPen((30, 30, 255, 200), width=4)
    # Color channel curves
    r_curve = pg.PlotCurveItem(pen=r_pen)
    g_curve = pg.PlotCurveItem(pen=g_pen)
    b_curve = pg.PlotCurveItem(pen=b_pen)
    # Define x data
    x_data = np.array(range(1, config.N_PIXELS + 1))
    r_curve.setData(x=x_data, y=x_data*0)
    g_curve.setData(x=x_data, y=x_data*0)
    b_curve.setData(x=x_data, y=x_data*0)
    # Add curves to plot
    led_plot.addItem(r_curve)
    led_plot.addItem(g_curve)
    led_plot.addItem(b_curve)
    # Frequency range label
    freq_label = pg.LabelItem('')
    # Frequency slider

    def freq_slider_change(tick):
        minf = freq_slider.tickValue(0)**2.0 * (config.MIC_RATE / 2.0)
        maxf = freq_slider.tickValue(1)**2.0 * (config.MIC_RATE / 2.0)
        t = 'Frequency range: {:.0f} - {:.0f} Hz'.format(minf, maxf)
        freq_label.setText(t)
        config.MIN_FREQUENCY = minf
        config.MAX_FREQUENCY = maxf
        dsp.create_mel_bank()
    freq_slider = pg.TickSliderItem(orientation='bottom', allowAdd=False)
    freq_slider.addTick((config.MIN_FREQUENCY / (config.MIC_RATE / 2.0))**0.5)
    freq_slider.addTick((config.MAX_FREQUENCY / (config.MIC_RATE / 2.0))**0.5)
    freq_slider.tickMoveFinished = freq_slider_change
    freq_label.setText('Frequency range: {} - {} Hz'.format(
        config.MIN_FREQUENCY,
        config.MAX_FREQUENCY))
    # Effect selection
    active_color = '#16dbeb'
    inactive_color = '#FFFFFF'

    def energy_click(x):
        global visualization_effect
        visualization_effect = energy
        energy_label.setText('Energy', color=active_color)
        scroll_label.setText('Scroll', color=inactive_color)
        spectrum_label.setText('Spectrum', color=inactive_color)

    def scroll_click(x):
        global visualization_effect
        visualization_effect = scroll
        energy_label.setText('Energy', color=inactive_color)
        scroll_label.setText('Scroll', color=active_color)
        spectrum_label.setText('Spectrum', color=inactive_color)

    def spectrum_click(x):
        global visualization_effect
        visualization_effect = spectrum
        energy_label.setText('Energy', color=inactive_color)
        scroll_label.setText('Scroll', color=inactive_color)
        spectrum_label.setText('Spectrum', color=active_color)
    # Create effect "buttons" (labels with click event)
    energy_label = pg.LabelItem('Energy')
    scroll_label = pg.LabelItem('Scroll')
    spectrum_label = pg.LabelItem('Spectrum')
    energy_label.mousePressEvent = energy_click
    scroll_label.mousePressEvent = scroll_click
    spectrum_label.mousePressEvent = spectrum_click
    energy_click(0)
    # Layout
    layout.nextRow()
    layout.addItem(freq_label, colspan=3)
    layout.nextRow()
    layout.addItem(freq_slider, colspan=3)
    layout.nextRow()
    layout.addItem(energy_label)
    layout.addItem(scroll_label)
    layout.addItem(spectrum_label)
    run()


def run():
    # Initialize LEDs
    led.update()
    # Start listening to live audio stream
    microphone.start_stream(microphone_update)
