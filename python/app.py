#!/usr/bin/python

import sys
import argparse
from settings import config
from PyQt4 import QtCore, QtGui
from gui.ui import UI

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
        app = QtGui.QApplication(sys.argv)
        window = QtGui.QMainWindow()
        ui = UI(app)
        ui.setupUi(window)
        window.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
