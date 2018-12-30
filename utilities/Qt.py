## 'Qt' is a local module; it is intended mainly to cover up the differences
## between PyQt4 and PyQt5.
import os

ENVIRON = os.environ['CSMCA_QT_LIB']

if ENVIRON=='PyQt5':
	from PyQt5 import QtGui,QtCore,QtWidgets
	try: from PyQt5 import QtSvg
	except: pass
	#try:
	#	from PyQt5.QtWebKitWidgets import QWebView# , QWebPage
	#except:
	#	print('webview unavailable')
elif ENVIRON == 'PyQt4':
	from PyQt4 import QtGui,QtCore
	from PyQt4 import QtGui as QtWidgets
	#try:
	#	from PyQt4.QtWebKitWidgets import QWebView# , QWebPage
	#except:
	#	print('webview unavailable')
	
