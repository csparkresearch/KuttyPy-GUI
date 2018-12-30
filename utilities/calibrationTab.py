from .Qt import QtGui,QtCore,QtWidgets
import numpy as np
import functools,time

from . templates import ui_calibration as calibration
from . templates import ui_calibWidget as ui_calibWidget

def htmlfy_fit(vals):
	html='''<table border="1" align="center" cellpadding="3" cellspacing="0" style="font-family:arial,helvetica,sans-serif;font-size:9pt;">
	<tbody><tr><td colspan="5" style="padding:5px;">%s</td></tr>'''%(time.ctime())

	html+='''<tr><td style="background-color:#77cfbb;">Channels</td><td style="background-color:#77cfbb;">Amplitude</td>
	<td style="background-color:#77cfbb;">Centroid</td><td style="background-color:#77cfbb;">FWHM</td><td style="background-color:#77cfbb;">Area</td></tr>'''


	for a in vals:
		html+='''
			<tr>
				<td>%s</td>
				<td>%.2f</td>
				<td>%.2f</td>
				<td>%.3f (%.1f %%)</td>
				<td>%.2f</td>
			</tr>
			'''%(a['region'],a['amplitude'],a['centroid'],a['fwhm'],100*a['fwhm']/a['centroid'],a['area'])
	html+="</tbody></table>"	
	return html

def htmlfy_p(msg,color='blue'):
	return '''<p style="color:%s;">%s</p>'''%(color,msg)
	
class calibWidget(QtGui.QWidget,ui_calibWidget.Ui_Form):
	def __init__(self,channel,energy,onDelete,updatePoly):
		super(calibWidget, self).__init__()
		self.setupUi(self)
		self.onDelete = onDelete
		self.updatePoly = updatePoly
		self.channel.setValue(channel)
		self.energy.setValue(energy)

	def onFinish(self):
		self.updatePoly()
		
	def getXY(self):
		return self.channel.value(),self.energy.value()	

	def delete(self):
		self.onDelete(self)
		self.updatePoly()

class calibrationTab(QtGui.QFrame,calibration.Ui_Frame):
	def __init__(self,onReload,*args,**kwargs):
		super(calibrationTab, self).__init__()
		self.setupUi(self)
		self.showSpectrum = kwargs.get('tabControl',None)

		#CALIBRATION ROUTINES

		self.onReload = onReload
		self.widgetLayout.setAlignment(QtCore.Qt.AlignTop)

		self.rows = []
		self.parentLabel = kwargs.get('parentLabel',None)

		#FITTING ROUTINES

		self.table.setHorizontalHeaderLabels(['Channels','Amplitude','centroid','FWHM (%)','Use for calibration'])
	
	def log(self,msg):
		self.logBrowser.append(msg)

	def returnToSpectrum(self):
		self.showSpectrum()

	#######################  CALIBRATION ROUTINES

	def reloadCalibration(self):
		self.onReload()

	def removeRow(self,R):
		R.setParent(None)
		self.rows.remove(R)

	def reloadPoints(self,points=[]):
		for R in self.rows:
			R.setParent(None)
		self.rows=[]
		for a in points:
			R = calibWidget(BIN,ENERGY,self.removeRow,self.updatePolyString)
			self.widgetLayout.addWidget(R)
			self.rows.append(R)
			
		self.updatePolyString()

		
	def addPoint(self):
		self.addPair(0,0)
		
	def addPair(self,BIN,ENERGY):
		R = calibWidget(BIN,ENERGY,self.removeRow,self.updatePolyString)
		self.widgetLayout.addWidget(R)
		self.rows.append(R)
		self.updatePolyString()

	def updatePolyString(self):
		_,p,_ = self.getPolynomial()
		self.polyLabel.setText("Calibration Polynomial : x' = %s"%(self.polystr(p)))
		self.parentLabel.setText("X' = %s"%(self.polystr(p)))
		self.log(htmlfy_p("Polynomial updated : x' = %s"%(self.polystr(p))))
		self.identifyZero()
		return self.polystr(p)

	def identifyZero(self):
		for a in self.rows:
			if a.energy.value()==0:
				a.energy.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255, 100, 100, 255), stop:0.995283 rgba(255, 200, 200, 255));");
			else:
				a.energy.setStyleSheet("");


	def polystr(self,p):
		msg = ''
		for a in range(len(p)+1):
			msg = ('%.2f '%p[a]) + ('x^%d  + '%a if a else '') + msg
		return msg


	def getPolynomial(self):
		self.identifyZero()
		try:
			msg=''
			if len(self.rows)==0:
				msg = 'No datapoints have been selected.\nThe calibration will be cleared and the x-axis will be reset to represent bins'
				self.log(htmlfy_p(msg,'green'))
				p1=np.poly1d([1,0]); p2=np.poly1d([1,0])
			elif len(self.rows)==1:
				A,B = self.rows[0].getXY()
				self.log(htmlfy_p(msg,'green'))
				p1= np.poly1d([B/A,0])
				p2= np.poly1d([A/B,0])
				msg = 'polynomial from: \nBIN\tENERGY\n0\t0\n%.1f\t%.1f\n\npolynomial : %s'%(A,B,self.polystr(p1))
			elif len(self.rows)==2:
				A,B = self.rows[0].getXY()
				A2,B2 = self.rows[1].getXY()
				p1 = np.poly1d(np.polyfit([A,A2],[B,B2],1))
				msg = 'polynomial from: \nBIN\tENERGY\n%.1f\t%.1f\n%.1f\t%.1f\n\npolynomial : %s'%(A,B,A2,B2,self.polystr(p1))
				self.log(htmlfy_p(msg,'green'))
				p2 = np.poly1d(np.polyfit([B,B2],[A,A2],1))
			elif len(self.rows)==3:
				A,B = self.rows[0].getXY()
				A2,B2 = self.rows[1].getXY()
				A3,B3 = self.rows[2].getXY()
				p1 = np.poly1d(np.polyfit([A,A2,A3],[B,B2,B3],2))
				msg = 'polynomial from: \nBIN\tENERGY\n%.1f\t%.1f\n%.1f\t%.1f\n%.1f\t%.1f\n\npolynomial : %s'%(A,B,A2,B2,A3,B3,self.polystr(p1))
				self.log(htmlfy_p(msg,'green'))
				p2 = np.poly1d(np.polyfit([B,B2,B3],[A,A2,A3],2))
			return msg,p1,p2
		except:
			self.show()
			#self.log(htmlfy_p("Could not fit, Please check the calibration datapoints",'red'))
			return "Could not fit, Please check the calibration datapoints",None,None


	##################  FITTING ROUTINES

	def setFitList(self,fitList):
		self.table.setRowCount(0); #Clear the table
		self.table.setRowCount(len(fitList))
		row=0
		self.fitList = fitList
		self.actuals = []
		self.log(htmlfy_fit(fitList))
		for a in self.fitList:
			item = QtGui.QTableWidgetItem(); self.table.setItem(row,0,item); item.setText('%s'%a['region']) #Region
			item = QtGui.QTableWidgetItem(); self.table.setItem(row,1,item); item.setText('%.2f'%a['amplitude']) #Amplitude
			item = QtGui.QTableWidgetItem(); self.table.setItem(row,2,item); item.setText('%.2f'%a['centroid']) #Centroid
			item = QtGui.QTableWidgetItem(); self.table.setItem(row,3,item); item.setText('%.3f (%.1f %%)'%(a['fwhm'],100*a['fwhm']/a['centroid'])) #FWHM


			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(":/control/plus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

			fn = functools.partial(self.applyCal,row)
			item = QtGui.QPushButton(); item.clicked.connect(fn) # Append point to calibration
			item.setIcon(icon)
			self.table.setCellWidget(row, 4, item)
			self.actuals.append(item)
			
			'''
			item = QtGui.QDoubleSpinBox();   # KeV Energy
			item.setRange(0,10000); item.setSuffix(' KeV')
			self.table.setCellWidget(row, 4, item)
			self.actuals.append(item)
			
			fn = functools.partial(self.applyCal,row)
			item = QtGui.QPushButton();item.setText('Add to Calibration'); item.clicked.connect(fn)
			self.table.setCellWidget(row, 5, item)
			'''
			row+=1




	def applyCal(self,r):
		par = self.fitList[r]
		#act = self.actuals[r].value()
		self.addPair(par['centroid'],0) #BIN, Energy
		#msg+=' Peak @ %.2f KeV with bin#%d added to calibration points!'%(act,par[2])

	

	def save(self):  #Save as CSV
		path = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '~/', 'CSV(*.csv)')
		if path:
			#check if file extension is CSV
			if path[-3:] not in ['csv','txt','dat'] :
				path+='.csv'
			self.writeToPath(path)

	def writeToPath(self,path):
		import csv
		with open(unicode(path), 'wb') as stream:
			delim = [' ','\t',',',';']
			writer = csv.writer(stream, delimiter = delim[self.delims.currentIndex()])
			headers = []
			try:
				writer.writerow(['Channels','Amplitude','centroid','FWHM'])
			except:
				pass
			#writer.writeheader()
			for row in range(len(self.fitList)):
				rowdata = []
				for column in range(self.table.columnCount()-2):
					item = self.table.item(row, column)
					if item is not None:
						rowdata.append(	unicode(item.text()).encode('utf8'))
					else:
						rowdata.append('')
				writer.writerow(rowdata)

