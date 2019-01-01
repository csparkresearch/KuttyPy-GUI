'''
'''
#!/usr/bin/python3

import os,sys,time,re
from utilities.Qt import QtGui, QtCore, QtWidgets

from utilities.templates import ui_layout as layout
from utilities import dio,PORTS
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
	ports = ['A','B','C','D']
	def __init__(self, parent=None,**kwargs):
		super(AppWindow, self).__init__(parent)
		self.setupUi(self)

		self.docks = [self.padock,self.pbdock,self.pcdock,self.pddock]
		self.monitoring = True
		self.autoUpdateUserRegisters = False
		self.registerLayout.setAlignment(QtCore.Qt.AlignTop)

		self.setTheme("material")
		examples = [a for a in os.listdir(path["examples"]) if '.py' in a]
		self.exampleList.addItems(examples)
		blinkindex = self.exampleList.findText('blink.py')
		if blinkindex!=-1: #default example. blink.py present in examples directory
			self.exampleList.setCurrentIndex(blinkindex)


		self.codeThread = QtCore.QThread()
		self.codeEval = self.codeObject()
		self.codeEval.moveToThread(self.codeThread)
		self.codeEval.finished.connect(self.codeThread.quit)
		self.codeEval.logThis.connect(self.appendLog) #Connect to the log window

		self.codeThread.started.connect(self.codeEval.execute)
		self.codeThread.finished.connect(self.codeFinished)

		self.codeThread.start()

		self.commandQ = []
		self.btns={}
		self.registers = []
		self.addPins()

		self.statusBar = self.statusBar()

		global app


		self.initializeCommunications()
		self.updatedRegs=OrderedDict()
		self.currentRegister = 0
		self.getRegs=[
		('PINA',self.updateInputs),
		('PINB',self.updateInputs),
		('PINC',self.updateInputs),
		('PIND',self.updateInputs),
		]
		self.pending = {
		'status':myTimer(constants.STATUS_UPDATE_INTERVAL),
		'update':myTimer(constants.AUTOUPDATE_INTERVAL),
		}
		
		self.startTime = time.time()
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateEverything)
		self.timer.start(50)

		
		#Auto-Detector
		self.shortlist=KuttyPyLib.getFreePorts()

	def newRegister(self):
		reg = dio.REGEDIT('DDRD',self.commandQ)
		self.registerLayout.addWidget(reg)
		self.registers.append(reg)

	def addPins(self):
		for port,dock in zip(self.ports,[self.palayout,self.pblayout,self.pclayout,self.pdlayout]):
			checkbox = dio.REGVALS(port)
			dock.addWidget(checkbox)
			self.btns[port] = checkbox

			seq = range(7,-1,-1)
			if port == 'C':seq = reversed(seq) #PORTC pins are ordered top to bottom
			for a in seq:
				name = 'P'+port+str(a)
				checkbox = dio.widget(name,self.commandQ,extra = PORTS.SPECIALS.get(name,''))
				dock.addWidget(checkbox)
				self.btns[name] = checkbox

	def tabChanged(self,index):
		if index != 0 : #examples/editor tab. disable monitoring
			self.monitoring = False
			for a in self.docks:
				a.hide()		
		else: #Playground . enable monitoring and control.
			self.monitoring = True
			for a in self.docks:
				a.show()		

	################USER CODE SECTION####################
	class codeObject(QtCore.QObject):
		finished = QtCore.pyqtSignal()
		logThis = QtCore.pyqtSignal(str)
		code = ''
		stopFlag = False
		PORTMAP = {v: k for k, v in PORTS.PORTS.items()} #Lookup port name based on number

		def __init__(self):
			super(AppWindow.codeObject, self).__init__()
			self.compiled = ''
			self.SR = None
			self.GR = None
			self.evalGlobals = {}
			self.evalGlobals['getReg']  = self.getReg
			self.evalGlobals['setReg']  = self.setReg
			self.evalGlobals['print']  = self.printer

		def setCode(self,code,SR,GR):
			self.compiled = compile(code.encode(), '<string>', mode='exec')
			self.SR = SR
			self.GR = GR

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
			exec(self.compiled,{},self.evalGlobals)
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

		self.codeEval.setCode('{0:s}'.format(self.userCode.toPlainText()),self.p.setReg, self.p.getReg)
		self.codeThread.start()

		self.userCode.setStyleSheet("border: 3px dashed #53ffff;")
		self.log.clear() #clear the log window
		self.tabs.setTabEnabled(0,False)
		self.log.setText('''<span style="color:green;">----------User Code Started-----------</span>''')

	def codeFinished(self):
		self.tabs.setTabEnabled(0,True)
		self.userCode.setStyleSheet("")

	def abort(self):
		if self.codeThread.isRunning():
			self.log.append('''<span style="color:red;">----------Kill Signal(Doesn't work yet. Restart the application)-----------</span>''')
			self.codeThread.quit()
			self.codeThread.terminate()
		

	def getReg(self,reg):
		val = self.p.getReg(reg)
		self.updatedRegs[reg] = [0,val]
		return val

	def setReg(self,reg,val):
		self.p.setReg(reg,val)
		self.updatedRegs[reg] = [1,val]
		return val

	def appendLog(self,txt):
		self.log.append(txt)

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
					<td>0x{2:02x} / 0b{2:08b}</td>
				</tr>
				'''.format(u'W \u2193' if row[0] else u'R \u2191',a,row[1])
		html+="</tbody></table>"	
		self.log.setHtml(html)

	def userRegistersAutoRefresh(self,state):
		self.autoUpdateUserRegisters = state

	def updateEverything(self):
		self.locateDevices()
		if not self.checkConnectionStatus():return
		self.setTheme("material")

		if self.codeThread.isRunning():
			return

		if self.autoUpdateUserRegisters:
			for a in self.registers:
				a.execute()
			
		if len(self.commandQ) and self.clearLog.isChecked()and self.enableLog.isChecked():
			self.log.clear()
			self.updatedRegs = OrderedDict()

		while len(self.commandQ):
			a = self.commandQ.pop(0)
			if a[0] == 'DSTATE': #Digital Out ['DSTATE','Pxx',state]
				pname = 'PORT'+a[1][1].upper()
				bit = int(a[1][2])
				reg = self.getReg(pname)
				reg &=~ (1<<bit)
				if(a[2]):reg |= (1<<bit)
				self.setReg(pname,reg);
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
				val = self.getReg(a[1]);
				a[2](val)
			elif a[0] == 'ADC': #['ADC',channel,output with setValue function]
				self.setReg('ADMUX',192|a[1]);
				self.setReg('ADCSRA',196);
				adcl = self.getReg('ADCL');
				adch = self.getReg('ADCH');
				a[2].setValue(adcl|(adch<<8))
			elif a[0] == 'CNTR1': #['CNTR1',output with setValue function]
				cl = self.getReg('TCNT1L');
				ch = self.getReg('TCNT1H');
				a[1].setValue(cl|(ch<<8))
			
			if self.enableLog.isChecked():
				self.genLog()

		if self.pending['status'].ready() and self.monitoring:
			val = self.p.getReg(self.getRegs[self.currentRegister][0])
			self.getRegs[self.currentRegister][1](self.getRegs[self.currentRegister][0],val)
			self.currentRegister +=1
			if self.currentRegister==len(self.getRegs):
				self.currentRegister = 0
			for a in self.ports:
				self.btns[a].setRegs(self.p.REGSTATES)


		if self.pending['update'].ready():
			pass
			#print('update')

	def updateInputs(self,port,value):
		portchar = port[3]
		for a in range(8):
			btn = self.btns['P'+portchar+str(a)]
			btn.nameIn.setChecked((value>>a)&1)
			if portchar == 'A': #ADC
				if btn.currentPage == 2: #ADC Page displayed
					self.commandQ.append(['ADC',a,btn.slider])
			elif type(btn)==dio.DIOCNTR and btn.currentPage==2: # CNTR
					self.commandQ.append(['CNTR1',btn.slider])

	def loadExample(self,filename):
		self.userCode.setPlainText(open(os.path.join(path["examples"],filename), "r").read())


	def setTheme(self,theme):
		self.setStyleSheet("")
		self.setStyleSheet(open(os.path.join(path["themes"],theme+".qss"), "r").read())

			
	def initializeCommunications(self,port=False):
		if self.p:
			try:self.p.fd.close()
			except:pass
		if port:
			self.p = KuttyPyLib.connect(port = port)
		else:
			self.p = KuttyPyLib.connect(autoscan=True)
		if self.p.connected:
			self.setWindowTitle('KuttyPy Interactive Console [{0:s}]'.format(self.p.portname))

		self.makeBottomMenu()


	def makeBottomMenu(self):
		try:self.pushbutton.setParent(None)
		except:pass
		self.pushbutton = QtWidgets.QPushButton('Menu')
		self.pushbutton.setStyleSheet("height: 13px;padding:3px;color: #FFFFFF;")
		menu = QtWidgets.QMenu()


		menu.addAction('Save Window as Svg', self.exportSvg)

		#Theme
		self.themeAction = QtWidgets.QWidgetAction(menu)
		themes = [a.split('.qss')[0] for a in os.listdir(path["themes"]) if '.qss' in a]
		self.themeBox = QtWidgets.QComboBox(); self.themeBox.addItems(themes)
		self.themeBox.currentIndexChanged['QString'].connect(self.setTheme)
		self.themeAction.setDefaultWidget(self.themeBox)
		menu.addAction(self.themeAction)

		self.pushbutton.setMenu(menu)
		self.statusBar.addPermanentWidget(self.pushbutton)



	def locateDevices(self):
		try:L = KuttyPyLib.getFreePorts()
		except Exception as e:print(e)
		total = len(L)
		menuChanged = False
		if L != self.shortlist:
			menuChanged = True

			if self.p.connected:
				if self.p.portname not in L:
						self.setWindowTitle('Error : Device Disconnected')
						QtWidgets.QMessageBox.warning(self, 'Connection Error', 'Device Disconnected. Please check the connections')
						try:self.p.fd.close()
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




if __name__ == "__main__":
	path = common_paths()
	app = QtWidgets.QApplication(sys.argv)
	import KuttyPyLib

	myapp = AppWindow(app=app, path=path)
	myapp.show()
	r = app.exec_()
	app.deleteLater()
	sys.exit(r)



