'''
Code snippet for reading data from the kuttypy

'''
import serial, struct, time,platform,os,sys,functools
from utilities import REGISTERS_UNO as REGISTERS
from collections import OrderedDict
import numpy as np

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
		return glob.glob('/dev/tty.usb*') + glob.glob('/dev/cu*')
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
	VERSIONNUM = Byte.pack(REGISTERS.VERSIONNUM)

	GET_VERSION = Byte.pack(1)
	READB =   Byte.pack(2)
	WRITEB =   Byte.pack(3)
	I2C_READ  =   Byte.pack(4)
	I2C_WRITE =   Byte.pack(5)
	I2C_SCAN  =   Byte.pack(6)

	BAUD = 38400
	version = 0
	portname = None
	REGS = REGISTERS.REGISTERS # A map of alphanumeric port names to the 8-bit register locations
	REGSTATES = {} #Store the last written state of the registers
	SPECIALS = REGISTERS.SPECIALS
	blockingSocket = None
	def __init__(self,**kwargs):
		self.sensors={
			0x39:{
				'name':'TSL2561',
				'init':self.TSL2561_init,
				'read':self.TSL2561_all,
				'fields':['total','IR'],
				'min':[0,0],
				'max':[2**15,2**15],
				'config':[{
							'name':'gain',
							'options':['1x','16x'],
							'function':self.TSL2561_gain
							},
							{
							'name':'Integration Time',
							'options':['3 mS','101 mS','402 mS'],
							'function':self.TSL2561_timing
							}
					] },
			0x1E:{
				'name':'HMC5883L',
				'init':self.HMC5883L_init,
				'read':self.HMC5883L_all,
				'fields':['Mx','My','Mz'],
				'min':[-5000,-5000,-5000],
				'max':[5000,5000,5000],
				'config':[{
							'name':'gain',
							'options':['1x','16x'],
							'function':self.TSL2561_gain
							},
							{
							'name':'Integration Time',
							'options':['3 mS','101 mS','402 mS'],
							'function':self.TSL2561_timing
							}
					] },
			0x49:{
				'name':'ADS1115',
				'init':self.ADS1115_init,
				'read':self.ADS1115_read,
				'fields':['Voltage'],
				'min':[0],
				'max':[2**16],
				'config':[{
							'name':'channel',
							'options':['UNI_0','UNI_1','UNI_2','UNI_3','DIFF_01','DIFF_23'],
							'function':self.ADS1115_channel
							},
							{
							'name':'Data Rate',
							'options':['8 SPS','16 SPS','32 SPS','64 SPS','128 SPS','250 SPS','475 SPS','860 SPS'],
							'function':self.TSL2561_rate
							}
					] },
			0x68:{
				'name':'MPU6050',
				'init':self.MPU6050_init,
				'read':self.MPU6050_all,
				'fields':['Ax','Ay','Az','Temp','Gx','Gy','Gz'],
				'min':[-1*2**15,-1*2**15,-1*2**15,0,-1*2**15,-1*2**15,-1*2**15],
				'max':[2**15,2**15,2**15,2**16,2**15,2**15,2**15],
				'config':[{
					'name':'Gyroscope Range',
					'options':['250','500','1000','2000'],
					'function':self.MPU6050_gyro_range
					},
					{
					'name':'Accelerometer Range',
					'options':['2x','4x','8x','16x'],
					'function':self.MPU6050_accel_range
					},
					{
					'name':'Kalman',
					'options':['OFF','0.001','0.01','0.1','1','10'],
					'function':self.MPU6050_kalman_set
					}
			]},
			41:{
				'name':'TCS34725: RGB Sensor',
				'init':self.TCS34725_init,
				'RGB':True,
				'read':self.TCS34725_all,
				'fields':['RED','GREEN','BLUE'],
				'min':[0,0,0,0],
				'max':[2**16,2**16,2**16],
				'config':[{
					'name':'Gain',
					'options':['1','4','16','60'],
					'function':self.TCS34725_gain
					}
			]},
			118:{
				'name':'BMP280',
				'init':self.BMP280_init,
				'read':self.BMP280_all,
				'fields':['Pressure','Temp','Alt'],
				'min':[0,0,0],
				'max':[1600,100,10],
				},
			12:{ #0xc
				'name':'AK8963 Mag',
				'init':self.AK8963_init,
				'read':self.AK8963_all,
				'fields':['X','Y','Z'],
				'min':[-32767,-32767,-32767],
				'max':[32767,32767,32767],
				},
			119:{
				'name':'MS5611',
				'init':self.MS5611_init,
				'read':self.MS5611_all,
				'fields':['Pressure','Temp','Alt'],
				'min':[0,0,0],
				'max':[1600,100,10],
				},
			0x41:{  #A0 pin connected to Vs . Otherwise address 0x40 conflicts with PCA board.
				'name':'INA3221',
				'init':self.INA3221_init,
				'read':self.INA3221_all,
				'fields':['CH1','CH2','CH3'],
				'min':[0,0,0],
				'max':[1000,1000,1000],
				},
			0x5A:{
				'name':'MLX90614',
				'init':self.MLX90614_init,
				'read':self.MLX90614_all,
				'fields':['TEMP'],
				'min':[0],
				'max':[350]}
		}
		self.controllers={
			self.MCP5725_ADDRESS:{
				'name':'MCP4725',
				'init':self.MCP4725_init,
				'write':[['CH0',0,4095,0,self.MCP4725_set]],
				},
		}

		self.special={
			0x40:{
				'name':'PCA9685 PWM',
				'init':self.PCA9685_init,
				'write':[['Channel 1',0,180,90,functools.partial(self.PCA9685_set,1)], #name, start, stop, default, function
						['Channel 2',0,180,90,functools.partial(self.PCA9685_set,2)],
						['Channel 3',0,180,90,functools.partial(self.PCA9685_set,3)],
						['Channel 4',0,180,90,functools.partial(self.PCA9685_set,4)],
						],
				}
		}


		self.connected=False
		if 'port' in kwargs:
			self.portname=kwargs.get('port',None)
			try:
				self.fd,self.version,self.connected=self.connectToPort(self.portname)
				if self.connected:
					self.REGSTATES = {} #Store the last written state of the registers
					for a in ['B','C','D']: #Initialize all inputs
						self.setReg('DDR'+a,0) #All inputs
						self.setReg('PORT'+a,0) #No Pullup
					self.setReg('PORTC',(1<<4)|(1<<5)) #I2C Pull-Up

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
							self.REGSTATES = {} #Store the last written state of the registers
							for a in ['B','C','D']: #Initialize all inputs
								self.setReg('DDR'+a,0) #All inputs
								self.setReg('PORT'+a,0) #No Pullup
							self.setReg('PORTC',(1<<4)|(1<<5)) #I2C Pull-Up
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
			if 'inux' in platform.system(): #Linux based system
				try:
					#try to lock down the serial port
					import socket
					self.blockingSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
					self.blockingSocket.bind('\0eyesj2%s'%portname) 
					self.blockingSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
					fd = serial.Serial(portname, self.BAUD, timeout = 0.5)
					if not fd.isOpen():
						return None,'',False
				except socket.error as e:
					#print ('Port {0} is busy'.format(portname))
					return None,'',False
					#raise RuntimeError("Another program is using %s (%d)" % (portname) )

				'''
				import fcntl
				try:
					fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
					#print ('locked access to ',portname,fd.fileno())
				except IOError:
					#print ('Port {0} is busy'.format(portname))
					return None,'',False
				'''
			else:
				fd = serial.Serial(portname, self.BAUD, timeout = 0.5)
				#print ('not on linux',platform.system())

			if(fd.in_waiting):
				fd.flush()
				fd.readall()

		except serial.SerialException as ex:
			print ('Port {0} is unavailable: {1}'.format(portname, ex) )
			return None,'',False

		version = self.__get_version__(fd)
		if len(version)==1:
			if ord(version)==ord(self.VERSIONNUM):
				return fd,ord(version),True
		print ('version check failed',len(version),ord(version))
		return None,'',False
		
	def close(self):
		self.fd.close()
		self.portname = None
		self.connected = False
		if self.blockingSocket:
			self.blockingSocket.shutdown(1)
			self.blockingSocket.close()
			self.blockingSocket = None

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
		if reg not in self.REGS and type(reg)==str: return False
		self.REGSTATES[reg] = data
		self.__sendByte__(self.WRITEB)
		if reg in self.REGS:
			self.__sendByte__(self.REGS[reg])
		else:
			#print('missing register',reg)
			self.__sendByte__(reg)
		self.__sendByte__(data)

	def getReg(self,reg):
		if (reg not in self.REGS) and type(reg)==str:
			print('unknown register',reg)
			return 0
		self.__sendByte__(self.READB)
		if reg in self.REGS:
			self.__sendByte__(self.REGS[reg])
		else:
			#print('missing register',reg)
			self.__sendByte__(reg)
		val = self.__getByte__()
		self.REGSTATES[reg] = val
		return val

	def readADC(self,ch):        # Read the ADC channel
		self.setReg(self.REGS['ADMUX'], 64 | ch)
		self.setReg(self.REGS['ADCSRA'], 197)		# Enable the ADC
		low = self.getReg(self.REGS['ADCL'])
		hi = self.getReg(self.REGS['ADCH'])
		return (hi << 8) | low

	'''
	def writeEEPROM(self,data):
		addr=0
		for a in data:
			timeout=20 #20mS
			while ((self.getReg('EECR') & 2)):
				timeout-=1
				if timeout==0:
					print ('wait timeout!')
					break
				time.sleep(0.001)

			self.setReg('EEARL',addr)
			self.setReg('EEARH',0)
			self.setReg('EEDR',a)
			self.setReg('EECR',4) ##EEMPE master write enable
			self.setReg('EECR',6) # EEPE write
			addr+=1

	def readEEPROM(self,total):
		addr=0; b = []
		for a in range(total):
			timeout=20 #20mS
			while ((self.getReg('EECR') & 2)):
				timeout-=1
				if timeout==0:
					print ('wait timeout!')
					break
				time.sleep(0.001)

			self.setReg('EEARL',addr)
			self.setReg('EEARH',0)
			self.setReg('EECR',1) ##EERE. Read 
			b.append(self.getReg('EEDR'))
			addr+=1
		return b
	'''

	# I2C Calls. Will be replaced with firmware level implementation
	'''
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
		while val<254:
			addrs.append(val)
			val = self.__getByte__()
		if(val==254):print('timed out')
		#self.setReg('TWBR',0xFF) #I2C speed minimal. testing purposes

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

	class KalmanFilter(object):
		'''
		Credits:http://scottlobdell.me/2014/08/kalman-filtering-python-reading-sensor-input/
		'''
		def __init__(self, var, est,initial_values): #var = process variance. est = estimated measurement var
			self.var = np.array(var)
			self.est = np.array(est)
			self.posteri_estimate = np.array(initial_values)
			self.posteri_error_estimate = np.ones(len(var),dtype=np.float16)

		def input(self, vals):
			vals = np.array(vals)
			priori_estimate = self.posteri_estimate
			priori_error_estimate = self.posteri_error_estimate + self.var

			blending_factor = priori_error_estimate / (priori_error_estimate + self.est)
			self.posteri_estimate = priori_estimate + blending_factor * (vals - priori_estimate)
			self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

		def output(self):
			return self.posteri_estimate


	MPU6050_kalman = 0

	def MPU6050_init(self):
		self.I2CWriteBulk(0x68,[0x1B,0<<3]) #Gyro Range . 250
		self.I2CWriteBulk(0x68,[0x1C,0<<3]) #Accelerometer Range. 2
		self.I2CWriteBulk(0x68,[0x6B, 0x00]) #poweron
		v,tmt = self.I2CReadBulk(0x68,0x75,1)
		self.mag = False
		if v[0] in [0x71,0x73]: #MPU9255, MPU9250. Has magnetometer. Enable it.
			self.mag = True
			self.I2CWriteBulk(0x68,[0x37,0x22]) #INT_PIN_CFG . I2C passthrough enabled. Rescan to detect magnetometer.
			
	def MPU6050_gyro_range(self,val):
		self.I2CWriteBulk(0x68,[0x1B,val<<3]) #Gyro Range . 250,500,1000,2000 -> 0,1,2,3 -> shift left by 3 positions

	def MPU6050_accel_range(self,val):
		print(val)
		self.I2CWriteBulk(0x68,[0x1C,val<<3]) #Accelerometer Range. 2,4,8,16 -> 0,1,2,3 -> shift left by 3 positions

	def MPU6050_kalman_set(self,val):
		if not val:
			self.MPU6050_kalman = 0
			return
		noise=[]
		for a in range(50):
			noise.append(np.array(self.MPU6050_all(disableKalman=True)))
		noise = np.array(noise)
		self.MPU6050_kalman = self.KalmanFilter(1e6*np.ones(noise.shape[1])/(10**val), np.std(noise,0)**2, noise[-1])


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

	def MPU6050_all(self,disableKalman=False):
		'''
		returns a 7 element list. Ax,Ay,Az,T,Gx,Gy,Gz
		returns None if communication timed out with I2C sensor
		disableKalman can be set to True if Kalman was previously enabled.
		'''
		b,tmt = self.I2CReadBulk(0x68, 0x3B ,14)
		if tmt:return None
		if None not in b:
			if (not self.MPU6050_kalman) or disableKalman:
				return [ np.int16((b[x*2]<<8)|b[x*2+1]) for x in range(7) ] #Ax,Ay,Az, Temp, Gx, Gy,Gz
			else:
				self.MPU6050_kalman.input([ np.int16((b[x*2]<<8)|b[x*2+1]) for x in range(7) ])
				return self.MPU6050_kalman.output()

	######## AK8963 magnetometer attacched to MPU925x #######
	AK8963_ADDRESS =0x0C
	_AK8963_CNTL = 0x0A
	def AK8963_init(self):
			self.I2CWriteBulk(self.AK8963_ADDRESS,[self._AK8963_CNTL,0]) #power down mag
			self.I2CWriteBulk(self.AK8963_ADDRESS,[self._AK8963_CNTL,(1<<4)|6]) #mode   (0=14bits,1=16bits) <<4 | (2=8Hz , 6=100Hz)
	def AK8963_all(self,disableKalman=False):
		vals,tmt=self.I2CReadBulk(self.AK8963_ADDRESS,0x03,7) #6+1 . 1(ST2) should not have bit 4 (0x8) true. It's ideally 16 . overflow bit
		if tmt:return None
		ax,ay,az = struct.unpack('hhh',bytes(vals[:6]))
		if not vals[6]&0x08:return [ax,ay,az]
		else: return None


	####### BMP280 ###################
	## Ported from https://github.com/farmerkeith/BMP280-library/blob/master/farmerkeith_BMP280.cpp
	BMP280_ADDRESS = 118
	BMP280_REG_CONTROL = 0xF4
	BMP280_REG_RESULT = 0xF6
	BMP280_oversampling = 0
	_BMP280_PRESSURE_MIN_HPA = 0
	_BMP280_PRESSURE_MAX_HPA = 1600
	_BMP280_sea_level_pressure = 1013.25 #for calibration.. from circuitpython library
	def BMP280_init(self):
		b,tmt = self.I2CReadBulk(self.BMP280_ADDRESS, 0xD0 ,1)
		if tmt:return
		b = b[0]
		if b in [0x58,0x56,0x57]:
			print('BMP280. ID:',b)
		elif b==0x60:
			print('BME280 . includes humidity')
		else:
			print('ID unknown',b)
		# get calibration data
		b,tmt = self.I2CReadBulk(self.BMP280_ADDRESS, 0x88 ,24) #24 bytes containing calibration data
		coeff = list(struct.unpack('<HhhHhhhhhhhh', bytes(b)))
		coeff = [float(i) for i in coeff]
		self._BMP280_temp_calib = coeff[:3]
		self._BMP280_pressure_calib = coeff[3:]
		self._BMP280_t_fine = 0.

		#details of register 0xF4
		#mode[1:0] F4bits[1:0] 00=sleep, 01,10=forced, 11=normal
		#osrs_p[2:0] F4bits[4:2] 000=skipped, 001=16bit, 010=17bit, 011=18bit, 100=19bit, 101,110,111=20 bit
		#osrs_t[2:0] F4bits[7:5] 000=skipped, 001=16bit, 010=17bit, 011=18bit, 100=19bit, 101,110,111=20 bit
		#VALUE = (osrs_t & 0x7) << 5 | (osrs_p & 0x7) << 2 | (mode & 0x3); #
		self.I2CWriteBulk(self.BMP280_ADDRESS, [0xF4,0xFF]) #


	def _BMP280_calcTemperature(self,adc_t):
		v1 = (adc_t / 16384.0 - self._BMP280_temp_calib[0] / 1024.0) * self._BMP280_temp_calib[1]
		v2 = ((adc_t / 131072.0 - self._BMP280_temp_calib[0] / 8192.0) * ( adc_t / 131072.0 - self._BMP280_temp_calib[0] / 8192.0)) * self._BMP280_temp_calib[2]
		self._BMP280_t_fine = int(v1+v2)
		return (v1+v2) / 5120.0  #actual temperature. 

	def _BMP280_calcPressure(self,adc_p,adc_t):
		self._BMP280_calcTemperature(adc_t) #t_fine has been set now.
		# Algorithm from the BMP280 driver. adapted from adafruit adaptation
		# https://github.com/BoschSensortec/BMP280_driver/blob/master/bmp280.c
		var1 = self._BMP280_t_fine / 2.0 - 64000.0
		var2 = var1 * var1 * self._BMP280_pressure_calib[5] / 32768.0
		var2 = var2 + var1 * self._BMP280_pressure_calib[4] * 2.0
		var2 = var2 / 4.0 + self._BMP280_pressure_calib[3] * 65536.0
		var3 = self._BMP280_pressure_calib[2] * var1 * var1 / 524288.0
		var1 = (var3 + self._BMP280_pressure_calib[1] * var1) / 524288.0
		var1 = (1.0 + var1 / 32768.0) * self._BMP280_pressure_calib[0]
		if not var1:
			return _BMP280_PRESSURE_MIN_HPA
		pressure = 1048576.0 - adc_p
		pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
		var1 = self._BMP280_pressure_calib[8] * pressure * pressure / 2147483648.0
		var2 = pressure * self._BMP280_pressure_calib[7] / 32768.0
		pressure = pressure + (var1 + var2 + self._BMP280_pressure_calib[6]) / 16.0
		pressure /= 100
		if pressure < self._BMP280_PRESSURE_MIN_HPA:
			return self._BMP280_PRESSURE_MIN_HPA
		if pressure > self._BMP280_PRESSURE_MAX_HPA:
			return self._BMP280_PRESSURE_MAX_HPA
		return pressure

	def BMP280_all(self):
		#os = [0x34,0x74,0xb4,0xf4]
		#delays=[0.005,0.008,0.014,0.026]
		#self.I2CWriteBulk(self.BMP280_ADDRESS,[self.BMP280_REG_CONTROL,os[self.BMP280_oversampling] ])
		#time.sleep(delays[self.BMP280_oversampling])
		data,tmt = self.I2CReadBulk(self.BMP280_ADDRESS, 0xF7,6)
		if tmt:return None
		if None not in data:
			# Convert pressure and temperature data to 19-bits
			adc_p = (((data[0] & 0xFF) * 65536.) + ((data[1] & 0xFF) * 256.) + (data[2] & 0xF0)) / 16.
			adc_t = (((data[3] & 0xFF) * 65536.) + ((data[4] & 0xFF) * 256.) + (data[5] & 0xF0)) / 16.
		return [self._BMP280_calcPressure(adc_p,adc_t), self._BMP280_calcTemperature(adc_t), 0]


	########## TCS34725 RGB sensor ###########

	_TCS34725_COMMAND_BIT       = 0x80
	_TCS34725_REGISTER_STATUS   = 0x13
	_TCS34725_REGISTER_CDATA    = 0x14
	_TCS34725_REGISTER_RDATA    = 0x16
	_TCS34725_REGISTER_GDATA    = 0x18
	_TCS34725_REGISTER_BDATA    = 0x1a

	_TCS34725_REGISTER_ENABLE   = 0x00
	_TCS34725_REGISTER_ATIME    = 0x01
	_TCS34725_REGISTER_AILT     = 0x04
	_TCS34725_REGISTER_AIHT     = 0x06
	_TCS34725_REGISTER_ID       = 0x12
	_TCS34725_REGISTER_APERS    = 0x0c
	_TCS34725_REGISTER_CONTROL  = 0x0f
	_TCS34725_REGISTER_SENSORID = 0x12
	_TCS34725_REGISTER_STATUS   = 0x13
	_TCS34725_ENABLE_AIEN       = 0x10
	_TCS34725_ENABLE_WEN        = 0x08
	_TCS34725_ENABLE_AEN        = 0x02
	_TCS34725_ENABLE_PON        = 0x01

	_GAINS  = (1, 4, 16, 60)
	_CYCLES = (0, 1, 2, 3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60)
	_INTEGRATION_TIME_THRESHOLD_LOW = 2.4
	_INTEGRATION_TIME_THRESHOLD_HIGH = 614.4

	TCS34725_ADDRESS = 41
	def TCS34725_init(self):
		enable,tmt = self.I2CReadBulk(self.TCS34725_ADDRESS, self._TCS34725_COMMAND_BIT|self._TCS34725_REGISTER_ENABLE,1)
		enable = enable[0]
		self.I2CWriteBulk(self.TCS34725_ADDRESS, [self._TCS34725_REGISTER_ENABLE,enable|self._TCS34725_ENABLE_PON]) #
		time.sleep(0.003)
		self.I2CWriteBulk(self.TCS34725_ADDRESS, [self._TCS34725_COMMAND_BIT|self._TCS34725_REGISTER_ENABLE,enable|self._TCS34725_ENABLE_PON | self._TCS34725_ENABLE_AEN| self._TCS34725_ENABLE_AIEN]) #
		self.I2CWriteBulk(self.TCS34725_ADDRESS, [self._TCS34725_COMMAND_BIT|self._TCS34725_REGISTER_APERS,10]) 
		self.I2CWriteBulk(self.TCS34725_ADDRESS, [self._TCS34725_COMMAND_BIT|self._TCS34725_REGISTER_ATIME,256-40]) 


	def TCS34725_gain(self,g):
		self.I2CWriteBulk(self.TCS34725_ADDRESS, [self._TCS34725_COMMAND_BIT|self._TCS34725_REGISTER_CONTROL,g]) #Gain
		

	def TCS34725_all(self):
		R,tmt = self.I2CReadBulk(self.TCS34725_ADDRESS, self._TCS34725_COMMAND_BIT|self._TCS34725_REGISTER_RDATA,2)
		G,tmt = self.I2CReadBulk(self.TCS34725_ADDRESS, self._TCS34725_COMMAND_BIT|self._TCS34725_REGISTER_GDATA,2)
		B,tmt = self.I2CReadBulk(self.TCS34725_ADDRESS, self._TCS34725_COMMAND_BIT|self._TCS34725_REGISTER_BDATA,2)

		if tmt:return None
		return [R[0]|(R[1]<<8),G[0]|(G[1]<<8),B[0]|(B[1]<<8)]
	def TCS34725_range(self):
		pass

	####### MS5611 Altimeter ###################
	MS5611_ADDRESS = 119

	def MS5611_init(self):
		self.I2CWriteBulk(self.MS5611_ADDRESS, [0x1E]) # reset
		time.sleep(0.5)
		self._MS5611_calib = np.zeros(6)

		#calibration data.
		#pressure gain, offset . T coeff of P gain, offset. Ref temp. T coeff of T. all unsigned shorts.
		b,tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA2 ,2) 
		if tmt:return
		self._MS5611_calib[0] = struct.unpack('!H', bytes(b))[0]
		b,tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA4 ,2) 
		self._MS5611_calib[1] = struct.unpack('!H', bytes(b))[0]
		b,tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA6 ,2) 
		self._MS5611_calib[2] = struct.unpack('!H', bytes(b))[0]
		b,tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA8 ,2) 
		self._MS5611_calib[3] = struct.unpack('!H', bytes(b))[0]
		b,tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0xAA ,2) 
		self._MS5611_calib[4] = struct.unpack('!H', bytes(b))[0]
		b,tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0xAC ,2) 
		self._MS5611_calib[5] = struct.unpack('!H', bytes(b))[0]
		print('Calibration for MS5611:',self._MS5611_calib)
		

	def MS5611_all(self):
		self.I2CWriteBulk(self.MS5611_ADDRESS, [0x48]) #  0x48 Pressure conversion(OSR = 4096) command
		time.sleep(0.01) #10mS
		b,tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0x00 ,3) #data.
		D1 = b[0]*65536 + b[1]*256 + b[2] #msb2, msb1, lsb

		self.I2CWriteBulk(self.MS5611_ADDRESS, [0x58]) #  0x58 Temperature conversion(OSR = 4096) command
		time.sleep(0.01)
		b,tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0x00 ,3) #data.
		D2 = b[0]*65536 + b[1]*256 + b[2] #msb2, msb1, lsb
		

		dT = D2 - self._MS5611_calib[4] * 256
		TEMP = 2000 + dT * self._MS5611_calib[5] / 8388608
		OFF = self._MS5611_calib[1] * 65536 + (self._MS5611_calib[3] * dT) / 128
		SENS = self._MS5611_calib[0] * 32768 + (self._MS5611_calib[2] * dT ) / 256
		T2 = 0;	OFF2 = 0;	SENS2 = 0
		if TEMP >= 2000 :
			T2 = 0
			OFF2 = 0
			SENS2 = 0
		elif TEMP < 2000 :
			T2 = (dT * dT) / 2147483648
			OFF2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 2
			SENS2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 4
			if TEMP < -1500 :
				OFF2 = OFF2 + 7 * ((TEMP + 1500) * (TEMP + 1500))
				SENS2 = SENS2 + 11 * ((TEMP + 1500) * (TEMP + 1500)) / 2

		TEMP = TEMP - T2
		OFF = OFF - OFF2
		SENS = SENS - SENS2
		pressure = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 100.0
		cTemp = TEMP / 100.0
		return [pressure,cTemp,0]


	### INA3221 3 channel , high side current sensor #############
	INA3221_ADDRESS  = 0x41
	_INA3221_REG_CONFIG = 0x0
	_INA3221_SHUNT_RESISTOR_VALUE = 0.1
	_INA3221_REG_SHUNTVOLTAGE = 0x01
	_INA3221_REG_BUSVOLTAGE = 0x02

	def INA3221_init(self):
		self.I2CWriteBulk(self.INA3221_ADDRESS,[self._INA3221_REG_CONFIG, 0b01110101, 0b00100111 ])  #cont shunt.

	def INA3221_all(self):
		I = [0.,0.,0.]
		b,tmt = self.I2CReadBulk(self.INA3221_ADDRESS,self._INA3221_REG_SHUNTVOLTAGE  , 2) 
		if tmt:return None
		b[1]&=0xF8; I[0] = struct.unpack('!h',bytes(b))[0]
		b,tmt = self.I2CReadBulk(self.INA3221_ADDRESS,self._INA3221_REG_SHUNTVOLTAGE  +2 , 2) 
		if tmt:return None
		b[1]&=0xF8; I[1] = struct.unpack('!h',bytes(b))[0]
		b,tmt = self.I2CReadBulk(self.INA3221_ADDRESS,self._INA3221_REG_SHUNTVOLTAGE  +4 , 2) 
		if tmt:return None
		b[1]&=0xF8; I[2] = struct.unpack('!h',bytes(b))[0]
		return [0.005*I[0]/self._INA3221_SHUNT_RESISTOR_VALUE,0.005*I[1]/self._INA3221_SHUNT_RESISTOR_VALUE,0.005*I[2]/self._INA3221_SHUNT_RESISTOR_VALUE]
	


	### SHT21 HUMIDITY TEMPERATURE SENSOR #############
	SHT21_ADDRESS  = 0x41
	_SHT21_TEMP = 0xf3
	_SHT21_HUM = 0xf5
	_SHT21_RESET = 0xFE
	_INA3221_REG_SHUNTVOLTAGE = 0x01
	_INA3221_REG_BUSVOLTAGE = 0x02

	def SHT21_init(self):
		self.I2CWriteBulk(self.SHT21_ADDRESS,[self._SHT21_RESET ])  #reset
		time.sleep(0.1)

	def SHT21_all(self):
		self.I2CWriteBulk(self.SHT21_ADDRESS,[self._SHT21_TEMP ])
		time.sleep(.1)
		self.startI2C()
		self.writeI2C((self.SHT21_ADDRESS<<1)|1) #Read
		b=[]
		for a in range(2):b.append(self.readI2C(1) )
		b.append(self.readI2C(0))
		self.stopI2C()
		temperature,checksum = struct.unpack('>HB',bytes(b))
		return [temperature* 175.72 / 65536.0 - 46.85,0]


	####### TSL2561 LIGHT SENSOR ###########
	TSL_GAIN = 0x00 # 0x00=1x , 0x01 = 16x
	TSL_TIMING = 0x00 # 0x00=3 mS , 0x01 = 101 mS, 0x02 = 402mS
	def TSL2561_init(self):
		self.I2CWriteBulk(0x39,[0x80 , 0x03 ]) #poweron
		self.I2CWriteBulk(0x39,[0x80 | 0x01, self.TSL_GAIN|self.TSL_TIMING ]) 
		return self.TSL2561_all()

	def TSL2561_gain(self,gain):
		self.TSL_GAIN = gain<<4
		self.TSL2561_config(self.TSL_GAIN,self.TSL_TIMING)
		
	def TSL2561_timing(self,timing):
		self.TSL_TIMING = timing
		self.TSL2561_config(self.TSL_GAIN,self.TSL_TIMING)

	def TSL2561_rate(self,timing):
		self.TSL_TIMING = timing
		self.TSL2561_config(self.TSL_GAIN,self.TSL_TIMING)

	def TSL2561_config(self,gain,timing):
		self.I2CWriteBulk(0x39,[0x80 | 0x01, gain|timing]) #Timing register 0x01. gain[1x,16x] | timing[13mS,100mS,400mS]

	def TSL2561_all(self):
		'''
		returns a 2 element list. total,IR
		returns None if communication timed out with I2C sensor
		'''
		b,tmt = self.I2CReadBulk(0x39,0x80 | 0x20 | 0x0C ,4)
		if tmt:return None
		if None not in b:
			return [ (b[x*2+1]<<8)|b[x*2] for x in range(2) ] #total, IR

	def MLX90614_init(self):
		pass

	def MLX90614_all(self):
		'''
		return a single element list.  None if failed
		'''
		vals,tmt = self.I2CReadBulk(0x5A, 0x07 ,3)
		if tmt:return None
		if vals:
			if len(vals)==3:
				return [((((vals[1]&0x007f)<<8)+vals[0])*0.02)-0.01 - 273.15]
			else:
				return None
		else:
			return None

	MCP5725_ADDRESS = 0x60
	def MCP4725_init(self):
		pass

	def MCP4725_set(self,val):
		'''
		Set the DAC value. 0 - 4095
		'''
		self.I2CWriteBulk(self.MCP5725_ADDRESS, [0x40,(val>>4)&0xFF,(val&0xF)<<4])

	####################### HMC5883L MAGNETOMETER ###############

	HMC5883L_ADDRESS = 0x1E
	HMC_CONFA=0x00
	HMC_CONFB=0x01
	HMC_MODE=0x02
	HMC_STATUS=0x09

	#--------CONFA register bits. 0x00-----------
	HMCSamplesToAverage=0
	HMCSamplesToAverage_choices=[1,2,4,8]
	
	HMCDataOutputRate=6
	HMCDataOutputRate_choices=[0.75,1.5,3,7.5,15,30,75]
	
	HMCMeasurementConf=0
	
	#--------CONFB register bits. 0x01-----------
	HMCGainValue = 7 #least sensitive
	HMCGain_choices = [8,7,6,5,4,3,2,1]
	HMCGainScaling=[1370.,1090.,820.,660.,440.,390.,330.,230.]

	def HMC5883L_init(self):
		self.__writeHMCCONFA__()
		self.__writeHMCCONFB__()
		self.I2CWriteBulk(self.HMC5883L_ADDRESS,[self.HMC_MODE,0]) #enable continuous measurement mode

	def __writeHMCCONFB__(self):
		self.I2CWriteBulk(self.HMC5883L_ADDRESS,[self.HMC_CONFB,self.HMCGainValue<<5]) #set gain

	def __writeHMCCONFA__(self):
		self.I2CWriteBulk(self.HMC5883L_ADDRESS,[self.HMC_CONFA,(self.HMCDataOutputRate<<2)|(self.HMCSamplesToAverage<<5)|(self.HMCMeasurementConf)])

	def HMC5883L_getVals(self,addr,bytes):
		vals = self.I2C.readBulk(self.ADDRESS,addr,bytes) 
		return vals
	
	def HMC5883L_all(self):
		vals=self.HMC5883L_getVals(0x03,6)
		if vals:
			if len(vals)==6:
				return [np.int16(vals[a*2]<<8|vals[a*2+1])/self.HMCGainScaling[self.HMCGainValue] for a in range(3)]
			else:
				return False
		else:
			return False

	PCA9685_address = 64
	def PCA9685_init(self):
		prescale_val = int((25000000.0 / 4096 / 60.)  - 1) # default clock at 25MHz
		#self.I2CWriteBulk(self.PCA9685_address, [0x00,0x10]) #MODE 1 , Sleep
		print('clock set to,',prescale_val)
		self.I2CWriteBulk(self.PCA9685_address, [0xFE,prescale_val]) #PRESCALE , prescale value
		self.I2CWriteBulk(self.PCA9685_address, [0x00,0x80]) #MODE 1 , restart
		self.I2CWriteBulk(self.PCA9685_address, [0x01,0x04]) #MODE 2 , Totem Pole
		
		pass

	CH0 = 0x6	 		    #LED0 start register
	CH0_ON_L =  0x6		#channel0 output and brightness control byte 0
	CH0_ON_H =  0x7		#channel0 output and brightness control byte 1
	CH0_OFF_L = 0x8		#channel0 output and brightness control byte 2
	CH0_OFF_H = 0x9		#channel0 output and brightness control byte 3
	CHAN_WIDTH = 4
	def PCA9685_set(self,chan,angle):
		'''
		chan: 1-16
		Set the servo angle for SG90: angle(0 - 180)
		'''
		Min = 180
		Max = 650
		val = int((( Max-Min ) * ( angle/180. ))+Min)
		print(chan,angle,val)
		self.I2CWriteBulk(self.PCA9685_address, [self.CH0_ON_L + self.CHAN_WIDTH * (chan - 1),0]) #
		self.I2CWriteBulk(self.PCA9685_address, [self.CH0_ON_H + self.CHAN_WIDTH * (chan - 1),0]) # Turn on immediately. At 0.
		self.I2CWriteBulk(self.PCA9685_address, [self.CH0_OFF_L + self.CHAN_WIDTH * (chan - 1),val&0xFF]) #Turn off after val width 0-4095
		self.I2CWriteBulk(self.PCA9685_address, [self.CH0_OFF_H + self.CHAN_WIDTH * (chan - 1),(val>>8)&0xFF])

	## ADS1115
	REG_POINTER_MASK    = 0x3
	REG_POINTER_CONVERT = 0
	REG_POINTER_CONFIG  = 1
	REG_POINTER_LOWTHRESH=2
	REG_POINTER_HITHRESH =3

	REG_CONFIG_OS_MASK      =0x8000
	REG_CONFIG_OS_SINGLE    =0x8000
	REG_CONFIG_OS_BUSY      =0x0000
	REG_CONFIG_OS_NOTBUSY   =0x8000

	REG_CONFIG_MUX_MASK     =0x7000
	REG_CONFIG_MUX_DIFF_0_1 =0x0000  # Differential P = AIN0, N = AIN1 =default)
	REG_CONFIG_MUX_DIFF_0_3 =0x1000  # Differential P = AIN0, N = AIN3
	REG_CONFIG_MUX_DIFF_1_3 =0x2000  # Differential P = AIN1, N = AIN3
	REG_CONFIG_MUX_DIFF_2_3 =0x3000  # Differential P = AIN2, N = AIN3
	REG_CONFIG_MUX_SINGLE_0 =0x4000  # Single-ended AIN0
	REG_CONFIG_MUX_SINGLE_1 =0x5000  # Single-ended AIN1
	REG_CONFIG_MUX_SINGLE_2 =0x6000  # Single-ended AIN2
	REG_CONFIG_MUX_SINGLE_3 =0x7000  # Single-ended AIN3

	REG_CONFIG_PGA_MASK     =0x0E00  #bits 11:9
	REG_CONFIG_PGA_6_144V   =(0<<9)  # +/-6.144V range = Gain 2/3
	REG_CONFIG_PGA_4_096V   =(1<<9)  # +/-4.096V range = Gain 1
	REG_CONFIG_PGA_2_048V   =(2<<9)  # +/-2.048V range = Gain 2 =default)
	REG_CONFIG_PGA_1_024V   =(3<<9)  # +/-1.024V range = Gain 4
	REG_CONFIG_PGA_0_512V   =(4<<9)  # +/-0.512V range = Gain 8
	REG_CONFIG_PGA_0_256V   =(5<<9)  # +/-0.256V range = Gain 16

	REG_CONFIG_MODE_MASK    =0x0100   #bit 8
	REG_CONFIG_MODE_CONTIN  =(0<<8)   # Continuous conversion mode
	REG_CONFIG_MODE_SINGLE  =(1<<8)   # Power-down single-shot mode =default)

	REG_CONFIG_DR_MASK      =0x00E0  
	REG_CONFIG_DR_8SPS    =(0<<5)   #8 SPS
	REG_CONFIG_DR_16SPS    =(1<<5)   #16 SPS
	REG_CONFIG_DR_32SPS    =(2<<5)   #32 SPS
	REG_CONFIG_DR_64SPS    =(3<<5)   #64 SPS
	REG_CONFIG_DR_128SPS   =(4<<5)   #128 SPS
	REG_CONFIG_DR_250SPS   =(5<<5)   #260 SPS
	REG_CONFIG_DR_475SPS   =(6<<5)   #475 SPS
	REG_CONFIG_DR_860SPS   =(7<<5)   #860 SPS

	REG_CONFIG_CMODE_MASK   =0x0010
	REG_CONFIG_CMODE_TRAD   =0x0000
	REG_CONFIG_CMODE_WINDOW =0x0010

	REG_CONFIG_CPOL_MASK    =0x0008
	REG_CONFIG_CPOL_ACTVLOW =0x0000
	REG_CONFIG_CPOL_ACTVHI  =0x0008

	REG_CONFIG_CLAT_MASK    =0x0004
	REG_CONFIG_CLAT_NONLAT  =0x0000
	REG_CONFIG_CLAT_LATCH   =0x0004

	REG_CONFIG_CQUE_MASK    =0x0003
	REG_CONFIG_CQUE_1CONV   =0x0000
	REG_CONFIG_CQUE_2CONV   =0x0001
	REG_CONFIG_CQUE_4CONV   =0x0002
	REG_CONFIG_CQUE_NONE    =0x0003
	gains = OrderedDict([('GAIN_TWOTHIRDS',REG_CONFIG_PGA_6_144V),('GAIN_ONE',REG_CONFIG_PGA_4_096V),('GAIN_TWO',REG_CONFIG_PGA_2_048V),('GAIN_FOUR',REG_CONFIG_PGA_1_024V),('GAIN_EIGHT',REG_CONFIG_PGA_0_512V),('GAIN_SIXTEEN',REG_CONFIG_PGA_0_256V)])
	gain_scaling =  OrderedDict([('GAIN_TWOTHIRDS',0.1875),('GAIN_ONE',0.125),('GAIN_TWO',0.0625),('GAIN_FOUR',0.03125),('GAIN_EIGHT',0.015625),('GAIN_SIXTEEN',0.0078125)])
	type_selection = OrderedDict([('UNI_0',0),('UNI_1',1),('UNI_2',2),('UNI_3',3),('DIFF_01','01'),('DIFF_23','23')])
	sdr_selection = OrderedDict([(8,REG_CONFIG_DR_8SPS),(16,REG_CONFIG_DR_16SPS),(32,REG_CONFIG_DR_32SPS),(64,REG_CONFIG_DR_64SPS),(128,REG_CONFIG_DR_128SPS),(250,REG_CONFIG_DR_250SPS),(475,REG_CONFIG_DR_475SPS),(860,REG_CONFIG_DR_860SPS)]) #sampling data rate
	conversion_time = [8,16,32,64,128,250,460,860]
	ADS1115_DATARATE = 5 #250SPS [ 8, 16, 32, 64, 128, 250, 475, 860 ]
	ADS1115_GAIN = REG_CONFIG_PGA_4_096V  # +/-4.096V range = Gain 1 . [+-6, +-4, +-2, +-1, +-0.5, +- 0.25]
	ADS1115_CHANNEL = REG_CONFIG_MUX_SINGLE_0 # ref: type_selection
	TSL_TIMING = 0x00 # 0x00=3 mS , 0x01 = 101 mS, 0x02 = 402mS
	ADS1115_ADDRESS = 0x48
	
	def ADS1115_init(self):
		self.I2CWriteBulk(0x39,[0x80 , 0x03 ]) #poweron
	def ADS1115_channel(self):
		pass
	def ADS1115_read(self):
		'''
		returns a voltage from ADS1115 channel selected using ADS1115_channel. default UNI_0 (Unipolar from channel 0)
		'''
		if chan<=3:
			config = (self.REG_CONFIG_CQUE_NONE # Disable the comparator (default val)
			|self.REG_CONFIG_CLAT_NONLAT        # Non-latching (default val)
			|self.REG_CONFIG_CPOL_ACTVLOW 	    #Alert/Rdy active low   (default val)
			|self.REG_CONFIG_CMODE_TRAD         # Traditional comparator (default val)
			|(self.ADS1115_DATARATE<<5)               # 1600 samples per second (default)
			|(self.REG_CONFIG_MODE_SINGLE)        # Single-shot mode (default)
			|self.ADS1115_GAIN)

			if self.ADS1115_CHANNEL == 0   : config |= self.REG_CONFIG_MUX_SINGLE_0
			elif self.ADS1115_CHANNEL == 1 : config |= self.REG_CONFIG_MUX_SINGLE_1
			elif self.ADS1115_CHANNEL == 2 : config |= self.REG_CONFIG_MUX_SINGLE_2
			elif self.ADS1115_CHANNEL == 3 : config |= self.REG_CONFIG_MUX_SINGLE_3
			#Set 'start single-conversion' bit
			config |= self.REG_CONFIG_OS_SINGLE
			self.I2CWriteBulk(self.ADS1115_ADDRESS,[self.REG_POINTER_CONFIG,(config>>8)&0xFF,config&0xFF])
			time.sleep(1./self.rate+.002) #convert to mS to S
			return self.readRegister(self.REG_POINTER_CONVERT)*self.gain_scaling[self.gain]



		b,tmt = self.I2CReadBulk(0x68, 0x3B ,14)
		if tmt:return None
		if None not in b:
			return [ np.int16((b[x*2]<<8)|b[x*2+1]) for x in range(7) ] #Ax,Ay,Az, Temp, Gx, Gy,Gz

	
	
if __name__ == '__main__':
	a=connect(autoscan=True)
	print ('version' , a.version)
	print ('------------')
	if not a.connected:
		sys.exit(1)
	time.sleep(0.01)
	a.setReg('DDRC',3)
	a.setReg('PORTC',2)
	time.sleep(1)
	a.setReg('PORTC',3)
	a.setReg('DDRC',0)
	print(a.I2CScan())
	'''
	a.PCA9685_init()
	a.PCA9685_set(1,650)

	for x in range(180):
		a.PCA9685_set(1,x)
		time.sleep(0.01)

	
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
