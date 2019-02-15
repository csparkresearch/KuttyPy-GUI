from ..Qt import QtGui,QtCore,QtWidgets

class Guage(QtWidgets.QWidget):
	valueChanged = QtCore.pyqtSignal(float)
	def __init__(self, parent=None):
		super(Guage, self).__init__(parent)
		self.setWindowTitle("Analog Clock")
		self.L=285.
		self.resize(self.L, self.L)
		self.hand = QtGui.QPolygon([
			QtCore.QPoint(7, 8),
			QtCore.QPoint(-7, 8),
			QtCore.QPoint(0, -80)
		])
		self.color = QtGui.QColor(40, 127, 57, 210)
		self.mcolor = QtGui.QColor(0, 255, 127, 191)
		self.min = 0.
		self.max = 100.
		self.range = self.max - self.min
		self.value = 100.

	def paintEvent(self, event):
		side = min(self.width(), self.height())

		painter = QtGui.QPainter()
		painter.begin(self)
		painter.setRenderHint(QtGui.QPainter.Antialiasing)
		painter.translate(self.width() / 2, self.height() / 2)
		painter.scale(side / self.L, side / self.L)

		painter.setPen(QtCore.Qt.NoPen)
		painter.setBrush(QtGui.QBrush(self.color))

		painter.save()
		painter.rotate(250*(self.value/self.range)-125)
		painter.drawConvexPolygon(self.hand)
		painter.restore()

		painter.setPen(self.color)
		txt = str(self.value)
		painter.setFont(QtGui.QFont("Helvetica", 30))
		painter.drawText(QtCore.QPoint(-10*len(txt), 95), txt)

		painter.rotate(145)
		for i in range(0, 11):
			painter.drawLine(85, 0, 96, 0)
			painter.rotate(25.0)

		painter.setPen(QtGui.QPen(self.mcolor))
		painter.rotate(85)
		for i in range(0, 51):
			painter.drawLine(92, 0, 96, 0)
			painter.rotate(5.0)

		painter.setFont(QtGui.QFont("Helvetica", 10))
		painter.setPen(QtGui.QPen(self.color))
		painter.rotate(-125)
		for i in range(5, 11):
			painter.drawText(QtCore.QPoint(97, 0), str(self.range*i/10));
			painter.rotate(25)

		painter.rotate(260)
		for i in range(5):
			txt = str(self.range*i/10)
			painter.drawText(QtCore.QPoint(-90-len(txt)*10, 0), txt);
			painter.rotate(25)
		painter.end()

	def minimumSizeHint(self):
		return QtCore.QSize(50, 50)

	def sizeHint(self):
		return QtCore.QSize(100, 100)

	def updateValue(self,val):
		self.valueChanged.emit(val)
