# seelab_examples/__init__.py

import sys,os, json, time
from PyQt5 import QtWidgets, QtGui, QtCore
import argparse  # Added import for argparse

from .KuttyPyPlus import run  # Adjust the import based on your actual script structure


import sys as _sys

class MyArgumentParser(argparse.ArgumentParser):

    def print_help(self, file=None):
        if file is None:
            file = _sys.stdout
        message = "-h : show this help for no reason at all."
        file.write(message+"\n")

def showSplash():
    # Create and display the splash screen
    splash = os.path.join(os.path.dirname(__file__),'docs/images/app-screens-1200.jpg')
    splash_pix = QtGui.QPixmap(splash)
    splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())

    progressBar = QtWidgets.QProgressBar(splash)
    progressBar.setStyleSheet('''

    QProgressBar {
        border: 2px solid grey;
        border-radius: 5px;	
        border: 2px solid grey;
        border-radius: 5px;
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: #012748;
        width: 10px;
        margin: 0.5px;
    }
    ''')
    progressBar.setMaximum(20)
    progressBar.setGeometry(0, splash_pix.height() - 50, splash_pix.width(), 20)
    progressBar.setRange(0,20)

    splash.show()
    splash.pbar = progressBar
    splash.show()
    return splash


def main():
    """Main entry point for the module."""

    os.chdir(os.path.dirname(__file__))
    app = QtWidgets.QApplication(sys.argv)
    splash = showSplash()
    splash.showMessage("<h2><font color='Black'>Initializing...</font></h2>", QtCore.Qt.AlignLeft, QtCore.Qt.black)

    for a in range(5):
        app.processEvents()
        time.sleep(0.01)

    #IMPORT LIBRARIES
    splash.showMessage("<h2><font color='Black'>Importing libraries...</font></h2>", QtCore.Qt.AlignLeft, QtCore.Qt.black)
    splash.pbar.setValue(1)

    splash.showMessage("<h2><font color='Black'>Importing communication library...</font></h2>", QtCore.Qt.AlignLeft, QtCore.Qt.black)
    splash.pbar.setValue(2)

    splash.showMessage("<h2><font color='Black'>Importing Numpy...</font></h2>", QtCore.Qt.AlignLeft, QtCore.Qt.black)
    splash.pbar.setValue(3)
    import pyqtgraph as pg
    import numpy as np

    splash.showMessage("<h2><font color='Black'>Importing Scipy...</font></h2>", QtCore.Qt.AlignLeft, QtCore.Qt.black)
    splash.pbar.setValue(5)

    window = run()
    window.show()
    sys.exit(app.exec_())

