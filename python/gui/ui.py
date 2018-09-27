from __future__ import division, print_function

import time

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from scipy.ndimage.filters import gaussian_filter1d

from audio import dsp
from audio.microphone import AudioInputProcess
from gui.gui import Ui_MainWindow
from output import led
from settings import config
from visualizer.effects import energy, scroll, spectrum
from visualizer.processor import Processor
import pyaudio

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class UI(Ui_MainWindow):
    """This class extends the converted UI by all the needed functionalities and stuff.
    So the UI can be converted from Qt without editing that big-ass code
    """
    active_color = '#16dbeb'
    inactive_color = '#FFFFFF'
    visualization_effect = spectrum  # Visualization effect to display on the LED strip"""

    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.audio_processor = AudioInputProcess(
            args=(Processor(self), None, self.parent_app.processEvents))

    def setupUi(self, MainWindow):

        super().setupUi(MainWindow)
        ####
        self.visualizerGView = pg.GraphicsView(self.visualizerTab)
        self.visualizerGView.setObjectName(_fromUtf8("visualizerGView"))
        self.visualizerVLayout.addWidget(self.visualizerGView)
        self.layout = pg.GraphicsLayout(border=(100, 100, 100))
        self.visualizerGView.setCentralItem(self.layout)
        ####
        # Mel filterbank plot
        self.fft_plot = self.layout.addPlot(
            title='Filterbank Output', colspan=3)
        self.fft_plot.setRange(yRange=[-0.1, 1.2])
        self.fft_plot.disableAutoRange(axis=pg.ViewBox.YAxis)
        self.x_data = np.array(range(1, config.N_FFT_BINS + 1))
        self.mel_curve = pg.PlotCurveItem()
        self.mel_curve.setData(x=self.x_data, y=self.x_data*0)
        self.fft_plot.addItem(self.mel_curve)
        # Visualization plot
        self.layout.nextRow()
        self.led_plot = self.layout.addPlot(
            title='Visualization Output', colspan=3)
        self.led_plot.setRange(yRange=[-5, 260])
        self.led_plot.disableAutoRange(axis=pg.ViewBox.YAxis)
        # Pen for each of the color channel curves
        self.r_pen = pg.mkPen((255, 30, 30, 200), width=4)
        self.g_pen = pg.mkPen((30, 255, 30, 200), width=4)
        self.b_pen = pg.mkPen((30, 30, 255, 200), width=4)
        # Color channel curves
        self.r_curve = pg.PlotCurveItem(pen=self.r_pen)
        self.g_curve = pg.PlotCurveItem(pen=self.g_pen)
        self.b_curve = pg.PlotCurveItem(pen=self.b_pen)
        # Define x data
        self.x_data = np.array(range(1, config.N_PIXELS + 1))
        self.r_curve.setData(x=self.x_data, y=self.x_data*0)
        self.g_curve.setData(x=self.x_data, y=self.x_data*0)
        self.b_curve.setData(x=self.x_data, y=self.x_data*0)
        # Add curves to plot
        self.led_plot.addItem(self.r_curve)
        self.led_plot.addItem(self.g_curve)
        self.led_plot.addItem(self.b_curve)
        # Frequency range label
        self.freq_label = pg.LabelItem('')
        # Frequency slider
        self.freq_slider = pg.TickSliderItem(
            orientation='bottom', allowAdd=False)
        self.freq_slider.addTick(
            (config.MIN_FREQUENCY / (config.MIC_RATE / 2.0))**0.5)
        self.freq_slider.addTick(
            (config.MAX_FREQUENCY / (config.MIC_RATE / 2.0))**0.5)
        self.freq_slider.tickMoveFinished = self.freq_slider_change
        self.freq_label.setText('Frequency range: {} - {} Hz'.format(
            config.MIN_FREQUENCY,
            config.MAX_FREQUENCY))
        # Create effect "buttons" (labels with click event)
        self.energy_label = pg.LabelItem('Energy')
        self.scroll_label = pg.LabelItem('Scroll')
        self.spectrum_label = pg.LabelItem('Spectrum')
        self.energy_label.mousePressEvent = self.energy_click
        self.scroll_label.mousePressEvent = self.scroll_click
        self.spectrum_label.mousePressEvent = self.spectrum_click
        self.energy_click(0)
        # Layout
        self.layout.nextRow()
        self.layout.addItem(self.freq_label, colspan=3)
        self.layout.nextRow()
        self.layout.addItem(self.freq_slider, colspan=3)
        self.layout.nextRow()
        self.layout.addItem(self.energy_label)
        self.layout.addItem(self.scroll_label)
        self.layout.addItem(self.spectrum_label)

        # Fix secondTab
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.visualizerTab), _translate("MainWindow", "Visualizer", None))
        #SIGNALS AND CONNECTORS
        self.visualizerStartBtn.clicked.connect(self.start_visualizer_click)
        self.visualizerStopBtn.clicked.connect(self.stop_visualizer_click)
        self.parent_app.aboutToQuit.connect(self.closeEvent)
        # AUDIO INPUT DEVICES
        self.getaudiodevices()
        self.soundDeviceSelectBox.currentIndexChanged.connect(
            self.inputDeviceChanged)

    def inputDeviceChanged(self, index):
        print("selection changed")
        self.audio_processor.stop()
        self.audio_processor = AudioInputProcess(
            args=(Processor(self), index, self.parent_app.processEvents))
        self.audio_processor.start()

    def getaudiodevices(self):
        p = pyaudio.PyAudio()
        ad_list = []
        for i in range(p.get_device_count()):
            if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
                ad_list.append(p.get_device_info_by_index(i).get('name'))
        self.soundDeviceSelectBox.addItems(ad_list)

    def freq_slider_change(self, tick):
        minf = self.freq_slider.tickValue(0)**2.0 * (config.MIC_RATE / 2.0)
        maxf = self.freq_slider.tickValue(1)**2.0 * (config.MIC_RATE / 2.0)
        t = 'Frequency range: {:.0f} - {:.0f} Hz'.format(minf, maxf)
        self.freq_label.setText(t)
        config.MIN_FREQUENCY = minf
        config.MAX_FREQUENCY = maxf
        dsp.create_mel_bank()

    def energy_click(self, x):
        self.visualization_effect = energy
        self.energy_label.setText('Energy', color=self.active_color)
        self.scroll_label.setText('Scroll', color=self.inactive_color)
        self.spectrum_label.setText('Spectrum', color=self.inactive_color)

    def scroll_click(self, x):
        self.visualization_effect = scroll
        self.energy_label.setText('Energy', color=self.inactive_color)
        self.scroll_label.setText('Scroll', color=self.active_color)
        self.spectrum_label.setText('Spectrum', color=self.inactive_color)

    def spectrum_click(self, x):
        self.visualization_effect = spectrum
        self.energy_label.setText('Energy', color=self.inactive_color)
        self.scroll_label.setText('Scroll', color=self.inactive_color)
        self.spectrum_label.setText('Spectrum', color=self.active_color)

    def start_visualizer_click(self, event):
        try:
            self.audio_processor.start()
        except:
            self.audio_processor = AudioInputProcess(args=(Processor(
                self), self.soundDeviceSelectBox.currentIndex(), self.parent_app.processEvents))
            self.audio_processor.start()

    def stop_visualizer_click(self, event):
        self.audio_processor.stop()

    def closeEvent(self):
        self.audio_processor.stop()
