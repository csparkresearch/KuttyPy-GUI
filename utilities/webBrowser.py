# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
print('importing webbrowser')
import os, string, glob

from pyqtgraph.Qt import QtGui, QtCore, QtWidgets

# QtWebEngineWidgets is not wrapped by pyqtgraph; try PyQt6 then PyQt5.
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEnginePage
    import PyQt6.QtWebEngineWidgets as QtWebEngineWidgets
except ImportError:
    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
        import PyQt5.QtWebEngineWidgets as QtWebEngineWidgets
    except ImportError:
        QWebEngineView = None
        QWebEnginePage = None
        QtWebEngineWidgets = None

import sys, pkg_resources


class codeBrowser(QWebEngineView):
	def __init__(self, *args, **kwargs):
		super(codeBrowser, self).__init__()
		self.code_path = '.'
		sys.path.append(self.code_path)
		self.showMaximized()

	def setFile(self, url):
		newUrl = QtCore.QUrl.fromLocalFile(QtCore.QFileInfo(url).absoluteFilePath())
		print('SETTING URL', url, newUrl)
		self.setUrl(newUrl)
