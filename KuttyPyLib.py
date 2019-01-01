'''
Code snippet for reading data from the 1024 bin MCA

'''
import serial, struct, time,platform,os,sys
from utilities import PORTS

if 'inux' in platform.system(): #Linux based system
	import fcntl

Byte =     struct.Struct("B") # size 1
ShortInt = struct.Struct("H") # size 2
Integer=   struct.Struct("I") # size 4

def _bv(x):
	return 1<<x

def connect(**kwargs):
	return KUTTYPY(**kwargs)


def listPorts():
	'''
	Make a list of available serial ports. For auto scanning and connecting
	'''
	import glob
	system_name = platform.system()
	if system_name == "Windows":
		# Scan for available ports.
		available = []
		for i in range(256):
			try:
				s = serial.Serial('COM%d'%i)
				available.append('COM%d'%i)
				s.close()
			except serial.SerialException:
				pass
		return available
	elif system_name == "Darwin":
		# Mac
		return glob.glob('/dev/tty*') + glob.glob('/dev/cu*')
	else:
		# Assume Linux or something else
		return glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')

def isPortFree(portname):
	try:
		fd = serial.Serial(portname, KUTTYPY.BAUD, stopbits=1, timeout = 1.0)
		if fd.isOpen():
			if 'inux' in platform.system(): #Linux based system
				try:
					fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
					fd.close()
					return True #Port is available
				except IOError:
					fd.close()
					return False #Port is not available

			else:
				fd.close()
				return True #Port is available
		else:
			fd.close()
			return False #Port is not available

	except serial.SerialException as ex:
		return False #Port is not available

def getFreePorts():
	'''
	Find out which ports are currently free 
	'''
	portlist={}
	for a in listPorts():
		portlist[a] = isPortFree(a)
	return portlist


class KUTTYPY:	
	VERSIONNUM = Byte.pack(99)
	GET_VERSION = Byte.pack(1)
	READB =   Byte.pack(2)
	WRITEB =   Byte.pack(3)

	BAUD = 38400
	version = 0
	REGS = PORTS.PORTS # A map of alphanumeric port names to the 8-bit register locations
	REGSTATES = {} #Store the last written state of the registers
	SPECIALS = PORTS.SPECIALS
	def __init__(self,**kwargs):
		self.connected=False
		if 'port' in kwargs:
			self.portname=kwargs.get('port',None)
			try:
				self.fd,self.version,self.connected=self.connectToPort(self.portname)
				if self.connected:
					self.fd.setRTS(0)
					for a in ['A','B','C','D']: #Initialize all inputs
						self.setReg('DDR'+a,0)
					return
			except Exception as ex:
				print('Failed to connect to ',self.portname,ex.message)
				
		elif kwargs.get('autoscan',False):	#Scan and pick a port	
			portList = getFreePorts()
			for a in portList:
				if portList[a]:
					try:
						self.portname=a
						self.fd,self.version,self.connected=self.connectToPort(self.portname)
						if self.connected:
							self.fd.setRTS(0)
							for a in ['A','B','C','D']: #Initialize all inputs
								self.setReg('DDR'+a,0) #All inputs
								self.setReg('PORT'+a,0) #No Pullup
							return
					except Exception as e:
						print (e)
				else:
					print(a,' is busy')


	def __get_version__(self,fd):
		fd.write(self.GET_VERSION)
		return fd.read()

	def get_version(self):
		return self.__get_version__(self.fd)


	def connectToPort(self,portname):
		'''
		connect to a port, and check for the right version
		'''

		try:
			fd = serial.Serial(portname, self.BAUD, stopbits=1, timeout = 1.0)
			if fd.isOpen():
				#try to lock down the serial port
				if 'inux' in platform.system(): #Linux based system
					import fcntl
					try:
						fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
						#print ('locked access to ',portname,fd.fileno())
					except IOError:
						#print ('Port {0} is busy'.format(portname))
						return None,'',False

				else:
					pass
					#print ('not on linux',platform.system())

				if(fd.inWaiting()):
					fd.setTimeout(0.1)
					fd.read(1000)
					fd.flush()
					fd.setTimeout(1.0)

			else:
				#print('unable to open',portname)
				return None,'',False

		except serial.SerialException as ex:
			print ('Port {0} is unavailable: {1}'.format(portname, ex) )
			return None,'',False

		version = self.__get_version__(fd)
		if len(version)==1:
			if ord(version)==ord(self.VERSIONNUM):
				return fd,version,True
		print ('version check failed',len(version),version)
		return None,'',False
		

	def __sendByte__(self,val):
		"""
		transmits a BYTE
		val - byte to send
		"""
		#print (val)
		if(type(val)==int):
			self.fd.write(Byte.pack(val))
		else:
			self.fd.write(val)

	def __getByte__(self):
		"""
		reads a byte from the serial port and returns it
		"""
		ss=self.fd.read(1)
		if len(ss): return Byte.unpack(ss)[0]
		else:
			print('byte communication error.',time.ctime())
			return 0

	def setReg(self,reg, data):
		#print(reg,data)
		self.REGSTATES[reg] = data
		self.__sendByte__(self.WRITEB)
		if reg in self.REGS:
			self.__sendByte__(self.REGS[reg])
		else:
			self.__sendByte__(reg)
		self.__sendByte__(data)

	def getReg(self,reg):
		self.__sendByte__(self.READB)
		if reg in self.REGS:
			self.__sendByte__(self.REGS[reg])
		else:
			self.__sendByte__(reg)
		val = self.__getByte__()
		self.REGSTATES[reg] = val
		return val

	def readADC(self,ch):        # Read the ADC channel
		self.setReg(self.REGS.ADMUX, self.REGS.REF_INT | ch)
		self.setReg(self.REGS.ADCSRA, 1 << self.REGS.ADEN | (1 << self.REGS.ADSC) | self.REGS.ADC_SPEED)		# Enable the ADC
		low = self.getReg(self.REGS.ADCL);
		hi = self.getReg(self.REGS.ADCH);
		return (hi << 8) | low

if __name__ == '__main__':
	a=connect(autoscan=True)
	print ('version' , a.version)
	print ('------------')
