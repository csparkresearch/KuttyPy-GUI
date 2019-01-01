from .Qt import QtGui,QtCore,QtWidgets
from utilities.templates import ui_dio,ui_dio_pwm,ui_dio_adc,ui_regvals,ui_dio_cntr,ui_regedit
from . import PORTS

def widget(name,Q,**kwargs):
	if 'OC' in kwargs.get('extra',''):
		widget = DIOPWM(name,Q,**kwargs)
	elif 'ADC' in kwargs.get('extra',''):
		widget = DIOADC(name,Q,**kwargs)
	elif kwargs.get('extra','') in ['T1']: #Counters
		widget = DIOCNTR(name,Q,**kwargs)
	else: #Regular D IO
		widget = DIO(name,Q,**kwargs)
	widget.setProperty("class", name)
	return widget

class REGVALS(QtWidgets.QFrame,ui_regvals.Ui_Frame):
	def __init__(self,name):
		super(REGVALS, self).__init__()
		self.setupUi(self)
		self.name = name
		self.DDR = 'DDR'+name
		self.PORT = 'PORT'+name
		self.PIN  = 'PIN' + name
		self.reglist = {}
		self.format = '{0:d}'
		self.L1.setText('%s\n-'%(self.DDR))
		self.L2.setText('%s\n-'%(self.PORT))
		self.L3.setText('%s\n-'%(self.PIN))

	def setRegs(self,reglist):
		if self.DDR in reglist:
			self.L1.setText('%s\n%s'%(self.DDR,self.format.format(reglist.get(self.DDR))) )
		if self.PORT in reglist:
			self.L2.setText('%s\n%s'%(self.PORT,self.format.format(reglist.get(self.PORT))) )
		if self.PIN in reglist:
			self.L3.setText('%s\n%s'%(self.PIN,self.format.format(reglist.get(self.PIN))) )
		self.reglist = reglist

	def mousePressEvent(self, event):
		if self.format == '{0:d}':
			self.format = '{0:08b}'
		elif self.format == '{0:08b}':
			self.format = '0x{0:02X}'
		elif self.format == '0x{0:02X}':
			self.format = '{0:d}'
		self.setRegs(self.reglist)

class DIO(QtWidgets.QStackedWidget,ui_dio.Ui_stack):
	def __init__(self,name,Q,**kwargs):
		super(DIO, self).__init__()
		self.setupUi(self)
		self.name = name
		self.Q = Q #Command Queue
		self.nameOut.setText(name)
		self.nameIn.setText(name)
		self.nameIn.setEnabled(False)
		self.currentPage = 0
		
	def next(self):
		self.currentPage+=1
		if self.currentPage >= self.count():
			self.currentPage = 0
		self.setCurrentIndex(self.currentPage)
		self.initPage()

	def initPage(self):
		if self.currentPage == 0: #Input
			self.Q.append(['DTYPE',self.name,0])
		elif self.currentPage == 1: #Output
			self.Q.append(['DTYPE',self.name,1])

	def setOutputState(self,state):
		self.nameOut.setChecked(state)
		self.pullup.setChecked(state)
		self.Q.append(['DSTATE',self.name,state])


class DIOPWM(QtWidgets.QStackedWidget,ui_dio_pwm.Ui_stack):
	def __init__(self,name,Q,**kwargs):
		super(DIOPWM, self).__init__()
		self.setupUi(self)
		self.name = name
		self.type = kwargs.get('extra','')
		if self.type == 'OC0':
			self.slider.setMaximum(255)
		elif self.type == 'OC2':
			self.slider.setMaximum(255)
		elif self.type == 'OC1A':
			self.slider.setMaximum(1023)
		
		self.Q = Q #Command Queue
		self.nameOut.setText(name)
		self.nameIn.setText(name)
		self.nameIn.setEnabled(False)
		self.currentPage = 0
		
	def next(self):
		if self.currentPage == 2: #Disable PWM
			if self.type == 'OC0':
				self.Q.append(['WRITE','TCCR0',0])
			elif self.type == 'OC2':
				self.Q.append(['WRITE','TCCR2',0])
				self.Q.append(['WRITE','TCNT2',0])
			elif self.type == 'OC1A':
				self.Q.append(['WRITE','TCCR1A',0])
				self.Q.append(['WRITE','TCCR1B',0])
		self.currentPage+=1
		if self.currentPage >= self.count():
			self.currentPage = 0
		self.setCurrentIndex(self.currentPage)
		self.initPage()

	def initPage(self):
		if self.currentPage == 2: #PWM
			self.Q.append(['DTYPE',self.name,1]) #Set it as output
			if self.type == 'OC0':
				self.Q.append(['WRITE','TCCR0',105])
			elif self.type == 'OC2':
				self.Q.append(['WRITE','TCCR2',105])
				self.Q.append(['WRITE','TCNT2',0])
			elif self.type == 'OC1A':
				self.Q.append(['WRITE','TCCR1A',131])
				self.Q.append(['WRITE','TCCR1B',1])


		if self.currentPage == 0: #Input
			self.Q.append(['DTYPE',self.name,0])
		elif self.currentPage == 1: #Output
			self.Q.append(['DTYPE',self.name,1])

	def setOutputState(self,state):
		self.nameOut.setChecked(state)
		self.pullup.setChecked(state)
		self.Q.append(['DSTATE',self.name,state])

	def setpwm(self,val):
		if self.type == 'OC0':
			self.Q.append(['WRITE','OCR0',val]) 
		elif self.type == 'OC2':
			self.Q.append(['WRITE','OCR2',val]) 
		elif self.type == 'OC1A':
			self.Q.append(['WRITE','OCR1AH',(val>>8)&0x3]) 
			self.Q.append(['WRITE','OCR1AL',(val)&0xFF]) 



class DIOADC(QtWidgets.QStackedWidget,ui_dio_adc.Ui_stack):
	def __init__(self,name,Q,**kwargs):
		super(DIOADC, self).__init__()
		self.setupUi(self)
		self.name = name
		
		self.Q = Q #Command Queue
		self.nameOut.setText(name)
		self.nameIn.setText(name)
		self.nameIn.setEnabled(False)
		self.currentPage = 0
		
	def next(self):
		self.currentPage+=1
		if self.currentPage >= self.count():
			self.currentPage = 0
		self.setCurrentIndex(self.currentPage)
		self.initPage()

	def initPage(self):
		if self.currentPage == 0 or self.currentPage == 2: #Input or ADC
			self.Q.append(['DTYPE',self.name,0])
		elif self.currentPage == 1: #Output
			self.Q.append(['DTYPE',self.name,1])

	def setOutputState(self,state):
		self.nameOut.setChecked(state)
		self.pullup.setChecked(state)
		self.Q.append(['DSTATE',self.name,state])


class DIOCNTR(QtWidgets.QFrame,ui_dio_cntr.Ui_Frame):
	def __init__(self,name,Q,**kwargs):
		super(DIOCNTR, self).__init__()
		self.setupUi(self)
		self.name = name
		
		self.Q = Q #Command Queue
		self.nameOut.setText(name)
		self.nameIn.setText(name)
		self.nameIn.setEnabled(False)
		self.currentPage = 0
		
	def setPage(self,page):
		self.currentPage=page
		self.stack.setCurrentIndex(self.currentPage)
		self.initPage()

	def setThreshold(self,val):
			self.thresLabel.setText(str(val)+u'\u21c6')
			self.Q.append(['WRITE','OCR1AH',(val>>8)&0xFF]) 
			self.Q.append(['WRITE','OCR1AL',(val)&0xFF]) 

	def initPage(self):
		if self.currentPage == 0 or self.currentPage == 2: #Input or CNTR INPUT
			self.Q.append(['DTYPE',self.name,0])
		elif self.currentPage == 1: #Output
			self.Q.append(['DTYPE',self.name,1])

		if self.currentPage == 2: #CNTR Input
				self.Q.append(['DTYPE','PD5',1])   #Set PD0 to output
				self.Q.append(['WRITE','TCNT1H',0]) # 
				self.Q.append(['WRITE','TCNT1L',0]) # 
				self.setThreshold(self.thresholdSlider.value())
				self.Q.append(['WRITE','TCCR1B',7]) # 0b111 - External clock input on T1
				self.Q.append(['WRITE','TCCR1A',64|4]) #Toggle PD5
				self.thresLabel.setText(u'PD5\u21c6')


	def setOutputState(self,state):
		self.nameOut.setChecked(state)
		self.pullup.setChecked(state)
		self.Q.append(['DSTATE',self.name,state])

class REGEDIT(QtWidgets.QFrame,ui_regedit.Ui_Frame):
	def __init__(self,name,Q):
		super(REGEDIT, self).__init__()
		self.setupUi(self)
		self.name = name
		self.Q = Q
		self.regName.addItems(PORTS.PORTS.keys())
		self.type = 0 # 0=read. 1 =write
		self.bits = [self.b0,self.b1,self.b2,self.b3,self.b4,self.b5,self.b6,self.b7]
		for a in self.bits:
			a.clicked.connect(self.valueRefresh)
			a.setEnabled(self.type)

		self.labels = [self.l0,self.l1,self.l2,self.l3,self.l4,self.l5,self.l6,self.l7]
		self.format = '{0:d}'
		self.valueLabel.mousePressEvent = self.valueMouseClick
		self.typeLabel.mousePressEvent = self.changeType

	def execute(self):
		if self.type: #In write mode
			self.Q.append(['WRITE',str(self.regName.currentText()),self.getValue()])
		else:
			self.Q.append(['READ',str(self.regName.currentText()),self.setValue])

	def changeType(self,event):
		if self.type: #Was in write mode
			self.type = 0 #Change to read mode
			self.typeLabel.setText(u'READ\u2191')
		else:
			self.type = 1 #Change to write mode
			self.typeLabel.setText(u'WRITE\u2193')
		for a in self.bits:
			a.setEnabled(self.type)

	def getValue(self):
		val = 0
		for a in reversed(self.bits):
			val = val<<1
			if a.isChecked(): val|=1
		return val

	def setValue(self,val):
		for a in self.bits:
			a.setChecked(val&1)
			val =val>>1

	def valueMouseClick(self, event):
		if self.format == '{0:d}':
			self.format = '{0:08b}'
		elif self.format == '{0:08b}':
			self.format = '0x{0:02X}'
		elif self.format == '0x{0:02X}':
			self.format = '{0:d}'
		self.valueRefresh()

	def valueRefresh(self):
		self.valueLabel.setText(self.format.format(self.getValue()))




