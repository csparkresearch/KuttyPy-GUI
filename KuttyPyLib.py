'''
Code snippet for reading data from the 1024 bin MCA

'''
import serial, struct, time,platform,os,sys
from utilities import REGISTERS
from numpy import int16,std

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

def getFreePorts(openPort=None):
	'''
	Find out which ports are currently free 
	'''
	portlist={}
	for a in listPorts():
		if a != openPort:
			portlist[a] = isPortFree(a)
		else:
			portlist[a] = False
	return portlist


class KUTTYPY:	
	VERSIONNUM = Byte.pack(99)
	GET_VERSION = Byte.pack(1)
	READB =   Byte.pack(2)
	WRITEB =   Byte.pack(3)
	I2C_READ  =   Byte.pack(4)
	I2C_WRITE =   Byte.pack(5)
	I2C_SCAN  =   Byte.pack(6)

	BAUD = 38400
	version = 0
	portname = None
	REGS = REGISTERS.VERSIONS[99]['REGISTERS'] # A map of alphanumeric port names to the 8-bit register locations
	REGSTATES = {} #Store the last written state of the registers
	SPECIALS = REGISTERS.VERSIONS[99]['SPECIALS']
	def __init__(self,**kwargs):
		self.sensors={
			0x39:{
				'name':'TSL2561',
				'init':self.TSL2561_init,
				'read':self.TSL2561_all,
				'fields':['total','IR'],
				'min':[0,0],
				'max':[2**15,2**15]},
			0x68:{
				'name':'MPU6050',
				'init':self.MPU6050_init,
				'read':self.MPU6050_all,
				'fields':['Ax','Ay','Az','Temp','Gx','Gy','Gz'],
				'min':[-1*2**15,-1*2**15,-1*2**15,0,-1*2**15,-1*2**15,-1*2**15],
				'max':[2**15,2**15,2**15,100,2**15,2**15,2**15]}
		}
		self.connected=False
		if 'port' in kwargs:
			self.portname=kwargs.get('port',None)
			try:
				self.fd,self.version,self.connected=self.connectToPort(self.portname)
				if self.connected:
					#self.fd.setRTS(0)
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
							#self.fd.setRTS(0)
							for a in ['A','B','C','D']: #Initialize all inputs
								self.setReg('DDR'+a,0) #All inputs
								self.setReg('PORT'+a,0) #No Pullup
							self.setReg('PORTC',3) #I2C Pull-Up
							return
					except Exception as e:
						print (e)
				else:
					print(a,' is busy')


	def __get_version__(self,fd):
		fd.setRTS(0)
		time.sleep(0.01)
		fd.setRTS(1)
		time.sleep(0.25)
		while fd.in_waiting:
			fd.read(fd.in_waiting)
		fd.write(self.GET_VERSION)
		return fd.read()

	def get_version(self):
		return self.__get_version__(self.fd)


	def connectToPort(self,portname):
		'''
		connect to a port, and check for the right version
		'''

		try:
			fd = serial.Serial(portname, self.BAUD, timeout = 0.5)
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

				if(fd.in_waiting):
					fd.flush()
					fd.readall()

			else:
				#print('unable to open',portname)
				return None,'',False

		except serial.SerialException as ex:
			print ('Port {0} is unavailable: {1}'.format(portname, ex) )
			return None,'',False

		version = self.__get_version__(fd)
		if len(version)==1:
			if ord(version)==ord(self.VERSIONNUM):
				return fd,ord(version),True
		print ('version check failed',len(version),version)
		return None,'',False
		

	def __sendByte__(self,val):
		"""
		transmits a BYTE
		val - byte to send
		"""
		#print (val)
		try:
			if(type(val)==int):
				self.fd.write(Byte.pack(val))
			else:
				self.fd.write(val)
		except:
			self.connected = False

	def __getByte__(self):
		"""
		reads a byte from the serial port and returns it
		"""
		try:
			ss=self.fd.read(1)
		except:
			self.connected = False
			print('No byte received. Disconnected?',time.ctime())
			return 0
		if len(ss): return Byte.unpack(ss)[0]
		else:
			print('byte communication error.',time.ctime())
			return None

	def setReg(self,reg, data):
		#print(reg,data)
		self.REGSTATES[reg] = data
		self.__sendByte__(self.WRITEB)
		if reg in self.REGS:
			self.__sendByte__(self.REGS[reg])
		else:
			print('missing register',reg)
			self.__sendByte__(reg)
		self.__sendByte__(data)

	def getReg(self,reg):
		self.__sendByte__(self.READB)
		if reg in self.REGS:
			self.__sendByte__(self.REGS[reg])
		else:
			print('missing register',reg)
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

	'''
	# I2C Calls. Will be replaced with firmware level implementation
	def initI2C(self): # Initialize I2C
		self.setReg('TWSR',0x00)
		self.setReg('TWBR',0x46)
		self.setReg('TWCR',0x04)

	def startI2C(self): 
		self.setReg('TWCR',(1<<7)|(1<<5) | (1<<2))
		timeout=10 #20mS
		time.sleep(0.001)
		while (not(self.getReg('TWCR') & (1<<7))):
			timeout-=1
			print('waiy')
			if timeout==0:
				print('start timeout')
				break
			time.sleep(0.001)

	def stopI2C(self):
		self.setReg('TWCR',(1<<7) | (1<<4) | (1<<2))
		timeout=10 #20mS
		time.sleep(0.001)

	def writeI2C(self,val):
		self.setReg('TWDR',val)
		self.setReg('TWCR',(1<<7) | (1<<2))
		timeout=20 #20mS
		while (not(self.getReg('TWCR') & (1<<7))):
			timeout-=1
			if timeout==0:
				print ('write timeout')
				break
			time.sleep(0.001)

	def readI2C(self,ack):
		self.setReg('TWCR',(1<<7) | (1<<2) | (ack<<6))
		timeout=20 #20mS
		while (not(self.getReg('TWCR') & (1<<7))):
			timeout-=1
			if timeout==0:
				print ('read timeout')
				break
			time.sleep(0.001)
		if timeout:
			return self.getReg('TWDR')
		else:
			return None

	def I2CWriteBulk(self,address,bytestream): 
		# Individual register write based writing. takes a few hundred milliseconds
		self.startI2C()
		self.writeI2C(address<<1)
		for a in bytestream:
			self.writeI2C(a) 
		self.stopI2C()

	def I2CReadBulk(self,address,register,total): 
		# Individual register write based reading. takes a few hundred milliseconds
		self.startI2C()
		self.writeI2C(address<<1)
		self.writeI2C(register)
		self.startI2C()
		self.writeI2C((address<<1)|1) #Read
		b=[]
		for a in range(total-1):
			b.append(self.readI2C(1) )
		b.append(self.readI2C(0))
		self.stopI2C()
		return b

	# Individual register write based scan. takes a few seconds
	def I2CScan(self):
		found = []
		for a in range(127):
			self.startI2C()
			time.sleep(0.005)
			self.writeI2C(a<<1)
			time.sleep(0.005)
			if self.getReg('TWSR') == 0x18:
				found.append(a)
		self.stopI2C()
		return found
	'''
	def I2CScan(self):
		self.__sendByte__(self.I2C_SCAN)
		addrs = []
		val = self.__getByte__()
		if val is None:
			return []
		while val<127:
			addrs.append(val)
			val = self.__getByte__()
		if(val==254):print('timed out')
		return addrs

	def I2CWriteBulk(self,address,bytestream): 
		self.__sendByte__(self.I2C_WRITE)
		self.__sendByte__(address) #address
		self.__sendByte__(len(bytestream)) #Total bytes to write. <=255
		for a in bytestream:
			self.__sendByte__(Byte.pack(a))
		tmt = self.__getByte__()		
		if tmt: return True #Hasn't Timed out.
		else: return False   #Timeout occured

	def I2CReadBulk(self,address,register,total): 
		self.__sendByte__(self.I2C_READ)
		self.__sendByte__(address) #address
		self.__sendByte__(register) #device register address
		self.__sendByte__(total) #Total bytes to read. <=255
		data = []
		for a in range(total):
			val = self.__getByte__()
			data.append(val)
		tmt = self.__getByte__()		
		return data,True if not tmt else False

	def MPU6050_init(self):
		self.I2CWriteBulk(0x68,[0x1B,3<<3]) #Gyro Range . 2000
		self.I2CWriteBulk(0x68,[0x1C,3<<3]) #Accelerometer Range. 16
		self.I2CWriteBulk(0x68,[0x6B, 0x00]) #poweron

	def MPU6050_accel(self):
		b,tmt = self.I2CReadBulk(0x68, 0x3B ,6)
		if tmt:return None
		if None not in b:
			return [(b[x*2+1]<<8)|b[x*2] for x in range(3)] #X,Y,Z
	def MPU6050_gyro(self):
		b,tmt = self.I2CReadBulk(0x68, 0x3B+6 ,6)
		if tmt:return None
		if None not in b:
			return [(b[x*2+1]<<8)|b[x*2] for x in range(3)] #X,Y,Z
	def MPU6050_all(self):
		'''
		returns a 7 element list. Ax,Ay,Az,T,Gx,Gy,Gz
		returns None if communication timed out with I2C sensor
		'''
		b,tmt = self.I2CReadBulk(0x68, 0x3B ,14)
		if tmt:return None
		if None not in b:
			return [ int16((b[x*2]<<8)|b[x*2+1]) for x in range(7) ] #Ax,Ay,Az, Temp, Gx, Gy,Gz

	def TSL2561_init(self):
		self.I2CWriteBulk(0x39,[0x80 , 0x03 ]) #poweron
		self.I2CWriteBulk(0x39,[0x80 | 0x01, 0x01 | 0x10 ]) 

	def TSL2561_all(self):
		'''
		returns a 2 element list. total,IR
		returns None if communication timed out with I2C sensor
		'''
		b,tmt = self.I2CReadBulk(0x39,0x80 | 0x20 | 0x0C ,4)
		if tmt:return None
		if None not in b:
			return [ (b[x*2+1]<<8)|b[x*2] for x in range(2) ] #total, IR


if __name__ == '__main__':
	a=connect(autoscan=True)
	print ('version' , a.version)
	print ('------------')
	if not a.connected:
		sys.exit(1)
	time.sleep(0.01)
	print(a.I2CScan())
	'''
	a.TSL2561_init()
	s=time.time()
	for x in range(1000):
		print(a.TSL2561_all())
	print(time.time()-s)

	a.MPU6050_init()
	s=time.time()
	for x in range(1000):
		print(a.MPU6050_all()[0])
	print(time.time()-s)
	'''
