from .Qt import QtGui,QtCore,QtWidgets
from utilities.templates import ui_dio,ui_dio_pwm,ui_dio_adc,ui_dio_adcConfig,ui_dio_sensor,ui_regvals,ui_dio_cntr,ui_regedit,ui_dio_control
from utilities.templates import ui_dio_robot

from . import REGISTERS
from utilities.templates.gauge import Gauge
import numpy as np
from functools import partial
from collections import OrderedDict
import time

colors=[(0,255,0),(255,0,0),(255,255,100),(10,255,255)]+[(50+np.random.randint(200),50+np.random.randint(200),150+np.random.randint(100)) for a in range(10)]

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


class DIOADCCONFIG(QtWidgets.QDialog,ui_dio_adcConfig.Ui_Dialog):
	def __init__(self,parent,name,opts,logstate,accepted):
		super(DIOADCCONFIG, self).__init__(parent)
		self.setupUi(self)
		self.setWindowTitle('Configure ADC Pin : %s'%parent.name)
		self.label.setText(name)
		self.scale = 1.
		self.log.setChecked(logstate)
		self.options.addItems(opts)
		self.onFinished = accepted
		self.gauge.update_value(200)
		self.gauge.set_MaxValue(1023)
		self.options.currentIndexChanged['QString'].connect(self.update)

	def changeRange(self,state):
		self.scale = 5000./1023. if state else 1.
		self.gauge.set_MaxValue(5000. if state else 1023)

	def setValue(self,val):
		self.gauge.update_value(val*self.scale)

	def update(self,i):
		self.onFinished(i,self.log.isChecked())

	def accept(self):
		self.onFinished(self.options.currentText(),self.log.isChecked())
		self.close()

class DIOADC(QtWidgets.QStackedWidget,ui_dio_adc.Ui_stack):
	def __init__(self,name,Q,**kwargs):
		super(DIOADC, self).__init__()
		self.setupUi(self)
		self.name = name
		self.configWindow = None
		self.chan = int(self.name[2])
		self.logstate = False
		self.ADMUX = 64|self.chan #  AREF With Capacitor | PA[x]
		self.muxOptions = {
			self.name:self.chan,
			'ADC1-ADC0 @10x':0b01001,
			'ADC1-ADC0 @200x':0b01011,
			'ADC3-ADC2 @10x':0b01101,
			'ADC3-ADC2 @200x':0b01111,
			self.name+'-ADC1 @1x':0b10000|self.chan,
			'1.22V(BandGap Reference)':0b11110,
			'0V (Ground)':0b11111,
		}
		self.Q = Q #Command Queue
		self.nameOut.setText(name)
		self.nameIn.setText(name)
		self.nameIn.setEnabled(False)
		self.currentPage = 0
		self.lcdNumber.mousePressEvent = self.config

	def config(self,evt):
		if not self.configWindow:
			self.configWindow = DIOADCCONFIG(self,'ADMUX',self.muxOptions.keys(),self.logstate,self.setConfig)
		#self.configWindow.exec_() #Blocks UI (Modal), and only one instance can be shown
		self.configWindow.show() # Non blocking. Multiple.

	def setConfig(self,val,log):
		self.ADMUX = 64|self.muxOptions.get(val,self.chan)
		self.logstate = log

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

	def setValue(self,val):
		self.slider.setValue(val)
		if self.configWindow:
			self.configWindow.setValue(val)
		
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
	def __init__(self,Q):
		super(REGEDIT, self).__init__()
		self.setupUi(self)
		self.Q = Q
		self.regName.addItems([k for k in REGISTERS.VERSIONS[99]['REGISTERS'].keys() if k not in REGISTERS.VERSIONS[99]['RESTRICTED_REGISTERS']])

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


class DIOSENSOR(QtWidgets.QDialog,ui_dio_sensor.Ui_Dialog):
	def __init__(self,parent,sensor):
		super(DIOSENSOR, self).__init__(parent)
		name = sensor['name']
		self.initialize = sensor['init']
		self.read = sensor['read']
		self.setupUi(self)
		self.currentPage = 0
		self.scale = 1.
		self.max = sensor.get('max',None)
		self.min = sensor.get('min',None)
		self.fields = sensor.get('fields',None)
		self.widgets =[]
		for a in sensor.get('config',[]): #Load configuration menus
			l = QtWidgets.QLabel(a.get('name',''))
			self.configLayout.addWidget(l) ; self.widgets.append(l)
			l = QtWidgets.QComboBox(); l.addItems(a.get('options',[]))
			l.currentIndexChanged['int'].connect(a.get('function',None))
			self.configLayout.addWidget(l) ; self.widgets.append(l)
			
		self.graph.setRange(xRange=[-300, 0])
		self.curves = {}
		self.gauges = {}
		self.datapoints=0
		row = 1; col=1;
		for a,b,c in zip(self.fields,self.min,self.max):
			gauge = Gauge(self)
			gauge.setObjectName(a)
			gauge.set_MinValue(b)
			gauge.set_MaxValue(c)
			#listItem = QtWidgets.QListWidgetItem()
			#self.listWidget.addItem(listItem)
			#self.listWidget.setItemWidget(listItem, gauge)
			self.gaugeLayout.addWidget(gauge,row,col)
			col+= 1
			if col == 4:
				row += 1
				col = 1
			self.gauges[gauge] = [a,b,c] #Name ,min, max value
			
			curve = self.graph.plot(pen=colors[len(self.curves.keys())])
			self.curves[curve] = np.empty(300)
		
		self.setWindowTitle('Sensor : %s'%name)

	def next(self):
		if self.currentPage==1:
			self.currentPage = 0
			self.switcher.setText("Data Logger")
		else:
			self.currentPage = 1
			self.switcher.setText("Analog Gauge")

		self.monitors.setCurrentIndex(self.currentPage)

	def changeRange(self,state):
		for a in self.gauges:
			self.scale = self.gauges[a][1]/65535. if state else 1.
			a.set_MaxValue(self.gauges[a][1] if state else 65535)

	def setValue(self,vals):
		if vals is None:
			print('check connections')
			return
		if self.currentPage == 0: #Update Analog Gauges
			p=0
			for a in self.gauges:
				a.update_value(vals[p]*self.scale)
				p+=1
		elif self.currentPage == 1: #Update Data Logger
			p=0
			for a in self.curves:
				self.curves[a][self.datapoints] = vals[p] * self.scale
				if not p: self.datapoints += 1 #Increment datapoints once per set. it's shared

				if self.datapoints >= self.curves[a].shape[0]-1:
					tmp = self.curves[a]
					self.curves[a] = np.empty(self.curves[a].shape[0] * 2) #double the size
					self.curves[a][:tmp.shape[0]] = tmp
				a.setData(self.curves[a][:self.datapoints])
				a.setPos(-self.datapoints, 0)
				p+=1

	def launch(self):
		self.initialize()
		self.show()


class DIOCONTROL(QtWidgets.QDialog,ui_dio_control.Ui_Dialog):
	def __init__(self,parent,sensor):
		super(DIOCONTROL, self).__init__(parent)
		name = sensor['name']
		self.initialize = sensor['init']
		self.setupUi(self)
		self.widgets =[]
		self.gauges = {}
		self.functions = {}

		for a in sensor.get('write',[]): #Load configuration menus
			l = QtWidgets.QSlider(self); l.setMinimum(a[1]); l.setMaximum(a[2]);l.setValue(a[3]);
			l.setOrientation(QtCore.Qt.Horizontal)
			l.valueChanged['int'].connect(partial(self.write,l))
			self.configLayout.addWidget(l) ; self.widgets.append(l)
			
			gauge = Gauge(self)
			gauge.setObjectName(a[0])
			gauge.set_MinValue(a[1])
			gauge.set_MaxValue(a[2])
			gauge.update_value(a[3])
			self.gaugeLayout.addWidget(gauge)
			self.gauges[l] = gauge #Name ,min, max value,default value, func
			self.functions[l] = a[4]
			
		self.setWindowTitle('Control : %s'%name)

	def write(self,w,val):
		self.gauges[w].update_value(val)
		self.functions[w](val)


	def launch(self):
		self.initialize()
		self.show()




class DIOROBOT(QtWidgets.QDialog,ui_dio_robot.Ui_Dialog):
	def __init__(self,parent,sensor):
		super(DIOROBOT, self).__init__(parent)
		name = sensor['name']
		self.initialize = sensor['init']
		self.setupUi(self)
		self.widgets =[]
		self.gauges = OrderedDict()
		self.lastPos = OrderedDict()
		self.functions = OrderedDict()
		self.positions = []

		for a in sensor.get('write',[]): #Load configuration menus
			l = QtWidgets.QSlider(self); l.setMinimum(a[1]); l.setMaximum(a[2]);l.setValue(a[3]);
			l.setOrientation(QtCore.Qt.Horizontal)
			l.valueChanged['int'].connect(partial(self.write,l))
			self.configLayout.addWidget(l) ; self.widgets.append(l)
			
			gauge = Gauge(self)
			gauge.setObjectName(a[0])
			gauge.set_MinValue(a[1])
			gauge.set_MaxValue(a[2])
			gauge.update_value(a[3])
			self.lastPos[l] = a[3]
			self.gaugeLayout.addWidget(gauge)
			self.gauges[l] = gauge #Name ,min, max value,default value, func
			self.functions[l] = a[4]
			
		self.setWindowTitle('Control : %s'%name)

	def write(self,w,val):
		self.gauges[w].update_value(val)
		self.lastPos[w] = val
		self.functions[w](val)

	def add(self):
		self.positions.append([a.value() for a in self.lastPos.keys()])
		item = QtWidgets.QListWidgetItem("%s" % str(self.positions[-1]))
		self.listWidget.addItem(item)
		print(self.positions)

	def play(self):
		mypos = [a.value() for a in self.lastPos.keys()] # Current position
		sliders = list(self.gauges.keys())
		for nextpos in self.positions:
			dx = [(x-y) for x,y in zip(nextpos,mypos)]  #difference between next position and current
			distance = max(dx)
			for travel in range(20):
				for step in range(4):
						self.write(sliders[step],int(mypos[step]))
						mypos[step] += dx[step]/20.
				time.sleep(0.01)
							
						

	def launch(self):
		self.initialize()
		self.show()

