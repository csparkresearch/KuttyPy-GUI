# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
print('importing webbrowser')
import os,string,glob

from PyQt5 import QtGui,QtCore,QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5 import QtWebEngineWidgets



import sys,pkg_resources

class codeBrowser(QWebView):
	def __init__(self,*args,**kwargs):
		super(codeBrowser, self).__init__()
		self.code_path = '.'
		sys.path.append(self.code_path)
		self.showMaximized()
				
	def setFile(self,url):
		newUrl = QtCore.QUrl.fromLocalFile(QtCore.QFileInfo(url).absoluteFilePath())
		print ('SETTING URL',url,newUrl)
		self.setUrl(newUrl)#pkg_resources.resource_filename('eyes_html',url)))
