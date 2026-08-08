## 'Qt' is a local module; it covers differences between PyQt5 and PyQt6
## by routing all Qt imports through pyqtgraph's compatibility layer.
import os

ENVIRON = os.environ.get('CSMCA_QT_LIB', 'PyQt5')

from pyqtgraph.Qt import QtGui, QtCore, QtWidgets

try:
    from pyqtgraph.Qt import QtSvg
except ImportError:
    pass

# QtWebEngineWidgets is not wrapped by pyqtgraph; try each binding directly.
QWebView = None
try:
    if ENVIRON == 'PyQt6':
        from PyQt6.QtWebEngineWidgets import QWebEngineView as QWebView
    else:
        from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView
except ImportError:
    QWebView = None
