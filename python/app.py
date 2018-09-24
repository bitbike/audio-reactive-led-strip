#!/usr/bin/python

import sys
import argparse
from settings import config
from visualizer.visualizer_gui import Visualizer
from visualizer.processor import Processor
from audio import microphone

"""Visualizer to process audio into 1D Color Data for NeoPixel-like LEDs"""


def main():
    parser = argparse.ArgumentParser(description='Start visualizer.')
    parser.add_argument("-hl", "--headless", action='store_true',
                        help="run the visualizer headless")
    parser.add_argument("-m", "--mode", dest="vis_mode",
                        help="set visualizer mode")

    args = parser.parse_args()

    #if args.headless:
    #    enable_gui = False
    #elif args.vis_mode:
    #    visualizer_mode = args.vis_mode

    print(args)

    if not args.headless:
        import pyqtgraph as pg
        from pyqtgraph.Qt import QtGui, QtCore
        # Create GUI window
        app = QtGui.QApplication([])
        view = pg.GraphicsView()
        layout = pg.GraphicsLayout(border=(100,100,100))
        view.setCentralItem(layout)
        view.show()
        view.setWindowTitle('Visualization')
        view.resize(800,600)
        gui = Visualizer(app, layout)
        process = Processor(gui)
        microphone.start_stream(process)

if __name__ == "__main__":
    main()
