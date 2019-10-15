import os

from .Qt import QtGui,QtCore,QtWidgets
from .templates import ui_ipy as ipy_template
import sys,string
import time

from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager

# The ID of an installed kernel, e.g. 'bash' or 'ir'.
USE_KERNEL = 'python3'

class myConsole(RichJupyterWidget):
	def __init__(self,customBanner=None):
		"""Start a kernel, connect to it, and create a RichJupyterWidget to use it
		"""
		super(myConsole, self).__init__()
		if customBanner!=None: self.banner=customBanner
		self.kernel_manager = QtInProcessKernelManager(kernel_name=USE_KERNEL)
		self.kernel_manager.start_kernel()
		self.kernel = self.kernel_manager.kernel

		self.kernel_manager.kernel.gui = 'qt'
		self.font_size = 6

		self.kernel_client = self.kernel_manager.client()
		self.kernel_client.start_channels()

		def stop():
			kernel_client.stop_channels()
			kernel_manager.shutdown_kernel()
			guisupport.get_app_qt().exit()

		self.exit_requested.connect(stop)

	def pushVariables(self,variableDict):
		""" Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
		self.kernel.shell.push(variableDict)
	def clearTerminal(self):
		""" Clears the terminal """
		self._control.clear()    

	def printText(self,text):
		""" Prints some plain text to the console """
		self._append_plain_text(text)

	def executeCommand(self,command,hidden=False):
		""" Execute a command in the frame of the console widget """
		self._execute(command,hidden)



class AppWindow(QtWidgets.QMainWindow, ipy_template.Ui_MainWindow):
	def __init__(self, parent=None,**kwargs):
		super(AppWindow, self).__init__(parent)
		self.setupUi(self)
		self.kp=kwargs.get('kp',None)

		self.setWindowTitle('iPython Console : Try out stuff!')
		self.msg = QtWidgets.QLabel()
		self.statusbar.addWidget(self.msg)
		self.msg.setText('Hi!')
		self.timer = QtCore.QTimer()

		try:
			#--------instantiate the iPython class-------
			self.ipyConsole = myConsole("################ Interactive KuttyPy Console ###########\nAccess hardware using the Instance 'kp'.  e.g.  kp.setReg('PORTB',8)\n\n")
			self.layout.addWidget(self.ipyConsole)
		except Exception as e:
			print ("failed to launch iPython. Is it installed?", e)
			self.close()
			return
			

		cmdDict = {}
		#cmdDict = {"analytics":self.analytics}
		if self.kp :
			cmdDict["kp"]=self.kp
		self.ipyConsole.pushVariables(cmdDict)
		self.console_enabled=True

	def importNumpy(self):
		self.ipyConsole.executeCommand('import numpy as np',True)
		self.message('imported Numpy as np')

	def importScipy(self):
		self.ipyConsole.executeCommand('import scipy',True)
		self.message('imported scipy')

	def importPylab(self):
		self.msg.setText('importing Pylab...')
		self.ipyConsole.executeCommand('from pylab import *',True)
		self.message('from pylab import * .  You can use plot() and show() commands now.')

	def message(self,txt):
		self.msg.setText(txt)
		self.timer.stop()
		self.timer.singleShot(4000,self.msg.clear)

	def updateDevice(self,kp):
		self.kp = kp

	def closeEvent(self, event):
		self.timer.stop()
		self.finished=True

	def __del__(self):
		print ('bye')
        		
if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	myapp = AppWindow(kp=None)
	myapp.show()
	sys.exit(app.exec_())


