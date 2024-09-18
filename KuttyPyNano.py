'''
'''
#!/usr/bin/python3

import os,sys,time,re,traceback,platform,inspect
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utilities.Qt import QtGui, QtCore, QtWidgets
import KuttyPyLibNano

from utilities.templates import ui_layoutnano as layout
from utilities import dio,uploader
from utilities import REGISTERS_NANO as REGISTERS
import constants


from functools import partial
from collections import OrderedDict




class myTimer():
	def __init__(self,interval):
		self.interval = interval
		self.reset()
	def reset(self):
		self.timeout = time.time()+self.interval
	def ready(self):
		T = time.time()
		dt = T - self.timeout
		if dt>0: #timeout is ahead of current time 
			#if self.interval>5:print('reset',self.timeout,dt)
			self.timeout = T - dt%self.interval + self.interval
			#if self.interval>5:print(self.timeout)
			return True
		return False
	def progress(self):
		return 100*(self.interval - self.timeout + time.time())/(self.interval)			

class AppWindow(QtWidgets.QMainWindow, layout.Ui_MainWindow):
	p=None
	logThis = QtCore.pyqtSignal(str)
	logThisPlain = QtCore.pyqtSignal(bytes)
	serialGaugeSignal = QtCore.pyqtSignal(int)
	def __init__(self, parent=None,**kwargs):
		super(AppWindow, self).__init__(parent)
		self.setupUi(self)

		self.VERSION = REGISTERS.VERSIONNUM
		self.SPECIALS = REGISTERS.SPECIALS
		self.REGISTERS = REGISTERS.REGISTERS
		self.EXAMPLES_DIR = REGISTERS.EXAMPLES
		self.ADC_PINS = REGISTERS.ADC
		
		self.docks = [self.leftdock,self.rightdock]
		self.sensorList = []
		self.controllerList = []
		self.monitoring = True
		self.logRegisters = True
		self.userHexRunning = False
		self.uploadingHex = False
		self.autoUpdateUserRegisters = False
		self.CFile = None #'~/kuttyPy.c'
		self.ipy = None

		self.setTheme("material")
		examples = [a for a in os.listdir(os.path.join(path["examples"],self.EXAMPLES_DIR)) if ('.py' in a) and a is not 'kuttyPy.py'] #.py files except the library
		self.exampleList.addItems(examples)
		blinkindex = self.exampleList.findText('blink.py')
		if blinkindex!=-1: #default example. blink.py present in examples directory
			self.exampleList.setCurrentIndex(blinkindex)

		######## PYTHON CODE
		self.codeThread = QtCore.QThread()
		self.codeEval = self.codeObject(self.REGISTERS)
		self.codeEval.moveToThread(self.codeThread)
		self.codeEval.finished.connect(self.codeThread.quit)
		self.codeEval.logThis.connect(self.appendLog) #Connect to the log window
		self.logThis.connect(self.appendLog) #Connect to the log window
		self.logThisPlain.connect(self.appendLogPlain) #Connect to the log window
		self.serialGaugeSignal.connect(self.setSerialgauge)
		
		self.codeThread.started.connect(self.codeEval.execute)
		self.codeThread.finished.connect(self.codeFinished)

		######### C CODE UPLOADER
		self.uploadThread = QtCore.QThread()
		self.UploadObject = self.uploadObject()
		self.UploadObject.moveToThread(self.uploadThread)
		self.UploadObject.finished.connect(self.uploadThread.quit)
		self.UploadObject.logThis.connect(self.appendLog) #Connect to the log window
		self.UploadObject.logThisPlain.connect(self.appendLogPlain) #Connect to the log window. add plain text
		self.logThis.connect(self.appendLog) #Connect to the log window

		self.uploadThread.started.connect(self.UploadObject.execute)
		self.uploadThread.finished.connect(self.codeFinished)

		self.commandQ = []
		self.btns={}
		self.registers = []
		self.addPins()

		self.statusBar = self.statusBar()
		self.makeBottomMenu()

		global app


		self.initializeCommunications()
		self.pending = {
		'status':myTimer(constants.STATUS_UPDATE_INTERVAL),
		'update':myTimer(constants.AUTOUPDATE_INTERVAL),
		}

		serialgaugeoptions = {'name':'Serial Monitor', 'init':print, 'read':None,
				'fields':['Value'],
				'min':[0],
				'max':[255]}
		self.serialGauge = dio.DIOSENSOR(self,serialgaugeoptions)
		
		self.startTime = time.time()
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateEverything)
		self.timer.start(20)

		
		#Auto-Detector
		self.shortlist=KuttyPyLibNano.getFreePorts()

	def newRegister(self):
		reg = dio.REGEDIT(self.commandQ)
		#self.registerLayout.addWidget(reg)
		#self.registers.append(reg)

		#TODO: Convert layout to listwidget to enable re-ordering
		regItem = QtWidgets.QListWidgetItem()
		regItem.setSizeHint(QtCore.QSize(200,40))
		self.registerList.addItem(regItem)
		self.registerList.setItemWidget(regItem,reg)
		self.registers.append(regItem)

	def addPins(self):
		for a in ['D','B']:
			self.btns[a] = dio.REGVALS(a)
			self.leftlayout.addWidget(self.btns[a])
		self.btns['C'] = dio.REGVALS('C')
		self.rightlayout.addWidget(self.btns['C'])
		for name in ['PD1','PD0','PC6','GND','PD2','PD3','PD4','PD5','PD6','PD7','PB0','PB1','PB2','PB3','PB4']: #left dock
			checkbox = dio.widget(name,self.commandQ,extra = self.SPECIALS.get(name,''))
			self.leftlayout.addWidget(checkbox)
			self.btns[name] = checkbox
		for name in ['VIN','GND','PC6','5V','ADC7','ADC6','SCL','SDA','PC3','PC2','PC1','PC0','AREF','3V3','PB5']: #left dock
			checkbox = dio.widget(name,self.commandQ,extra = self.SPECIALS.get(name,''))
			self.rightlayout.addWidget(checkbox)
			self.btns[name] = checkbox

	def tabChanged(self,index):
		if index != 0 : #examples/editor tab. disable monitoring
			self.monitoring = False
			for a in self.docks:
				a.hide()		
		else: #Playground . enable monitoring and control.
			self.monitoring = True
			self.autoRefreshUserRegisters.setChecked(False)
			self.userRegistersAutoRefresh(False)
			for a in self.docks:
				a.show()		

	################USER CODE SECTION####################
	class codeObject(QtCore.QObject):
		finished = QtCore.pyqtSignal()
		logThis = QtCore.pyqtSignal(str)
		code = ''

		def __init__(self,REGISTERS):
			super(AppWindow.codeObject, self).__init__()
			self.PORTMAP = {v: k for k, v in REGISTERS.items()} #Lookup port name based on number
			self.compiled = ''
			self.SR = None
			self.GR = None
			self.evalGlobals = {}

			self.evalGlobals['getReg']  = self.getReg
			self.evalGlobals['setReg']  = self.setReg
			self.evalGlobals['print']  = self.printer

		def setCode(self,code,**kwargs):
			try:
				self.compiled = compile(code.encode(), '<string>', mode='exec')
			except SyntaxError as err:
				error_class = err.__class__.__name__
				detail = err.args[0]
				line_number = err.lineno
				return '''<span style="color:red;">%s at line %d : %s</span>''' % (error_class, line_number, detail)
			except Exception as err:
				error_class = err.__class__.__name__
				detail = err.args[0]
				cl, exc, tb = sys.exc_info()
				line_number = traceback.extract_tb(tb)[-1][1]
				return '''<span style="color:red;">%s at line %d: %s</span>''' % (error_class, line_number, detail)

			self.SR = kwargs.get('setReg')
			self.GR = kwargs.get('getReg')
			self.evalGlobals = kwargs
			self.evalGlobals['getReg']  = self.getReg #Overwrite these three. They will be wrapped.
			self.evalGlobals['setReg']  = self.setReg
			self.evalGlobals['print']  = self.printer
			return ''
			

		def printer(self,*args):
			self.logThis.emit('''<span style="color:cyan;">%s</span>'''%(' '.join([str(a) for a in args])))

		def setReg(self,reg,value):
			html=u'''<pre><span>W\u2193</span>{0:s}\t{1:d}\t0x{1:02x} / 0b{1:08b}</pre>'''.format(self.PORTMAP.get(reg,''),value)
			self.logThis.emit(html)
			self.SR(reg,value)

		def getReg(self,reg):
			value = self.GR(reg)
			html=u'''<pre><span>R\u2191</span>{0:s}\t{1:d}\t0x{1:02x} / 0b{1:08b}</pre>'''.format(self.PORTMAP.get(reg,''),value)
			self.logThis.emit(html)
			return value

		def execute(self):
			#old = sys.stdout
			#olde = sys.stderr
			#sys.stdout = self.toLog(self.logThis)
			#sys.stderr = self.toLog(self.logThis)
			try:
				exec(self.compiled,{},self.evalGlobals)
			except SyntaxError as err:
				error_class = err.__class__.__name__
				detail = err.args[0]
				line_number = err.lineno
				self.logThis.emit('''<span style="color:red;">%s at line %d : %s</span>''' % (error_class, line_number, detail))
			except Exception as err:
				error_class = err.__class__.__name__
				detail = err.args[0]
				cl, exc, tb = sys.exc_info()
				line_number = traceback.extract_tb(tb)[-1][1]
				self.logThis.emit('''<span style="color:red;">%s at line %d: %s</span>''' % (error_class, line_number, detail))
			#sys.stdout = old
			#sys.stderr = olde
			self.logThis.emit("Finished executing user code")
			self.finished.emit()
	
	def runCode(self):
		#if self.p:
		#	try:
		#		self.p.fd.read() #Clear junk
		#		self.p.fd.close()
		#	except:pass
		if self.codeThread.isRunning():
			print('one code is already running')
			return

		self.log.clear() #clear the log window
		self.log.setText('''<span style="color:green;">----------User Code Started-----------</span>''')
		kwargs = {}
		for a in dir(self.p):
			attr = getattr(self.p, a)
			if inspect.ismethod(attr) and a[:2]!='__':
				kwargs[a] = attr

		compilemsg = self.codeEval.setCode('{0:s}'.format(self.userCode.toPlainText()),**kwargs)
		if len(compilemsg):
			self.log.append(compilemsg)
			return
		self.codeThread.start()

		self.userCode.setStyleSheet("border: 3px dashed #53ffff;")
		self.tabs.setTabEnabled(0,False)

	def codeFinished(self):
		print('finished')
		self.tabs.setTabEnabled(0,True)
		self.userCode.setStyleSheet("")
		self.uploadingHex = False

	def abort(self):
		if self.codeThread.isRunning():
			self.log.append('''<span style="color:red;">----------Kill Signal(Doesn't work yet. Restart the application)-----------</span>''')
			self.codeThread.quit()
			self.codeThread.terminate()
			del self.codeThread
			self.codeThread = QtCore.QThread()
			self.codeEval = self.codeObject(self.REGISTERS)
			self.codeEval.moveToThread(self.codeThread)
			self.codeEval.finished.connect(self.codeThread.quit)
			self.codeEval.logThis.connect(self.appendLog) #Connect to the log window			
			self.codeThread.started.connect(self.codeEval.execute)
			self.codeThread.finished.connect(self.codeFinished)

	def getReg(self,reg,record = True):
		val = self.p.getReg(reg)
		if record:
			self.updatedRegs[reg] = [0,val]
		return val

	def setReg(self,reg,val,record = True):
		self.p.setReg(reg,val)
		if record:
			self.updatedRegs[reg] = [1,val]
		return val

	def appendLog(self,txt):
		self.log.append(txt)

	def appendLogPlain(self,txt):
		self.log.moveCursor(QtGui.QTextCursor.End)
		self.log.insertPlainText(txt.decode('ascii'))

	def setSerialgauge(self,val):
		self.serialGauge.setValue([val])

	def genLog(self):
		html='''<table border="1" align="center" cellpadding="1" cellspacing="0" style="font-family:arial,helvetica,sans-serif;font-size:9pt;">
		<tbody><tr><td colspan="4">%s</td></tr>'''%(time.ctime())
		#html+='''<tr><td style="background-color:#77cfbb;">R/W</td><td style="background-color:#77cfbb;">REGISTER</td>
		#<td style="background-color:#77cfbb;">Value</td><td style="background-color:#77cfbb;">Hex/Binary</td></tr>'''

		for a in self.updatedRegs:
			row = self.updatedRegs[a]
			html+=u'''
				<tr>
					<td>{0:s}</td>
					<td>{1:s}</td>
					<td>{2:d}</td>
					<td>0b{2:08b} | 0x{2:02x}</td>
				</tr>
				'''.format(u'W \u2193' if row[0] else u'R \u2191',a,row[1])
		html+="</tbody></table>"	
		self.log.setHtml(html)

	def userRegistersAutoRefresh(self,state):
		self.autoUpdateUserRegisters = state

	def updateEverything(self):
		self.locateDevices()
		if not self.checkConnectionStatus():return
		#KuttyPy monitor has handed over control to native code. act as serial monitor/ debug window
		if self.uploadingHex:
			return

		
		if self.userHexRunning:
			t = self.p.fd.read(self.p.fd.in_waiting)
			if len(t):
				self.serialGaugeSignal.emit(t[0])
				self.logThisPlain.emit(t)
			return
		
		#self.setTheme('material')

		if self.codeThread.isRunning():
			return

		if self.autoUpdateUserRegisters:
			for a in range(self.registerList.count()):
				self.registerList.itemWidget(self.registerList.item(a)).execute()
			
		while len(self.commandQ):
			if not self.centralWidget().isEnabled():
				return
			a = self.commandQ.pop(0)
			if a[0] == 'DSTATE': #Digital Out ['DSTATE','Pxx',state]
				pname = 'PORT'+a[1][1].upper()
				bit = int(a[1][2])
				reg = self.getReg(pname)
				reg &=~ (1<<bit)
				if(a[2]):reg |= (1<<bit)
				self.setReg(pname,reg)
			elif a[0] == 'DTYPE': #Digital pin I/O ['DTYPE','Pxx',state]
				pname = 'DDR'+a[1][1].upper()
				bit = int(a[1][2])
				reg = self.getReg(pname)
				reg &=~ (1<<bit)
				if(a[2]):reg |= (1<<bit)
				self.setReg(pname,reg);
			elif a[0] == 'WRITE': #['WRITE','REGNAME',val]
				self.setReg(a[1],a[2]);
			elif a[0] == 'READ': #['READ','REGNAME',function]
				val = self.getReg(a[1])
				a[2](val)
			elif a[0] == 'CNTR1': #['CNTR1',output with setValue function]
				cl = self.getReg('TCNT1L',False)
				ch = self.getReg('TCNT1H',False)
				a[1].setValue(cl|(ch<<8))
			elif a[0] == 'ADC': #['ADC',ADMUX,output with setValue function, to log, or not to log]
				self.setReg('ADMUX',a[1],a[3])
				self.setReg('ADCSRA',196|1,a[3])
				adcl = self.getReg('ADCL',a[3])
				adch = self.getReg('ADCH',a[3])
				a[2].setValue(adcl|(adch<<8))
		
		for a in self.sensorList:
			if a[0].isVisible():
				a[0].setValue(a[0].read())
			
		if self.enableLog.isChecked():
			if self.clearLog.isChecked() and len(self.updatedRegs):
				self.log.clear()
			if len(self.updatedRegs):
				self.genLog()
				self.updatedRegs = OrderedDict()

		if self.pending['status'].ready() and self.monitoring:
			val = self.p.getReg(self.getRegs[self.currentRegister][0])
			self.getRegs[self.currentRegister][1](self.getRegs[self.currentRegister][0],val)
			self.currentRegister +=1
			if self.currentRegister==len(self.getRegs):
				self.currentRegister = 0
			for a in ['B','C','D']:
				self.btns[a].setRegs(self.p.REGSTATES)


		if self.pending['update'].ready():
			pass
			#print('update')

	def updateInputs(self,port,value):
		portchar = port[3]
		for a in range(8):
			name = 'P'+portchar+str(a)
			btn = self.btns.get(name,None)
			if btn is None: continue
			btn.nameIn.setChecked((value>>a)&1)
			if name in self.ADC_PINS: #ADC
				if btn.currentPage == 2: #ADC Page displayed
					self.commandQ.append(['ADC',btn.ADMUX,btn,btn.logstate])
			elif type(btn)==dio.DIOCNTR and btn.currentPage==2: # CNTR
					self.commandQ.append(['CNTR1',btn.slider])

	def newStepperController(self):
		if self.p.connected:
			dialog = dio.DIOSTEPPER(self,total=200,device=self.p)
			dialog.launch()
			self.sensorList.append([dialog,None])


	############ I2C SENSORS #################
	def I2CScan(self):
		if self.p.connected:
			x = self.p.I2CScan()
			print('Responses from: ',x)
			for a in self.sensorList:
				a[0].setParent(None)
				a[1].setParent(None)
			self.sensorList = []
			for a in self.controllerList:
				a[0].setParent(None)
				a[1].setParent(None)
			self.controllerList = []
			for a in x:
				s = self.p.sensors.get(a,None)
				if s is not None:
					btn = QtWidgets.QPushButton(s['name']+':'+hex(a))
					dialog = dio.DIOSENSOR(self,s)
					btn.clicked.connect(dialog.launch)
					self.sensorLayout.addWidget(btn)
					self.sensorList.append([dialog,btn])
					continue

				s = self.p.controllers.get(a,None)
				if s is not None:
					btn = QtWidgets.QPushButton(s['name']+':'+hex(a))
					dialog = dio.DIOCONTROL(self,s)
					btn.clicked.connect(dialog.launch)
					self.sensorLayout.addWidget(btn)
					self.controllerList.append([dialog,btn])
					continue

				s = self.p.special.get(a,None)
				if s is not None:
					btn = QtWidgets.QPushButton(s['name']+':'+hex(a))
					dialog = dio.DIOROBOT(self,s)
					btn.clicked.connect(dialog.launch)
					self.sensorLayout.addWidget(btn)
					self.controllerList.append([dialog,btn])
					continue


	def loadExample(self,filename):
		self.userCode.setPlainText(open(os.path.join(path["examples"],self.EXAMPLES_DIR,filename), "r").read())


	########################### UPLOAD HEX FILE #######################

	class uploadObject(QtCore.QObject):
		finished = QtCore.pyqtSignal()
		logThis = QtCore.pyqtSignal(str)
		logThisPlain = QtCore.pyqtSignal(bytes)
		fname = ''
		p = None
		def __init__(self):
			super(AppWindow.uploadObject, self).__init__()
		def config(self,mode,p,fname):
			self.p = p
			self.fname = fname
			self.mode = mode

		def execute(self):
			if self.mode == 'compileupload':
				try:
					import subprocess
					fname = '.'.join(self.fname.split('.')[:-1])
					cmd = 'avr-gcc -Wall -O2 -mmcu=%s -o "%s" "%s"' %('atmega328p',fname,self.fname)
					self.logThis.emit('''<span style="color:green;">Compiling for Atmega328p (Nano)</span>''')
					print(cmd)
					res = subprocess.getstatusoutput(cmd)
					if res[0] != 0:
						self.logThis.emit('''<span style="color:red;">Compile Error: %s</span>'''%res[1])
						self.finished.emit()
						return

					else:
						self.logThis.emit('''<span style="color:white;">%s</span><br>'''%res[1])
					cmd = 'avr-objcopy -j .text -j .data -O ihex "%s" "%s.hex"' %(fname,fname)
					res = subprocess.getstatusoutput(cmd)
					self.logThis.emit('''<span style="color:white;">%s</span><br>'''%res[1])
					cmd = 'avr-objdump -S "%s" > "%s.lst"'%(fname,fname)
					res = subprocess.getstatusoutput(cmd)
					self.logThis.emit('''<span style="color:white;">%s</span><br>'''%res[1])
					if self.fname[-2:] in ['.c','.C']:
						self.fname = self.fname[:-2]+'.hex' #Replace .c with .hex
						self.mode = 'upload'
						self.logThis.emit('''<span style="color:green;">Generated Hex File</span>''')
					self.logThis.emit('''<span style="color:green;">Finished Compiling: Generated Hex File</span>''')
				except Exception as err:
					self.logThis.emit('''<span style="color:red;">Failed to Compile:%s</span>'''%str(err))

			if self.p.connected:
				if self.mode == 'upload':
					try:
						self.p.fd.setRTS(0);time.sleep(0.01);self.p.fd.setRTS(1);time.sleep(0.4)
						dude = uploader.Uploader(self.p.fd, hexfile=self.fname,logger = self.logThis)
						dude.program()
						dude.verify()
						self.p.fd.setRTS(0);time.sleep(0.01);self.p.fd.setRTS(1);time.sleep(0.2)
						self.p.get_version()
						self.logThis.emit('''<span style="color:green;">Finished upload</span>''')
					except Exception as err:
						self.logThis.emit('''<span style="color:red;">Failed to upload</span>''')
			self.finished.emit()
	
	def uploadHex(self):
		filename = QtWidgets.QFileDialog.getOpenFileName(self," Open a hex file to upload to your KuttyPy", "", "Hex Files (*.hex)")
		if len(filename[0]):
			#self.userCode.setStyleSheet("border: 3px dashed #53ffff;")
			#self.tabs.setTabEnabled(0,False)
			self.uploadingHex = True
			self.log.clear()
			self.log.setText('''<span style="color:cyan;">-- Uploading Code --</span><br>''')
			self.UploadObject.config('upload',self.p,filename[0])
			self.uploadThread.start()


	def openFile(self):
		filename = QtWidgets.QFileDialog.getOpenFileName(self," Open a C file to edit", path["examples"], "C Files (*.c *.C)")
		if len(filename[0]):
			self.filenameLabel.setText(filename[0])
			self.CFile = filename[0]
			self.log.clear()
			self.log.setText('''<span style="color:cyan;">-- Opened File: %s --</span><br>'''%filename[0])
			if 'inux' in platform.system(): #Linux based system
				os.system('%s "%s"' % ('xdg-open', filename[0]))
			else:
				os.system('%s "%s"' % ('open', filename[0]))

	def compileAndUpload(self):
		if self.CFile:
			self.uploadingHex = True
			self.log.clear()
			self.log.setText('''<span style="color:cyan;">-- Compiling and Uploading Code --</span><br>''')
			self.UploadObject.config('compileupload',self.p,self.CFile)
			self.uploadThread.start()
			

	##############################
	def setTheme(self,theme):
		self.setStyleSheet("")
		self.setStyleSheet(open(os.path.join(path["themes"],theme+".qss"), "r").read())

			
	def initializeCommunications(self,port=False):
		if self.p:
			try:self.p.fd.close()
			except:pass
		if port:
			self.p = KuttyPyLibNano.connect(port = port)
		else:
			self.p = KuttyPyLibNano.connect(autoscan=True)
		if self.p.connected:
			self.userApplication.setChecked(False)
			self.setWindowTitle('KuttyPy Interactive Console [{0:s}]'.format(self.p.portname))
			self.updatedRegs=OrderedDict()
			self.currentRegister = 0
			self.getRegs=[
			('PINB',self.updateInputs),
			('PINC',self.updateInputs),
			('PIND',self.updateInputs),
			]


		else:
			self.setWindowTitle('KuttyPy Interactive Console [ Hardware not detected ]')

	def jumpToApplication(self,state):
		if self.p:
			if state:
				self.userHexRunning=True
				self.p.fd.write(b'j') #Skip to application (Bootloader resets) 

				for a in self.docks:
					a.setEnabled(False)
				self.tabs.setEnabled(False)
				self.log.clear()
				self.log.setText('''<span style="color:cyan;">-- Serial Port Monitor --</span><br>''')
				self.serialGauge.show()

			else:
				self.p.fd.setRTS(0)  #Trigger a reset
				time.sleep(0.01)
				self.p.fd.setRTS(1)
				time.sleep(0.1)
				while self.p.fd.in_waiting:
					self.p.fd.read()
				self.p.get_version()
				for a in self.docks:
					a.setEnabled(True)
				self.userHexRunning=False
				self.tabs.setEnabled(True)
				self.serialGauge.hide()
		else:
			if self.isChecked():
				self.setChecked(False)

		
	def makeBottomMenu(self):
		try:self.pushbutton.setParent(None)
		except:pass
		self.pushbutton = QtWidgets.QPushButton('Menu')
		self.pushbutton.setStyleSheet("height: 13px;padding:3px;color: #FFFFFF;")
		menu = QtWidgets.QMenu()

		menu.addAction('Save Window as Svg', self.exportSvg)
		menu.addAction('Open Stepper Controller', self.newStepperController)

		#Theme
		self.themeAction = QtWidgets.QWidgetAction(menu)
		themes = [a.split('.qss')[0] for a in os.listdir(path["themes"]) if '.qss' in a]
		self.themeBox = QtWidgets.QComboBox(); self.themeBox.addItems(themes)
		self.themeBox.currentIndexChanged['QString'].connect(self.setTheme)
		self.themeAction.setDefaultWidget(self.themeBox)
		menu.addAction(self.themeAction)

		self.pushbutton.setMenu(menu)

		self.userApplication = QtWidgets.QCheckBox("User App");
		self.userApplication.toggled['bool'].connect(self.jumpToApplication)
		self.statusBar.addPermanentWidget(self.userApplication)

		self.hexUploadButton = QtWidgets.QPushButton("Upload Hex");
		self.hexUploadButton.clicked.connect(self.uploadHex)
		self.statusBar.addPermanentWidget(self.hexUploadButton)


		self.speedbutton = QtWidgets.QComboBox(); self.speedbutton.addItems(['Slow','Fast','Ultra']);
		self.speedbutton.setCurrentIndex(1);
		self.speedbutton.currentIndexChanged['int'].connect(self.setSpeed)
		self.statusBar.addPermanentWidget(self.speedbutton)

		self.statusBar.addPermanentWidget(self.pushbutton)

	def setSpeed(self,index):
		self.timer.setInterval([100,20,5][index])

	def locateDevices(self):
		try:L = KuttyPyLibNano.getFreePorts(self.p.portname)
		except Exception as e:print(e)
		total = len(L)
		menuChanged = False
		if L != self.shortlist:
			menuChanged = True
			if self.p.connected:
				if self.p.portname not in L:
						self.setWindowTitle('Error : Device Disconnected')
						QtWidgets.QMessageBox.warning(self, 'Connection Error', 'Device Disconnected. Please check the connections')
						try:
							self.p.fd.close()
							self.p.portname = None
						except:pass
						self.p.connected = False
						self.setWindowTitle('KuttyPy Interactive Console [ Hardware not detected ]')

			elif True in L.values():
				reply = QtWidgets.QMessageBox.question(self, 'Connection', 'Device Available. Connect?', QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
				if reply == QtWidgets.QMessageBox.Yes:
					self.initializeCommunications()

			#update the shortlist
			self.shortlist=L

	def checkConnectionStatus(self,dialog=False):
		if self.p.connected:return True
		else:
			if dialog: QtWidgets.QMessageBox.warning(self, 'Connection Error', 'Device not connected. Please connect a KuttyPy to the USB port')
			return False
			
	def updateStatus(self):
		if not self.checkConnectionStatus():
			self.countLabel.setText('Not Connected')
			return
		try:
			state,cnt = self.p.getStatus()
			self.currentState = state
			self.countLabel.setText('%s: %d'%("Running" if state else "Paused",cnt))
		except:
			self.countLabel.setText('Disconnect!')
			self.p.fd.close()


	######## WINDOW EXPORT SVG
	def exportSvg(self):
		from utilities.Qt import QtSvg
		path, _filter  = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '~/')
		if path:
			generator = QtSvg.QSvgGenerator()
			generator.setFileName(path)
			target_rect = QtCore.QRectF(0, 0, 800, 600)
			generator.setSize(target_rect.size().toSize())#self.size())
			generator.setViewBox(self.rect())
			generator.setTitle("Your title")
			generator.setDescription("some description")
			p = QtGui.QPainter()
			p.begin(generator)
			self.render(p)
			p.end()

	def ipython(self): #Experimental feature. Import ipython and launch console
		if not self.p.connected:
			return
		from utilities import ipy
		if not self.ipy:
			self.ipy = ipy.AppWindow(self,kp = self.p)
		self.ipy.show()
		self.ipy.updateDevice(self.p)

def translators(langDir, lang=None):
	"""
	create a list of translators
	@param langDir a path containing .qm translation
	@param lang the preferred locale, like en_IN.UTF-8, fr_FR.UTF-8, etc.
	@result a list of QtCore.QTranslator instances
	"""
	if lang==None:
			lang=QtCore.QLocale.system().name()
	result=[]
	qtTranslator=QtCore.QTranslator()
	qtTranslator.load("qt_" + lang,
			QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
	result.append(qtTranslator)

	# path to the translation files (.qm files)
	sparkTranslator=QtCore.QTranslator()
	sparkTranslator.load(lang, langDir);
	result.append(sparkTranslator)
	return result

def firstExistingPath(l):
	"""
	Returns the first existing path taken from a list of
	possible paths.
	@param l a list of paths
	@return the first path which exists in the filesystem, or None
	"""
	for p in l:
		if os.path.exists(p):
			return p
	return None

def common_paths():
	"""
	Finds common paths
	@result a dictionary of common paths
	"""
	path={}
	curPath = os.path.dirname(os.path.realpath(__file__))
	path["current"] = curPath
	sharedPath = "/usr/share/kuttypy"
	path["translation"] = firstExistingPath(
			[os.path.join(p, "lang") for p in
			 (curPath, sharedPath,)])
	path["utilities"] = firstExistingPath(
			[os.path.join(p,'utilities') for p in
			 (curPath, sharedPath,)])
	path["templates"] = firstExistingPath(
			[os.path.join(p,'utilities','templates') for p in
			 (curPath, sharedPath,)])

	path["themes"] = firstExistingPath(
			[os.path.join(p,'utilities','themes') for p in
			 (curPath, sharedPath,)])

	path["examples"] = firstExistingPath(
			[os.path.join(p,'examples') for p in
			 (curPath, sharedPath,)])

	path["editor"] = firstExistingPath(
			[os.path.join(p,'editor') for p in
			 (curPath, sharedPath,)])

	lang=str(QtCore.QLocale.system().name()) 
	shortLang=lang[:2]
	return path



def run():
	global path, app, myapp
	path = common_paths()
	app = QtWidgets.QApplication(sys.argv)

	myapp = AppWindow(app=app, path=path)
	myapp.show()
	r = app.exec_()
	'''
	if myapp.p.connected:
		myapp.p.fd.write(b'j')
		#myapp.p.fd.setRTS(0)
		#time.sleep(0.01)
		#myapp.p.fd.setRTS(1)
	'''
	app.deleteLater()
	sys.exit(r)

if __name__ == "__main__":
	run()


