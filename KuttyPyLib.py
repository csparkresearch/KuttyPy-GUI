'''
Code snippet for reading data from the kuttypy

'''
import serial, struct, time, platform, os, sys, functools
from utilities import REGISTERS
from collections import OrderedDict
import numpy as np

if 'inux' in platform.system():  # Linux based system
    import fcntl

Byte = struct.Struct("B")  # size 1
ShortInt = struct.Struct("H")  # size 2
Integer = struct.Struct("I")  # size 4


def _bv(x):
    return 1 << x


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
                s = serial.Serial('COM%d' % i)
                available.append('COM%d' % i)
                s.close()
            except serial.SerialException:
                pass
        return available
    elif system_name == "Darwin":
        # Mac
        return glob.glob('/dev/tty.usb*') + glob.glob('/dev/cu*')
    else:
        # Assume Linux or something else
        return glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*') + glob.glob('/dev/rfcomm*')


def isPortFree(portname):
    try:
        fd = serial.Serial(portname, KUTTYPY.BAUD, stopbits=1, timeout=1.0)
        if fd.isOpen():
            if 'inux' in platform.system():  # Linux based system
                try:
                    fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    fd.close()
                    return True  # Port is available
                except IOError:
                    fd.close()
                    return False  # Port is not available

            else:
                fd.close()
                return True  # Port is available
        else:
            fd.close()
            return False  # Port is not available

    except serial.SerialException as ex:
        return False  # Port is not available


def getFreePorts(openPort=None):
    '''
	Find out which ports are currently free 
	'''
    portlist = {}
    for a in listPorts():
        if a != openPort:
            portlist[a] = isPortFree(a)
        else:
            portlist[a] = False
    return portlist


class KUTTYPY:
    VERSIONNUM_168P = Byte.pack(98)
    VERSIONNUM = Byte.pack(99)
    VERSIONNUM_328P = Byte.pack(100)
    VERSIONNUM_UNO = Byte.pack(101)
    GET_VERSION = Byte.pack(1)
    READB = Byte.pack(2)
    WRITEB = Byte.pack(3)
    I2C_READ = Byte.pack(4)
    I2C_WRITE = Byte.pack(5)
    I2C_SCAN = Byte.pack(6)

    BAUD = 38400
    version = 0
    portname = None
    REGS = REGISTERS.VERSIONS[99]['REGISTERS']  # A map of alphanumeric port names to the 8-bit register locations
    REGSTATES = {}  # Store the last written state of the registers
    SPECIALS = REGISTERS.VERSIONS[99]['SPECIALS']
    nano = False  # check if atmega328p is found instead of 32
    blockingSocket = None
    PCF_text_options = ['hello', 'one', 'two', 'three']

    def __init__(self, **kwargs):
        self.bootloaderfirmware = True
        self.sensors = {
            0x39: {
                'name': 'TSL2561',
                'init': self.TSL2561_init,
                'read': self.TSL2561_all,
                'fields': ['total', 'IR'],
                'min': [0, 0],
                'max': [2 ** 15, 2 ** 15],
                'config': [{
                    'name': 'gain',
                    'options': ['1x', '16x'],
                    'function': self.TSL2561_gain
                },
                    {
                        'name': 'Integration Time',
                        'options': ['3 mS', '101 mS', '402 mS'],
                        'function': self.TSL2561_timing
                    }
                ]},
            0x1E: {
                'name': 'HMC5883L',
                'init': self.HMC5883L_init,
                'read': self.HMC5883L_all,
                'fields': ['Mx', 'My', 'Mz'],
                'min': [-5000, -5000, -5000],
                'max': [5000, 5000, 5000],
                'config': [{
                    'name': 'gain',
                    'options': ['1x', '16x'],
                    'function': self.TSL2561_gain
                },
                    {
                        'name': 'Integration Time',
                        'options': ['3 mS', '101 mS', '402 mS'],
                        'function': self.TSL2561_timing
                    }
                ]},
            0x48: {
                'name': 'ADS1115',
                'init': self.ADS1115_init,
                'read': self.ADS1115_read,
                'fields': ['Voltage'],
                'min': [-5],
                'max': [5],
                'config': [{
                    'name': 'channel',
                    'options': ['UNI_0', 'UNI_1', 'UNI_2', 'UNI_3', 'DIFF_01', 'DIFF_23'],
                    'function': self.ADS1115_channel
                },
                    {
                        'name': 'Data Rate',
                        'options': ['8', '16', '32', '64', '128', '250', '475', '860'],
                        'function': self.ADS1115_rate
                    },
                    {
                        'name': 'Gain',
                        'options': ['GAIN_TWOTHIRDS', 'GAIN_ONE', 'GAIN_TWO', 'GAIN_FOUR', 'GAIN_EIGHT',
                                    'GAIN_SIXTEEN'],
                        'function': self.ADS1115_gain
                    }
                ]},
            0x68: {
                'name': 'MPU6050',
                'init': self.MPU6050_init,
                'read': self.MPU6050_all,
                'fields': ['Ax', 'Ay', 'Az', 'Temp', 'Gx', 'Gy', 'Gz'],
                'min': [-1 * 2 ** 15, -1 * 2 ** 15, -1 * 2 ** 15, 0, -1 * 2 ** 15, -1 * 2 ** 15, -1 * 2 ** 15],
                'max': [2 ** 15, 2 ** 15, 2 ** 15, 2 ** 16, 2 ** 15, 2 ** 15, 2 ** 15],
                'config': [{
                    'name': 'Gyroscope Range',
                    'options': ['250', '500', '1000', '2000'],
                    'function': self.MPU6050_gyro_range
                },
                    {
                        'name': 'Accelerometer Range',
                        'options': ['2x', '4x', '8x', '16x'],
                        'function': self.MPU6050_accel_range
                    },
                    {
                        'name': 'Kalman',
                        'options': ['OFF', '0.001', '0.01', '0.1', '1', '10'],
                        'function': self.MPU6050_kalman_set
                    }
                ]},
            41: {
                'name': 'TCS34725: RGB Sensor',
                'init': self.TCS34725_init,
                'RGB': True,
                'read': self.TCS34725_all,
                'fields': ['RED', 'GREEN', 'BLUE'],
                'min': [0, 0, 0, 0],
                'max': [2 ** 16, 2 ** 16, 2 ** 16],
                'config': [{
                    'name': 'Gain',
                    'options': ['1', '4', '16', '60'],
                    'function': self.TCS34725_gain
                }
                ]},
            118: {
                'name': 'BMP280',
                'init': self.BMP280_init,
                'read': self.BMP280_all,
                'fields': ['Pressure', 'Temp', 'Alt'],
                'min': [0, 0, 0],
                'max': [1600, 100, 100],
            },
            12: {  # 0xc
                'name': 'AK8963 Mag',
                'init': self.AK8963_init,
                'read': self.AK8963_all,
                'fields': ['X', 'Y', 'Z'],
                'min': [-32767, -32767, -32767],
                'max': [32767, 32767, 32767],
            },
            119: {
                'name': 'MS5611',
                'init': self.MS5611_init,
                'read': self.MS5611_all,
                'fields': ['Pressure', 'Temp', 'Alt'],
                'min': [0, 0, 0],
                'max': [1600, 100, 10],
            },
            119: {
                'name': 'BMP180',
                'init': self.BMP180_init,
                'read': self.BMP180_all,
                'fields': ['Pressure', 'Temp'],
                'min': [0, 0],
                'max': [1600, 100],
            },
            0x41: {  # A0 pin connected to Vs . Otherwise address 0x40 conflicts with PCA board.
                'name': 'INA3221',
                'init': self.INA3221_init,
                'read': self.INA3221_all,
                'fields': ['CH1', 'CH2', 'CH3'],
                'min': [0, 0, 0],
                'max': [1000, 1000, 1000],
            },
            0x5A: {
                'name': 'MLX90614',
                'init': self.MLX90614_init,
                'read': self.MLX90614_all,
                'fields': ['TEMP'],
                'min': [0],
                'max': [350]},
            39: {
                'name': 'PCF_LCD',
                'init': self.PCF_LCD_init,
                'read': self.PCF_LCD_all,
                'fields': ['Dummy'],
                'min': [0],
                'max': [1],
                'config': [{
                        'name': 'text',
                        'options': ['hello', 'one', 'two', 'three'],
                        'function': self.PCF_LCD_text
                    },
                    {
                        'name': 'row',
                        'options': ['1', '2'],
                        'function': self.PCF_LCD_row
                    },
                    {
                        'name': 'backlight',
                        'options': ['OFF', 'ON'],
                        'function': self.PCF_LCD_backlight
                    }
                ]}

        }

        self.namedsensors = {
            'GMCOUNTER': {
                'address': [0xe, 0xf, 0x10, 0x11, 0x12],
                'name': 'GMCOUNTER CSpark Geiger Counter',
                'init': self.CSGM_init,
                'read': self.CSGM_all,
                'fields': ['count', 'voltage'],
                'min': [0, 0],
                'max': [65535, 1000],
                'config': [{
                    'name': 'Set Voltage',
                    'widget': 'spinbox',
                    'min': 0,
                    'max': 900,
                    'readbackfunction': self.CSGM_voltage,
                    'function': self.CSGM_config
                }, {
                    'name': 'Set Time Limit(0 for inf)',
                    'widget': 'spinbox',
                    'min': 0,
                    'max': 9000,
                    'function': self.CSGM_timelimit
                },
                    {
                        'name': 'Save To Flash',
                        'widget': 'button',
                        'function': self.CSGM_save
                    }, {
                        'name': 'Start',
                        'widget': 'button',
                        'function': self.CSGM_start
                    },
                    {
                        'name': 'Stop',
                        'widget': 'button',
                        'function': self.CSGM_stop
                    },
                    {
                        'name': 'Reset',
                        'widget': 'button',
                        'function': self.CSGM_reset
                    }
                ]},
            'BH1750': {
                'address': [35],
                'name': 'BH1750 Luminosity Sensor',
                'init': self.BH1750_init,
                'read': self.BH1750_all,
                'fields': ['luminosity(mLx)'],
                'min': [0, 0],
                'max': [32767],
                'config': [{
                    'name': 'sensitivity',
                    'options': ['500mLx', '1000mLx', '4000mLx'],
                    'function': self.BH1750_gain
                }
                ]},
            'TSL2561': {
                'address': [0x29, 0x39, 0x49],
                'name': 'TSL2561 Luminosity Sensor',
                'init': self.TSL2561_init,
                'read': self.TSL2561_all,
                'fields': ['total', 'IR'],
                'min': [0, 0],
                'max': [2 ** 15, 2 ** 15],
                'config': [{
                    'name': 'gain',
                    'options': ['1x', '16x'],
                    'function': self.TSL2561_gain
                },
                    {
                        'name': 'Integration Time',
                        'options': ['3 mS', '101 mS', '402 mS'],
                        'function': self.TSL2561_timing
                    }
                ]},
            'AHT21B': {
                'address': [56],
                'name': 'AHT21B Humidity and Temperature',
                'init': self.AHT21B_init,
                'read': self.AHT21B_all,
                'fields': ['%%RH', 'T'],
                'min': [0, -20, ],
                'max': [100, 100]
            },
            'HMC5883L': {
                'address': [0x1E, 0x3D, 0x3C],
                'name': 'HMC5883L 3 Axis Magnetometer ',
                'init': self.HMC5883L_init,
                'read': self.HMC5883L_all,
                'fields': ['Mx', 'My', 'Mz'],
                'min': [-8, -8, -8],
                'max': [8, 8, 8]
            },
            'QMC3883': {
                'address': [0x13],
                'name': 'QMC5883L 3 Axis Magnetometer ',
                'init': self.QMC5883L_init,
                'read': self.QMC5883L_all,
                'fields': ['Mx', 'My', 'Mz'],
                'min': [-8, -8, -8],
                'max': [8, 8, 8],
                'config': [{
                    'name': 'range',
                    'options': ['2g', '8g'],
                    'function': self.QMC_RANGE
                }
                ]},
            'ADS1115': {
                'address': [0x48, 0x49, 0x4A, 0x4B],
                'name': 'ADS1115',
                'init': self.ADS1115_init,
                'read': self.ADS1115_read,
                'fields': ['Voltage'],
                'min': [-20],
                'max': [20],
                'config': [{
                    'name': 'channel',
                    'options': ['UNI_0', 'UNI_1', 'UNI_2', 'UNI_3', 'DIFF_01', 'DIFF_23'],
                    'function': self.ADS1115_channel
                },
                    {
                        'name': 'Data Rate',
                        'options': ['8', '16', '32', '64', '128', '250', '475', '860'],
                        'function': self.ADS1115_rate
                    },
                    {
                        'name': 'Gain',
                        'options': ['GAIN_TWOTHIRDS', 'GAIN_ONE', 'GAIN_TWO', 'GAIN_FOUR', 'GAIN_EIGHT',
                                    'GAIN_SIXTEEN'],
                        'function': self.ADS1115_gain
                    }
                ]},
            'MPU6050': {
                'address': [0x68, 0x69],
                'name': 'MPU6050 3 Axis Accelerometer and Gyro (Ax, Ay, Az, Temp, Gx, Gy, Gz) ',
                'init': self.MPU6050_init,
                'read': self.MPU6050_all,
                'fields': ['Ax', 'Ay', 'Az', 'Temp', 'Gx', 'Gy', 'Gz'],
                'min': [-1 * 2 ** 15, -1 * 2 ** 15, -1 * 2 ** 15, 0, -1 * 2 ** 15, -1 * 2 ** 15, -1 * 2 ** 15],
                'max': [2 ** 15, 2 ** 15, 2 ** 15, 2 ** 16, 2 ** 15, 2 ** 15, 2 ** 15],
                'config': [{
                    'name': 'Gyroscope Range',
                    'options': ['250', '500', '1000', '2000'],
                    'function': self.MPU6050_gyro_range
                },
                    {
                        'name': 'Accelerometer Range',
                        'options': ['2x', '4x', '8x', '16x'],
                        'function': self.MPU6050_accel_range
                    },
                    {
                        'name': 'Kalman',
                        'options': ['OFF', '0.001', '0.01', '0.1', '1', '10'],
                        'function': self.MPU6050_kalman_set
                    }
                ]},
            'BMP180': {
                'address': [0x77],
                'name': 'BMP180 Pressure and Temperature sensor',
                'init': self.BMP180_init,
                'read': self.BMP180_all,
                'fields': ['Pressure', 'Temp'],
                'min': [0, 0],
                'max': [1600, 100],
                'config': [{
                    'name': 'Oversampling',
                    'options': ['0', '1', '2', '3'],
                    'function': self.BMP180_setOversampling
                }]
            },
            'BMP280': {
                'address': [0x76],
                'name': 'BMP280 Pressure and Temperature sensor',
                'init': self.BMP280_init,
                'read': self.BMP280_all,
                'fields': ['Pressure', 'Temp', 'rH %%'],
                'min': [0, 0, 0],
                'max': [1600, 100, 100],
            },
            'AK8963': {  # 0xc
                'address': [12],
                'name': 'AK8963 Mag',
                'init': self.AK8963_init,
                'read': self.AK8963_all,
                'fields': ['X', 'Y', 'Z'],
                'min': [-32767, -32767, -32767],
                'max': [32767, 32767, 32767],
            },
            'MS5611': {
                'address': [119],
                'name': 'MS5611 Pressure and Temperature Sensor',
                'init': self.MS5611_init,
                'read': self.MS5611_all,
                'fields': ['Pressure', 'Temp', 'Alt'],
                'min': [0, 0, 0],
                'max': [1600, 100, 10],
            },
            'INA3221': {  # A0 pin connected to Vs . Otherwise address 0x40 conflicts with PCA board.
                'address': [0x40, 0x41],
                'name': 'INA3221 Current Sensor',
                'init': self.INA3221_init,
                'read': self.INA3221_all,
                'fields': ['CH1', 'CH2', 'CH3'],
                'min': [0, 0, 0],
                'max': [1000, 1000, 1000],

            },
            'TSL2591': {
                'address': [0x29],
                'name': 'TSL2591 Luminosity Sensor',
                'init': self.TSL2591_init,
                'read': self.TSL2591_all,
                'fields': ['Raw', 'full', 'IR'],
                'min': [0, 0, 0],
                'max': [37889, 88000, 88000],
                'config': [{
                    'name': 'gain',
                    'options': ['1x', '25x', '428x', '9876x'],
                    'function': self.TSL2591_gain
                },
                    {
                        'name': 'Integration Time',
                        'options': ['100 mS', '200 mS', '300 mS', '400 mS', '500 mS', '600 mS'],
                        'function': self.TSL2591_timing
                    }
                ]},
            'VL53L0X': {  # VL53L0X.
                'address': [0x29],
                'name': 'VL53L0X time of flight sensor',
                'init': self.VL53L0X_init,
                'read': self.VL53L0X_all,
                'fields': ['mm'],
                'min': [0],
                'max': [1000],
            },
            'MLX90614': {
                'address': [0x5A],
                'name': 'MLX90614 Passive IR thermometer',
                'init': self.MLX90614_init,
                'read': self.MLX90614_all,
                'fields': ['TEMP'],
                'min': [0],
                'max': [350]},
            'MPR1221': {  # Overrides MLX(0x5A). revise this address:sensor map to sensor:[addr.., options] map
                'address': [0x5A],
                'name': 'MPR1221 capacitive touch sensor',
                'init': self.MPR121_init,
                'read': self.MPR121_all,
                'fields': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
                'min': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'max': [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]},
            'PCF_LCD': {
                'address': [39,63],
                'name': 'PCF_LCD: I2C LCD Display',
                'init': self.PCF_LCD_init,
                'read': self.PCF_LCD_all,
                'fields': ['Dummy'],
                'min': [0],
                'max': [1],
                'config': [{
                    'name': 'text',
                    'options': self.PCF_text_options,
                    'function': self.PCF_LCD_text
                },
                    {
                        'name': 'row',
                        'options': ['1', '2'],
                        'function': self.PCF_LCD_row
                    }
                ]}
        }

        self.controllers = {
            self.MCP5725_ADDRESS: {
                'name': 'MCP4725',
                'init': self.MCP4725_init,
                'write': [['CH0', 0, 4095, 0, self.MCP4725_set]],
            },
        }

        self.special = {
            0x40: {
                'name': 'PCA9685 PWM',
                'init': self.PCA9685_init,
                'write': [['Channel 1', 0, 180, 90, functools.partial(self.PCA9685_set, 1)],
                          # name, start, stop, default, function
                          ['Channel 2', 0, 180, 90, functools.partial(self.PCA9685_set, 2)],
                          ['Channel 3', 0, 180, 90, functools.partial(self.PCA9685_set, 3)],
                          ['Channel 4', 0, 180, 90, functools.partial(self.PCA9685_set, 4)],
                          ],
            }
        }

        self.connected = False

        self.sensormap = {}
        self.addressmap = {}
        for a in range(128):
            self.sensormap[a] = []
        for a in self.namedsensors:
            for addr in self.namedsensors[a]['address']:
                self.sensormap[addr].append(a)
                if addr in self.addressmap:
                    self.addressmap[addr] += '/' + a
                else:
                    self.addressmap[addr] = a


        if 'port' in kwargs:
            self.portname = kwargs.get('port', None)
            try:
                self.fd, self.version, self.connected = self.connectToPort(self.portname)
                if self.connected:
                    # self.fd.setRTS(0)
                    if self.nano:
                        self.REGS = REGISTERS.VERSIONS[self.version][
                            'REGISTERS']  # A map of alphanumeric port names to the 8-bit register locations
                        self.REGSTATES = {}  # Store the last written state of the registers
                        self.SPECIALS = REGISTERS.VERSIONS[self.version]['SPECIALS']
                        for a in ['B', 'C', 'D']:  # Initialize all inputs
                            self.setReg('DDR' + a, 0)  # All inputs
                            self.setReg('PORT' + a, 0)  # No Pullup
                        self.setReg('PORTC', (1 << 4) | (1 << 5))  # I2C Pull-Up
                    else:
                        for a in ['A', 'B', 'C', 'D']:  # Initialize all inputs
                            self.setReg('DDR' + a, 0)
                    return
            except Exception as ex:
                print('Failed to connect to ', self.portname, ex.message)

        elif kwargs.get('autoscan', False):  # Scan and pick a port
            portList = getFreePorts()
            for a in portList:
                if portList[a]:
                    try:
                        self.portname = a
                        self.fd, self.version, self.connected = self.connectToPort(self.portname)
                        if self.connected:
                            # self.fd.setRTS(0)
                            if self.nano:
                                print('kuttypy nano with version', self.version)
                                self.REGS = REGISTERS.VERSIONS[self.version][
                                    'REGISTERS']  # A map of alphanumeric port names to the 8-bit register locations
                                self.REGSTATES = {}  # Store the last written state of the registers
                                self.SPECIALS = REGISTERS.VERSIONS[self.version]['SPECIALS']
                                for a in ['B', 'C', 'D']:  # Initialize all inputs
                                    self.setReg('DDR' + a, 0)  # All inputs
                                    self.setReg('PORT' + a, 0)  # No Pullup
                                self.setReg('PORTC', (1 << 4) | (1 << 5))  # I2C Pull-Up
                            else:
                                for a in ['A', 'B', 'C', 'D']:  # Initialize all inputs
                                    self.setReg('DDR' + a, 0)  # All inputs
                                    self.setReg('PORT' + a, 0)  # No Pullup
                                self.setReg('PORTC', 3)  # I2C Pull-Up
                            return
                    except Exception as e:
                        print(e)
                else:
                    print(a, ' is busy')



    def __get_version__(self, fd):
        fd.flush()
        if self.bootloaderfirmware:
            fd.setRTS(0)
            fd.setDTR(0)
            time.sleep(0.01)
            fd.setRTS(1)
            fd.setDTR(1)
        st = time.time()
        while fd.in_waiting:
            fd.read(fd.in_waiting)
        time.sleep(max(0, 0.25 - (time.time() - st)))
        fd.write(self.GET_VERSION)
        x = fd.read()
        return x

    def get_version(self):
        return self.__get_version__(self.fd)

    def connectToPort(self, portname):
        '''
		connect to a port, and check for the right version
		'''

        try:
            if 'inux' in platform.system():  # Linux based system
                try:
                    # try to lock down the serial port
                    import socket
                    self.blockingSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    self.blockingSocket.bind('\0eyesj2%s' % portname)
                    self.blockingSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    if 'rfcomm' in portname:
                        self.BAUD = 9600
                    fd = serial.Serial(portname, self.BAUD, timeout=0.2)
                    if not fd.isOpen():
                        return None, '', False
                except socket.error as e:
                    # print ('Port {0} is busy'.format(portname))
                    return None, '', False
            # raise RuntimeError("Another program is using %s (%d)" % (portname) )


            else:
                fd = serial.Serial(portname, self.BAUD, timeout=0.5)
            # print ('not on linux',platform.system())

            if (fd.in_waiting):
                fd.flush()
                fd.readall()

        except serial.SerialException as ex:
            print('Port {0} is unavailable: {1}'.format(portname, ex))
            return None, '', False

        version = self.__get_version__(fd)
        self.nano = False
        if len(version) == 1:
            if ord(version) == ord(self.VERSIONNUM):
                return fd, ord(version), True
            elif ord(version) in [ord(self.VERSIONNUM_168P), ord(self.VERSIONNUM_328P),
                                  ord(self.VERSIONNUM_UNO)]:  # assume it is mega32. will work with glitches
                self.nano = True
                return fd, ord(self.VERSIONNUM), True
            elif ord(version) in [42]:  # bluetooth
                self.nano = True
                self.bootloaderfirmware = False
                print('Bluetooth Enabled', portname, self.BAUD, ord(version), 'bootfirm:', self.bootloaderfirmware)
                return fd, ord(self.VERSIONNUM_328P), True
        print('version check failed', len(version), ord(version))
        return None, '', False

    def close(self):
        self.fd.close()
        self.portname = None
        self.connected = False
        if self.blockingSocket:
            self.blockingSocket.shutdown(1)
            self.blockingSocket.close()
            self.blockingSocket = None

    def __sendByte__(self, val):
        """
		transmits a BYTE
		val - byte to send
		"""
        # print (val)
        try:
            if type(val) == int:
                #print('w',val)
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
            ss = self.fd.read(1)
        #print('r', ss)
        except:
            self.connected = False
            print('No byte received. Disconnected?', time.ctime())
            return 0
        if len(ss):
            return Byte.unpack(ss)[0]
        else:
            print('byte communication error.', time.ctime())
            self.get_version()
            return None

    def setReg(self, reg, data):
        # print(reg,data)
        if reg not in self.REGS and type(reg) == str: return False
        self.REGSTATES[reg] = data
        self.__sendByte__(self.WRITEB)
        if reg in self.REGS:
            self.__sendByte__(self.REGS[reg])
        else:
            # print('missing register',reg)
            self.__sendByte__(reg)
        self.__sendByte__(data)

    def getReg(self, reg):
        if (reg not in self.REGS) and type(reg) == str:
            print('unknown register', reg)
            return 0
        self.__sendByte__(self.READB)
        if reg in self.REGS:
            self.__sendByte__(self.REGS[reg])
        else:
            # print('missing register',reg)
            self.__sendByte__(reg)
        val = self.__getByte__()
        self.REGSTATES[reg] = val
        return val

    def readADC(self, ch):  # Read the ADC channel
        self.setReg(self.REGS['ADMUX'], 64 | ch)
        self.setReg(self.REGS['ADCSRA'], 197)  # Enable the ADC
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
        while val < 254:
            addrs.append(val)
            val = self.__getByte__()
        if (val == 254): print('timed out')
        # self.setReg('TWBR',0xFF) #I2C speed minimal. testing purposes

        return addrs

    def I2CWriteBulk(self, address, bytestream):
        self.__sendByte__(self.I2C_WRITE)
        self.__sendByte__(address)  # address
        self.__sendByte__(len(bytestream))  # Total bytes to write. <=255
        for a in bytestream:
            self.__sendByte__(Byte.pack(a))
        tmt = self.__getByte__()
        if tmt:
            return True  # Hasn't Timed out.
        else:
            return False  # Timeout occured

    def I2CReadBulk(self, address, register, total):
        self.__sendByte__(self.I2C_READ)
        self.__sendByte__(address)  # address
        self.__sendByte__(register)  # device register address
        self.__sendByte__(total)  # Total bytes to read. <=255
        data = []
        for a in range(total):
            val = self.__getByte__()
            data.append(val)
        tmt = self.__getByte__()
        return data, True if not tmt else False

    ####################### CSPARK GM COUNTER ###############

    CSGM_ADDRESS = 0x10
    CSGM_START_LOCATION = 100
    CSGM_STOP_LOCATION = 101
    CSGM_RESET_LOCATION = 102
    CSGM_SAVE_LOCATION = 103
    CSGM_VOLTS_READ_LOCATION = 104
    CSGM_VOLTS_WRITE_LOCATION = 105
    CSGM_COUNT_READ_LOCATION = 106
    CSGM_TIMELIMIT_WRITE = 107

    def set_device(self, d):
        self.p = d

    def CSGM_init(self, **kwargs):
        self.CSGM_ADDRESS = kwargs.get('address', self.CSGM_ADDRESS)

    def CSGM_all(self):
        retlist = []
        vals = self.I2CReadBulk(self.CSGM_ADDRESS, self.CSGM_COUNT_READ_LOCATION, 4)
        if vals:
            if len(vals) >= 4:
                retlist.append((vals[3] << 24) | (vals[2] << 16) | (vals[1] << 8) | vals[0])  # long

                vals2, tmt = self.I2CReadBulk(self.CSGM_ADDRESS, self.CSGM_VOLTS_READ_LOCATION, 2)
                if not tmt:
                    if len(vals2) == 2:
                        retlist.append((vals2[1] << 8) | vals2[0])
                        # print(retlist, vals, vals2)
                        return retlist

        return False

    def CSGM_voltage(self, **kwargs):
        self.CSGM_ADDRESS = kwargs.get('address', self.CSGM_ADDRESS)
        vals, tmt = self.I2CReadBulk(self.CSGM_ADDRESS, self.CSGM_VOLTS_READ_LOCATION, 2)
        if not tmt:
            if len(vals) == 2:
                # print('readback:', (vals[1] << 8) | vals[0])
                return (vals[1] << 8) | vals[0]
            else:
                return 0
        else:
            return False

    def CSGM_config(self, volts):
        self.I2CWriteBulk(self.CSGM_ADDRESS,
                          [self.CSGM_VOLTS_WRITE_LOCATION, int(volts) & 0xFF, int(volts >> 8) & 0xFF])

    def CSGM_timelimit(self, t):
        t = int(t)
        self.I2CWriteBulk(self.CSGM_ADDRESS,
                          [self.CSGM_TIMELIMIT_WRITE, int(t) & 0xFF, int(t >> 8) & 0xFF])

    def CSGM_start(self):
        self.I2CWriteBulk(self.CSGM_ADDRESS, [self.CSGM_START_LOCATION])

    def CSGM_stop(self):
        self.I2CWriteBulk(self.CSGM_ADDRESS, [self.CSGM_STOP_LOCATION])

    def CSGM_reset(self):
        self.I2CWriteBulk(self.CSGM_ADDRESS, [self.CSGM_RESET_LOCATION])

    def CSGM_save(self):
        self.I2CWriteBulk(self.CSGM_ADDRESS, [self.CSGM_SAVE_LOCATION])
        time.sleep(0.1)  # Wait for save.

    class KalmanFilter(object):
        '''
		Credits:http://scottlobdell.me/2014/08/kalman-filtering-python-reading-sensor-input/
		'''

        def __init__(self, var, est, initial_values):  # var = process variance. est = estimated measurement var
            self.var = np.array(var)
            self.est = np.array(est)
            self.posteri_estimate = np.array(initial_values)
            self.posteri_error_estimate = np.ones(len(var), dtype=np.float16)

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
    MPU6050_address = 0x68

    def MPU6050_init(self, **kwargs):
        self.MPU6050_address = kwargs.get('address', self.MPU6050_address)
        self.I2CWriteBulk(0x68, [0x1B, 0 << 3])  # Gyro Range . 250
        self.I2CWriteBulk(0x68, [0x1C, 0 << 3])  # Accelerometer Range. 2
        self.I2CWriteBulk(0x68, [0x6B, 0x00])  # poweron
        v, tmt = self.I2CReadBulk(0x68, 0x75, 1)
        self.mag = False
        if v[0] in [0x71, 0x73]:  # MPU9255, MPU9250. Has magnetometer. Enable it.
            self.mag = True
            self.I2CWriteBulk(0x68,
                              [0x37, 0x22])  # INT_PIN_CFG . I2C passthrough enabled. Rescan to detect magnetometer.

    def MPU6050_gyro_range(self, val):
        self.I2CWriteBulk(0x68,
                          [0x1B, val << 3])  # Gyro Range . 250,500,1000,2000 -> 0,1,2,3 -> shift left by 3 positions

    def MPU6050_accel_range(self, val):
        print(val)
        self.I2CWriteBulk(0x68,
                          [0x1C, val << 3])  # Accelerometer Range. 2,4,8,16 -> 0,1,2,3 -> shift left by 3 positions

    def MPU6050_kalman_set(self, val):
        if not val:
            self.MPU6050_kalman = 0
            return
        noise = []
        for a in range(50):
            noise.append(np.array(self.MPU6050_all(disableKalman=True)))
        noise = np.array(noise)
        self.MPU6050_kalman = self.KalmanFilter(1e6 * np.ones(noise.shape[1]) / (10 ** val), np.std(noise, 0) ** 2,
                                                noise[-1])

    def MPU6050_accel(self):
        b, tmt = self.I2CReadBulk(0x68, 0x3B, 6)
        if tmt: return None
        if None not in b:
            return [(b[x * 2 + 1] << 8) | b[x * 2] for x in range(3)]  # X,Y,Z

    def MPU6050_gyro(self):
        b, tmt = self.I2CReadBulk(0x68, 0x3B + 6, 6)
        if tmt: return None
        if None not in b:
            return [(b[x * 2 + 1] << 8) | b[x * 2] for x in range(3)]  # X,Y,Z

    def MPU6050_all(self, disableKalman=False):
        '''
		returns a 7 element list. Ax,Ay,Az,T,Gx,Gy,Gz
		returns None if communication timed out with I2C sensor
		disableKalman can be set to True if Kalman was previously enabled.
		'''
        b, tmt = self.I2CReadBulk(0x68, 0x3B, 14)
        if tmt: return None
        if None not in b:
            if (not self.MPU6050_kalman) or disableKalman:
                return [np.int16((b[x * 2] << 8) | b[x * 2 + 1]) for x in range(7)]  # Ax,Ay,Az, Temp, Gx, Gy,Gz
            else:
                self.MPU6050_kalman.input([np.int16((b[x * 2] << 8) | b[x * 2 + 1]) for x in range(7)])
                return self.MPU6050_kalman.output()

    ######## AK8963 magnetometer attacched to MPU925x #######
    AK8963_ADDRESS = 0x0C
    _AK8963_CNTL = 0x0A

    def AK8963_init(self, **kwargs):
        self.AK8963_ADDRESS = kwargs.get('address', self.AK8963_ADDRESS)
        self.I2CWriteBulk(self.AK8963_ADDRESS, [self._AK8963_CNTL, 0])  # power down mag
        self.I2CWriteBulk(self.AK8963_ADDRESS,
                          [self._AK8963_CNTL, (1 << 4) | 6])  # mode   (0=14bits,1=16bits) <<4 | (2=8Hz , 6=100Hz)

    def AK8963_all(self, disableKalman=False):
        vals, tmt = self.I2CReadBulk(self.AK8963_ADDRESS, 0x03,
                                     7)  # 6+1 . 1(ST2) should not have bit 4 (0x8) true. It's ideally 16 . overflow bit
        if tmt: return None
        ax, ay, az = struct.unpack('hhh', bytes(vals[:6]))
        if not vals[6] & 0x08:
            return [ax, ay, az]
        else:
            return None

    ########## BMP180 ##############
    BMP180_ADDRESS = 0x77
    BMP180_REG_CONTROL = 0xF4
    BMP180_REG_RESULT = 0xF6
    BMP180_CMD_TEMP = 0x2E
    BMP180_CMD_P0 = 0x34
    BMP180_CMD_P1 = 0x74
    BMP180_CMD_P2 = 0xB4
    BMP180_CMD_P3 = 0xF4
    BMP180_oversampling = 0
    BMP180_NUMPLOTS = 2
    BMP180_PLOTNAMES = ['Temperature', 'Pressure', 'Altitude']
    BMP180_name = 'Altimeter BMP180'
    BMP180_params = {'setOversampling': [0, 1, 2, 3]}

    BMP180_c3 = 0
    BMP180_c4 = 0
    BMP180_b1 = 0
    BMP180_c5 = 0
    BMP180_c6 = 0
    BMP180_mc = 0
    BMP180_md = 0
    BMP180_x0 = 0
    BMP180_x1 = 0
    BMP180_x2 = 0
    BMP180_y0 = 0
    BMP180_y1 = 0
    BMP180_y2 = 0
    BMP180_p0 = 0
    BMP180_p1 = 0
    BMP180_p2 = 0
    BMP180_P = 1000
    BMP180_T = 25

    def BMP180_init(self, **kwargs):
        self.BMP180_ADDRESS = kwargs.get('address', self.BMP180_ADDRESS)
        MB = self.__readInt__(0xBA)
        self.BMP180_c3 = 160.0 * pow(2, -15) * self.__readInt__(0xAE)
        self.BMP180_c4 = pow(10, -3) * pow(2, -15) * self.__readUInt__(0xB0)
        self.BMP180_b1 = pow(160, 2) * pow(2, -30) * self.__readInt__(0xB6)
        self.BMP180_c5 = (pow(2, -15) / 160) * self.__readUInt__(0xB2)
        self.BMP180_c6 = self.__readUInt__(0xB4)
        self.BMP180_mc = (pow(2, 11) / pow(160, 2)) * self.__readInt__(0xBC)
        self.BMP180_md = self.__readInt__(0xBE) / 160.0
        self.BMP180_x0 = self.__readInt__(0xAA)
        self.BMP180_x1 = 160.0 * pow(2, -13) * self.__readInt__(0xAC)
        self.BMP180_x2 = pow(160, 2) * pow(2, -25) * self.__readInt__(0xB8)
        self.BMP180_y0 = self.BMP180_c4 * pow(2, 15)
        self.BMP180_y1 = self.BMP180_c4 * self.BMP180_c3
        self.BMP180_y2 = self.BMP180_c4 * self.BMP180_b1
        self.BMP180_p0 = (3791.0 - 8.0) / 1600.0
        self.BMP180_p1 = 1.0 - 7357.0 * pow(2, -20)
        self.BMP180_p2 = 3038.0 * 100.0 * pow(2, -36)
        self.BMP180_T = 25
        print('calib:', self.BMP180_x0, self.BMP180_x1, self.BMP180_x2,
              self.BMP180_y0, self.BMP180_y1, self.BMP180_p0, self.BMP180_p1, self.BMP180_p2)
        self.BMP180_initTemperature()
        self.BMP180_readTemperature()
        self.BMP180_initPressure()

    def __readInt__(self, addr):
        return np.int16(self.__readUInt__(addr))

    def __readUInt__(self, addr):
        vals, tmt = self.I2CReadBulk(self.BMP180_ADDRESS, addr, 2)
        v = 1. * ((vals[0] << 8) | vals[1])
        return v

    def BMP180_initTemperature(self):
        self.I2CWriteBulk(self.BMP180_ADDRESS, [self.BMP180_REG_CONTROL, self.BMP180_CMD_TEMP])
        time.sleep(0.005)

    def BMP180_readTemperature(self):
        vals, tmt = self.I2CReadBulk(self.BMP180_ADDRESS, self.BMP180_REG_RESULT, 2)
        if tmt: return None
        if vals:
            if len(vals) == 2:
                T = (vals[0] << 8) + vals[1]
                a = self.BMP180_c5 * (T - self.BMP180_c6)
                self.BMP180_T = a + (self.BMP180_mc / (a + self.BMP180_md))
                return self.BMP180_T
        return None

    def BMP180_setOversampling(self, num):
        self.BMP180_oversampling = int(num)

    def BMP180_initPressure(self):
        os = [0x34, 0x74, 0xb4, 0xf4]
        delays = [0.005, 0.008, 0.014, 0.026]
        self.I2CWriteBulk(self.BMP180_ADDRESS, [self.BMP180_REG_CONTROL, os[self.BMP180_oversampling]])
        time.sleep(delays[self.BMP180_oversampling])

    def BMP180_readPressure(self):
        vals, tmt = self.I2CReadBulk(self.BMP180_ADDRESS, self.BMP180_REG_RESULT, 3)
        if tmt:
            return None
        if len(vals) == 3:
            P = 1. * (vals[0] << 8) + vals[1] + (vals[2] / 256.0)
            s = self.BMP180_T - 25.0
            x = (self.BMP180_x2 * pow(s, 2)) + (self.BMP180_x1 * s) + self.BMP180_x0
            y = (self.BMP180_y2 * pow(s, 2)) + (self.BMP180_y1 * s) + self.BMP180_y0
            z = (P - x) / y
            self.BMP180_P = (self.BMP180_p2 * pow(z, 2)) + (self.BMP180_p1 * z) + self.BMP180_p0
            return self.BMP180_P
        else:
            return None

    def BMP180_sealevel(self, P, A):
        '''
        given a calculated pressure and altitude, return the sealevel
        '''
        return P / pow(1 - (A / 44330.0), 5.255)

    def BMP180_all(self):
        self.BMP180_initTemperature()
        self.BMP180_readTemperature()
        self.BMP180_initPressure()
        self.BMP180_readPressure()
        return [self.BMP180_P, self.BMP180_T]

    ####### BMP280 ###################
    # https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf
    ## Partly from https://github.com/farmerkeith/BMP280-library/blob/master/farmerkeith_BMP280.cpp
    BMP280_ADDRESS = 118
    BMP280_REG_CONTROL = 0xF4
    BMP280_REG_RESULT = 0xF6
    BMP280_HUMIDITY_ENABLED = False
    _BMP280_humidity_calib = [0] * 6
    BMP280_oversampling = 0
    _BMP280_PRESSURE_MIN_HPA = 0
    _BMP280_PRESSURE_MAX_HPA = 1600
    _BMP280_sea_level_pressure = 1013.25  # for calibration.. from circuitpython library

    def BMP280_init(self, **kwargs):
        self.BMP280_ADDRESS = kwargs.get('address', self.BMP280_ADDRESS)
        b = self.I2CWriteBulk(self.BMP280_ADDRESS, [0xE0, 0xB6])  # reset
        time.sleep(0.1)
        self.BMP280_HUMIDITY_ENABLED = False
        b, tmt = self.I2CReadBulk(self.BMP280_ADDRESS, 0xD0, 1)
        print(b)
        if b is None: return None
        b = b[0]
        if b in [0x58, 0x56, 0x57]:
            print('BMP280. ID:', b)
        elif b == 0x60:
            self.BMP280_HUMIDITY_ENABLED = True
            print('BME280 . includes humidity')
        else:
            print('ID unknown', b)
        # get calibration data
        b, tmt = self.I2CReadBulk(self.BMP280_ADDRESS, 0x88, 24)  # 24 bytes containing calibration data
        coeff = list(struct.unpack('<HhhHhhhhhhhh', bytes(b)))
        coeff = [float(i) for i in coeff]
        self._BMP280_temp_calib = coeff[:3]
        self._BMP280_pressure_calib = coeff[3:]
        self._BMP280_t_fine = 0.

        if self.BMP280_HUMIDITY_ENABLED:
            self.I2CWriteBulk(self.BMP280_ADDRESS, [0xF2, 0b101])  # ctrl_hum. oversampling x 16
            # humidity calibration read
            self._BMP280_humidity_calib = [0] * 6
            val, tmt = self.I2CReadBulk(self.BMP280_ADDRESS, 0xA1, 1)
            self._BMP280_humidity_calib[0] = val[0]  # H1
            coeff, tmt = self.I2CReadBulk(self.BMP280_ADDRESS, 0xE1, 7)
            coeff = list(struct.unpack('<hBbBbb', bytes(coeff)))
            self._BMP280_humidity_calib[1] = float(coeff[0])
            self._BMP280_humidity_calib[2] = float(coeff[1])
            self._BMP280_humidity_calib[3] = float((coeff[2] << 4) | (coeff[3] & 0xF))
            self._BMP280_humidity_calib[4] = float((coeff[4] << 4) | (coeff[3] >> 4))
            self._BMP280_humidity_calib[5] = float(coeff[5])
            print('calibration data: ', self._BMP280_temp_calib, self._BMP280_humidity_calib)

        self.I2CWriteBulk(self.BMP280_ADDRESS, [0xF4, 0xFF])  # ctrl_meas (oversampling of pressure, temperature)

    def _BMP280_calcTemperature(self, adc_t):
        v1 = (adc_t / 16384.0 - self._BMP280_temp_calib[0] / 1024.0) * self._BMP280_temp_calib[1]
        v2 = ((adc_t / 131072.0 - self._BMP280_temp_calib[0] / 8192.0) * (
                adc_t / 131072.0 - self._BMP280_temp_calib[0] / 8192.0)) * self._BMP280_temp_calib[2]
        self._BMP280_t_fine = int(v1 + v2)
        return (v1 + v2) / 5120.0  # actual temperature.

    def _BMP280_calcPressure(self, adc_p, adc_t):
        self._BMP280_calcTemperature(adc_t)  # t_fine has been set now.
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

    def _BMP280_calcHumidity(self, adc_h, adc_t):
        self._BMP280_calcTemperature(adc_t)  # t fine set.
        var1 = float(self._BMP280_t_fine) - 76800.0
        var2 = (self._BMP280_humidity_calib[3] * 64.0 + (self._BMP280_humidity_calib[4] / 16384.0) * var1)
        var3 = adc_h - var2
        var4 = self._BMP280_humidity_calib[1] / 65536.0
        var5 = (1.0 + (self._BMP280_humidity_calib[2] / 67108864.0) * var1)
        var6 = 1.0 + (self._BMP280_humidity_calib[5] / 67108864.0) * var1 * var5
        var6 = var3 * var4 * (var5 * var6)
        humidity = var6 * (1.0 - self._BMP280_humidity_calib[0] * var6 / 524288.0)
        if humidity > 100:
            return 100
        if humidity < 0:
            return 0

        return humidity

    def BMP280_all(self):
        if self.BMP280_HUMIDITY_ENABLED:
            data, tmt = self.I2CReadBulk(self.BMP280_ADDRESS, 0xF7, 8)
        else:
            data, tmt = self.I2CReadBulk(self.BMP280_ADDRESS, 0xF7, 6)
        # os = [0x34,0x74,0xb4,0xf4]
        # delays=[0.005,0.008,0.014,0.026]
        # self.I2CWriteBulk(self.BMP280_ADDRESS,[self.BMP280_REG_CONTROL,os[self.BMP280_oversampling] ])
        # time.sleep(delays[self.BMP280_oversampling])
        if tmt: return None
        if data is None: return None
        if None not in data:
            # Convert pressure and temperature data to 19-bits
            adc_p = (((data[0] & 0xFF) * 65536.) + ((data[1] & 0xFF) * 256.) + (data[2] & 0xF0)) / 16.
            adc_t = (((data[3] & 0xFF) * 65536.) + ((data[4] & 0xFF) * 256.) + (data[5] & 0xF0)) / 16.
            if self.BMP280_HUMIDITY_ENABLED:
                adc_h = (data[6] * 256.) + data[7]
                return [self._BMP280_calcPressure(adc_p, adc_t), self._BMP280_calcTemperature(adc_t),
                        self._BMP280_calcHumidity(adc_h, adc_t)]
            else:
                return [self._BMP280_calcPressure(adc_p, adc_t), self._BMP280_calcTemperature(adc_t), 0]

        return None

    # BH1750
    BH1750_GAIN = 0x11  # 0x11=500 , 0x10 = 1000, 0x13 = 4000mLx
    BH1750_ADDRESS = 35
    BH1750_SCALING = 1.0

    def BH1750_init(self, **kwargs):
        self.BH1750_ADDRESS = kwargs.get('address', self.BH1750_ADDRESS)
        self.BH1750_gain(0)  # 500mLx range
        time.sleep(0.1)
        return self.BH1750_all()

    def BH1750_gain(self, gain):
        self.BH1750_GAIN = [0x11, 0x10, 0x13][gain]
        if gain == 0:  # 500 mLx
            self.BH1750_SCALING = 1.
        else:  # 1000mLx or 4000mLx
            self.BH1750_SCALING = 2.
        self.I2CWriteBulk(self.BH1750_ADDRESS, [self.BH1750_GAIN])  # poweron

    def BH1750_all(self):
        '''
        returns a 2 element list. total,IR
        returns None if communication timed out with I2C sensor
        '''

        b, tmt = self.I2CReadBulk(self.BH1750_ADDRESS, 0x00, 2) #Todo. implement simpleread. 0x00 does nothing.
        if tmt:
            return None
        if None not in b:
            return [float((b[0] << 8) | b[1]) * self.BH1750_SCALING / 2.]  # total lux

    ########## TCS34725 RGB sensor ###########

    _TCS34725_COMMAND_BIT = 0x80
    _TCS34725_REGISTER_STATUS = 0x13
    _TCS34725_REGISTER_CDATA = 0x14
    _TCS34725_REGISTER_RDATA = 0x16
    _TCS34725_REGISTER_GDATA = 0x18
    _TCS34725_REGISTER_BDATA = 0x1a

    _TCS34725_REGISTER_ENABLE = 0x00
    _TCS34725_REGISTER_ATIME = 0x01
    _TCS34725_REGISTER_AILT = 0x04
    _TCS34725_REGISTER_AIHT = 0x06
    _TCS34725_REGISTER_ID = 0x12
    _TCS34725_REGISTER_APERS = 0x0c
    _TCS34725_REGISTER_CONTROL = 0x0f
    _TCS34725_REGISTER_SENSORID = 0x12
    _TCS34725_ENABLE_AIEN = 0x10
    _TCS34725_ENABLE_WEN = 0x08
    _TCS34725_ENABLE_AEN = 0x02
    _TCS34725_ENABLE_PON = 0x01

    _GAINS = (1, 4, 16, 60)
    _CYCLES = (0, 1, 2, 3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60)
    _INTEGRATION_TIME_THRESHOLD_LOW = 2.4
    _INTEGRATION_TIME_THRESHOLD_HIGH = 614.4

    TCS34725_ADDRESS = 41

    def TCS34725_init(self, **kwargs):
        self.TCS34725_ADDRESS = kwargs.get('address', self.TCS34725_ADDRESS)
        enable, tmt = self.I2CReadBulk(self.TCS34725_ADDRESS,
                                       self._TCS34725_COMMAND_BIT | self._TCS34725_REGISTER_ENABLE, 1)
        enable = enable[0]
        self.I2CWriteBulk(self.TCS34725_ADDRESS,
                          [self._TCS34725_REGISTER_ENABLE, enable | self._TCS34725_ENABLE_PON])  #
        time.sleep(0.003)
        self.I2CWriteBulk(self.TCS34725_ADDRESS, [self._TCS34725_COMMAND_BIT | self._TCS34725_REGISTER_ENABLE,
                                                  enable | self._TCS34725_ENABLE_PON | self._TCS34725_ENABLE_AEN | self._TCS34725_ENABLE_AIEN])  #
        self.I2CWriteBulk(self.TCS34725_ADDRESS, [self._TCS34725_COMMAND_BIT | self._TCS34725_REGISTER_APERS, 10])
        self.I2CWriteBulk(self.TCS34725_ADDRESS, [self._TCS34725_COMMAND_BIT | self._TCS34725_REGISTER_ATIME, 256 - 40])

    def TCS34725_gain(self, g):
        self.I2CWriteBulk(self.TCS34725_ADDRESS,
                          [self._TCS34725_COMMAND_BIT | self._TCS34725_REGISTER_CONTROL, g])  # Gain

    def TCS34725_all(self):
        R, tmt = self.I2CReadBulk(self.TCS34725_ADDRESS, self._TCS34725_COMMAND_BIT | self._TCS34725_REGISTER_RDATA, 2)
        G, tmt = self.I2CReadBulk(self.TCS34725_ADDRESS, self._TCS34725_COMMAND_BIT | self._TCS34725_REGISTER_GDATA, 2)
        B, tmt = self.I2CReadBulk(self.TCS34725_ADDRESS, self._TCS34725_COMMAND_BIT | self._TCS34725_REGISTER_BDATA, 2)

        if tmt: return None
        return [R[0] | (R[1] << 8), G[0] | (G[1] << 8), B[0] | (B[1] << 8)]

    def TCS34725_range(self):
        pass

    ####### MS5611 Altimeter ###################
    MS5611_ADDRESS = 119

    def MS5611_init(self, **kwargs):
        self.MS5611_ADDRESS = kwargs.get('address', self.MS5611_ADDRESS)
        self.I2CWriteBulk(self.MS5611_ADDRESS, [0x1E])  # reset
        time.sleep(0.5)
        self._MS5611_calib = np.zeros(6)

        # calibration data.
        # pressure gain, offset . T coeff of P gain, offset. Ref temp. T coeff of T. all unsigned shorts.
        b, tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA2, 2)
        if tmt: return
        self._MS5611_calib[0] = struct.unpack('!H', bytes(b))[0]
        b, tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA4, 2)
        self._MS5611_calib[1] = struct.unpack('!H', bytes(b))[0]
        b, tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA6, 2)
        self._MS5611_calib[2] = struct.unpack('!H', bytes(b))[0]
        b, tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0xA8, 2)
        self._MS5611_calib[3] = struct.unpack('!H', bytes(b))[0]
        b, tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0xAA, 2)
        self._MS5611_calib[4] = struct.unpack('!H', bytes(b))[0]
        b, tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0xAC, 2)
        self._MS5611_calib[5] = struct.unpack('!H', bytes(b))[0]
        print('Calibration for MS5611:', self._MS5611_calib)

    #BMP180 pressure sensor
    BMP180 = None

    def BMP180_init(self, **kwargs):
        import BMP180
        self.BMP180 = BMP180.BMP180(self.I2CReadBulk, self.I2CWriteBulk)

    def BMP180_all(self):
        if self.BMP180 is not None:
            return self.BMP180.getRaw()

    def MS5611_all(self):
        self.I2CWriteBulk(self.MS5611_ADDRESS, [0x48])  # 0x48 Pressure conversion(OSR = 4096) command
        time.sleep(0.01)  # 10mS
        b, tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0x00, 3)  # data.
        D1 = b[0] * 65536 + b[1] * 256 + b[2]  # msb2, msb1, lsb

        self.I2CWriteBulk(self.MS5611_ADDRESS, [0x58])  # 0x58 Temperature conversion(OSR = 4096) command
        time.sleep(0.01)
        b, tmt = self.I2CReadBulk(self.MS5611_ADDRESS, 0x00, 3)  # data.
        D2 = b[0] * 65536 + b[1] * 256 + b[2]  # msb2, msb1, lsb

        dT = D2 - self._MS5611_calib[4] * 256
        TEMP = 2000 + dT * self._MS5611_calib[5] / 8388608
        OFF = self._MS5611_calib[1] * 65536 + (self._MS5611_calib[3] * dT) / 128
        SENS = self._MS5611_calib[0] * 32768 + (self._MS5611_calib[2] * dT) / 256
        T2 = 0;
        OFF2 = 0;
        SENS2 = 0
        if TEMP >= 2000:
            T2 = 0
            OFF2 = 0
            SENS2 = 0
        elif TEMP < 2000:
            T2 = (dT * dT) / 2147483648
            OFF2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 2
            SENS2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 4
            if TEMP < -1500:
                OFF2 = OFF2 + 7 * ((TEMP + 1500) * (TEMP + 1500))
                SENS2 = SENS2 + 11 * ((TEMP + 1500) * (TEMP + 1500)) / 2

        TEMP = TEMP - T2
        OFF = OFF - OFF2
        SENS = SENS - SENS2
        pressure = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 100.0
        cTemp = TEMP / 100.0
        return [pressure, cTemp, 0]

    ### INA3221 3 channel , high side current sensor #############
    INA3221_ADDRESS = 0x41
    _INA3221_REG_CONFIG = 0x0
    _INA3221_SHUNT_RESISTOR_VALUE = 0.1
    _INA3221_REG_SHUNTVOLTAGE = 0x01
    _INA3221_REG_BUSVOLTAGE = 0x02

    def INA3221_init(self, **kwargs):
        self.INA3221_ADDRESS = kwargs.get('address', self.INA3221_ADDRESS)
        self.I2CWriteBulk(self.INA3221_ADDRESS, [self._INA3221_REG_CONFIG, 0b01110101, 0b00100111])  # cont shunt.

    def INA3221_all(self):
        I = [0., 0., 0.]
        b, tmt = self.I2CReadBulk(self.INA3221_ADDRESS, self._INA3221_REG_SHUNTVOLTAGE, 2)
        if tmt: return None
        b[1] &= 0xF8;
        I[0] = struct.unpack('!h', bytes(b))[0]
        b, tmt = self.I2CReadBulk(self.INA3221_ADDRESS, self._INA3221_REG_SHUNTVOLTAGE + 2, 2)
        if tmt: return None
        b[1] &= 0xF8;
        I[1] = struct.unpack('!h', bytes(b))[0]
        b, tmt = self.I2CReadBulk(self.INA3221_ADDRESS, self._INA3221_REG_SHUNTVOLTAGE + 4, 2)
        if tmt: return None
        b[1] &= 0xF8;
        I[2] = struct.unpack('!h', bytes(b))[0]
        return [0.005 * I[0] / self._INA3221_SHUNT_RESISTOR_VALUE, 0.005 * I[1] / self._INA3221_SHUNT_RESISTOR_VALUE,
                0.005 * I[2] / self._INA3221_SHUNT_RESISTOR_VALUE]

    ### SHT21 HUMIDITY TEMPERATURE SENSOR #############
    SHT21_ADDRESS = 0x41
    _SHT21_TEMP = 0xf3
    _SHT21_HUM = 0xf5
    _SHT21_RESET = 0xFE

    def SHT21_init(self, **kwargs):
        self.SHT21_ADDRESS = kwargs.get('address', self.SHT21_ADDRESS)
        self.I2CWriteBulk(self.SHT21_ADDRESS, [self._SHT21_RESET])  # reset
        time.sleep(0.1)

    def SHT21_all(self):
        self.I2CWriteBulk(self.SHT21_ADDRESS, [self._SHT21_TEMP])
        time.sleep(.1)
        self.startI2C()
        self.writeI2C((self.SHT21_ADDRESS << 1) | 1)  # Read
        b = []
        for a in range(2): b.append(self.readI2C(1))
        b.append(self.readI2C(0))
        self.stopI2C()
        temperature, checksum = struct.unpack('>HB', bytes(b))
        return [temperature * 175.72 / 65536.0 - 46.85, 0]

    # AHT 21 Humidity sensor
    AHT21B_ADDRESS = 56
    AHT_CMD_INIT = 0xBE  # initialization cmd
    AHT_CMD_TRIGGER = 0xAC  # trigger measurement cmd
    _buf = b''

    def AHT21B_init(self, **kwargs):
        self.AHT21B_ADDRESS = kwargs.get('address', self.AHT21B_ADDRESS)
        self._buf = bytearray(6)  # not using crc
        self.I2CWriteBulk(self.AHT21B_ADDRESS, [self.AHT_CMD_INIT, 0x08, 0x00])  # calibrate
        time.sleep(0.01)  # Wait initialization process

    def AHT21B_all(self):
        self.I2CWriteBulk(self.AHT21B_ADDRESS, [self.AHT_CMD_TRIGGER, 0x33, 0x00])  # trigger measurement
        time.sleep(0.08)  # Wait measurement process
        self._buf, tmt = self.I2CReadBulk(self.AHT21B_ADDRESS,0x00, 6) #TODO Implement simpleread
        if tmt: return None
        if len(self._buf) == 6:
            hum = self._buf[1] << 12 | self._buf[2] << 4 | self._buf[3] >> 4
            humidity = hum * 100. / 0x100000
            temp = (self._buf[3] & 0xF) << 16 | self._buf[4] << 8 | self._buf[5]
            temp = temp * 200.0 / 0x100000 - 50
            return [humidity, temp]
        return False


    ####### TSL2561 LIGHT SENSOR ###########
    TSL_GAIN = 0x00  # 0x00=1x , 0x01 = 16x
    TSL_TIMING = 0x00  # 0x00=3 mS , 0x01 = 101 mS, 0x02 = 402mS
    TSL2561_ADDRESS = 0x39

    def TSL2561_init(self, **kwargs):
        self.TSL2561_ADDRESS = kwargs.get('address', self.TSL2561_ADDRESS)
        self.I2CWriteBulk(self.TSL2561_ADDRESS, [0x80, 0x03])  # poweron
        self.I2CWriteBulk(self.TSL2561_ADDRESS, [0x80 | 0x01, self.TSL_GAIN | self.TSL_TIMING])
        return self.TSL2561_all()

    def TSL2561_gain(self, gain):
        self.TSL_GAIN = gain << 4
        self.TSL2561_config(self.TSL_GAIN, self.TSL_TIMING)

    def TSL2561_timing(self, timing):
        self.TSL_TIMING = timing
        self.TSL2561_config(self.TSL_GAIN, self.TSL_TIMING)

    def TSL2561_rate(self, timing):
        self.TSL_TIMING = timing
        self.TSL2561_config(self.TSL_GAIN, self.TSL_TIMING)

    def TSL2561_config(self, gain, timing):
        self.I2CWriteBulk(self.TSL2561_ADDRESS,
                          [0x80 | 0x01, gain | timing])  # Timing register 0x01. gain[1x,16x] | timing[13mS,100mS,400mS]

    def TSL2561_all(self):
        '''
        returns a 2 element list. total,IR
        returns None if communication timed out with I2C sensor
        '''
        b, tmt = self.I2CReadBulk(self.TSL2561_ADDRESS, 0x80 | 0x20 | 0x0C, 4)
        if tmt: return None
        if None not in b:
            return [(b[x * 2 + 1] << 8) | b[x * 2] for x in range(2)]  # total, IR

    TSL2591_GAIN = 0x00  # 0x00=1x , 0x10 = medium 25x, 0x20 428x , 0x30 Max 9876x
    TSL2591_TIMING = 0x00  # 0x00=100 mS , 0x05 = 600mS

    TSL2591_ADDRESS = 0x29

    TSL2591_COMMAND_BIT = 0xA0
    # Register (0x00)
    TSL2591_ENABLE_REGISTER = 0x00
    TSL2591_ENABLE_POWERON = 0x01
    TSL2591_ENABLE_POWEROFF = 0x00
    TSL2591_ENABLE_AEN = 0x02
    TSL2591_ENABLE_AIEN = 0x10
    TSL2591_ENABLE_SAI = 0x40
    TSL2591_ENABLE_NPIEN = 0x80

    TSL2591_CONTROL_REGISTER = 0x01
    TSL2591_SRESET = 0x80
    # AGAIN
    TSL2591_LOW_AGAIN = 0X00  # Low gain (1x)
    TSL2591_MEDIUM_AGAIN = 0X10  # Medium gain (25x)
    TSL2591_HIGH_AGAIN = 0X20  # High gain (428x)
    TSL2591_MAX_AGAIN = 0x30  # Max gain (9876x)
    # ATIME
    TSL2591_ATIME_100MS = 0x00  # 100 millis #MAX COUNT 36863
    TSL2591_ATIME_200MS = 0x01  # 200 millis #MAX COUNT 65535
    TSL2591_ATIME_300MS = 0x02  # 300 millis #MAX COUNT 65535
    TSL2591_ATIME_400MS = 0x03  # 400 millis #MAX COUNT 65535
    TSL2591_ATIME_500MS = 0x04  # 500 millis #MAX COUNT 65535
    TSL2591_ATIME_600MS = 0x05  # 600 millis #MAX COUNT 65535

    TSL2591_AILTL_REGISTER = 0x04
    TSL2591_AILTH_REGISTER = 0x05
    TSL2591_AIHTL_REGISTER = 0x06
    TSL2591_AIHTH_REGISTER = 0x07
    TSL2591_NPAILTL_REGISTER = 0x08
    TSL2591_NPAILTH_REGISTER = 0x09
    TSL2591_NPAIHTL_REGISTER = 0x0A
    TSL2591_NPAIHTH_REGISTER = 0x0B
    TSL2591_PERSIST_REGISTER = 0x0C

    TSL2591_ID_REGISTER = 0x12

    TSL2591_STATUS_REGISTER = 0x13

    TSL2591_CHAN0_LOW = 0x14
    TSL2591_CHAN0_HIGH = 0x15
    TSL2591_CHAN1_LOW = 0x16
    TSL2591_CHAN1_HIGH = 0x14

    # LUX_DF = GA * 53   GA is the Glass Attenuation factor
    TSL2591_LUX_DF = 408.0
    TSL2591_LUX_COEFB = 1.64
    TSL2591_LUX_COEFC = 0.59
    TSL2591_LUX_COEFD = 0.86

    # LUX_DF              = 408.0
    TSL2591_MAX_COUNT_100MS = (36863)  # 0x8FFF
    TSL2591_MAX_COUNT = (65535)  # 0xFFFF

    def TSL2591_init(self, **kwargs):
        self.TSL2591_ADDRESS = kwargs.get('address', self.TSL2591_ADDRESS)

        b,tmt = self.I2CReadBulk(self.TSL2591_ADDRESS, self.TSL2591_COMMAND_BIT | self.TSL2591_ID_REGISTER, 1)
        if tmt: return None
        b = b[0]
        if b != 0x50:
            print('TSL. wrong ID:', b)

        self.I2CWriteBulk(self.TSL2591_ADDRESS, [self.TSL2591_COMMAND_BIT | self.TSL2591_ENABLE_REGISTER,
                                                 self.TSL2591_ENABLE_AIEN | self.TSL2591_ENABLE_POWERON | self.TSL2591_ENABLE_AEN | self.TSL2591_ENABLE_NPIEN])
        self.I2CWriteBulk(self.TSL2591_ADDRESS, [self.TSL2591_COMMAND_BIT | self.TSL2591_PERSIST_REGISTER, 0x01])
        self.TSL2591_config(self.TSL2591_GAIN, self.TSL2591_TIMING)
        return self.TSL2591_all()

    def TSL2591_gain(self, gain):
        self.TSL2591_GAIN = gain << 4  # 0x00=1x , 0x10 = medium 25x, 0x20 428x , 0x30 Max 9876x
        self.TSL2591_config(self.TSL2591_GAIN, self.TSL2591_TIMING)

    def TSL2591_timing(self, timing):
        self.TSL2591_TIMING = timing
        self.TSL2591_config(self.TSL2591_GAIN, self.TSL2591_TIMING)

    def TSL2591_config(self, gain, timing):
        self.I2CWriteBulk(self.TSL2591_ADDRESS,
                          [self.TSL2591_COMMAND_BIT | self.TSL2591_CONTROL_REGISTER, gain | timing])

    def TSL2591_Read_CHAN0(self):
        b,tmt = self.I2CReadBulk(self.TSL2591_ADDRESS, self.TSL2591_COMMAND_BIT | self.TSL2591_CHAN0_LOW, 2)
        if tmt: return None
        if None not in b:
            return (b[1] << 8) | b[0]

    def TSL2591_Read_CHAN1(self):
        b,tmt = self.I2CReadBulk(self.TSL2591_ADDRESS, self.TSL2591_COMMAND_BIT | self.TSL2591_CHAN1_LOW, 2)
        if tmt: return None
        if None not in b:
            return (b[1] << 8) | b[0]

    def TSL2591_Read_FullSpectrum(self):
        """Read the full spectrum (IR + visible) light and return its value"""
        data = (self.TSL2591_Read_CHAN1() << 16) | self.TSL2591_Read_CHAN0()
        return data

    def TSL2591_Read_Infrared(self):
        '''Read the infrared light and return its value as a 16-bit unsigned number'''
        data = self.TSL2591_Read_CHAN0()
        return data

    def TSL2591_all(self):
        b,tmt = self.I2CReadBulk(self.TSL2591_ADDRESS, self.TSL2591_COMMAND_BIT | self.TSL2591_CHAN0_LOW, 4)
        if tmt: return None

        channel_0 = (b[1] << 8) | b[0]
        channel_1 = (b[3] << 8) | b[2]

        # channel_0 = self.TSL2591_Read_CHAN0()
        # channel_1 = self.TSL2591_Read_CHAN1()
        # for i in range(0, self.TSL2591_TIMING+2):
        #	time.sleep(0.1)

        atime = 100.0 * self.TSL2591_TIMING + 100.0

        # Set the maximum sensor counts based on the integration time (atime) setting
        if self.TSL2591_TIMING == 0:
            max_counts = self.TSL2591_MAX_COUNT_100MS
        else:
            max_counts = self.TSL2591_MAX_COUNT

        '''
        if channel_0 >= max_counts or channel_1 >= max_counts:
            if(self.TSL2591_GAIN != self.TSL2591_LOW_AGAIN):
                self.TSL2591_GAIN = ((self.TSL2591_GAIN>>4)-1)<<4
                self.TSL2591_config(self.self.TSL2591_GAIN,self.TSL2591_TIMING)
                channel_0 = 0
                channel_1 = 0
                while(channel_0 <= 0 and channel_1 <=0):
                    channel_0 = self.TSL2591_Read_CHAN0()
                    channel_1 = self.TSL2591_Read_CHAN1()
                    time.sleep(0.1)
            else :
                return 0
        '''

        if channel_0 >= max_counts or channel_1 >= max_counts:
            return [(channel_1 & 0xFFFFFFFF << 16) | channel_0, 0, 0]

        again = 1.0
        if self.TSL2591_GAIN == self.TSL2591_MEDIUM_AGAIN:
            again = 25.0
        elif self.TSL2591_GAIN == self.TSL2591_HIGH_AGAIN:
            again = 428.0
        elif self.TSL2591_GAIN == self.TSL2591_MAX_AGAIN:
            again = 9876.0

        cpl = (atime * again) / self.TSL2591_LUX_DF

        lux1 = (channel_0 - (self.TSL2591_LUX_COEFB * channel_1)) / cpl

        lux2 = ((self.TSL2591_LUX_COEFC * channel_0) - (self.TSL2591_LUX_COEFD * channel_1)) / cpl

        return [(channel_1 & 0xFFFFFFFF << 16) | channel_0, lux1, lux2]

    MLX90614_ADDRESS= 0x5A
    def MLX90614_init(self, **kwargs):
        self.MLX90614_ADDRESS = kwargs.get('address', self.MLX90614_ADDRESS)

    def MLX90614_all(self):
        '''
        return a single element list.  None if failed
        '''
        vals, tmt = self.I2CReadBulk(self.MLX90614_ADDRESS, 0x07, 3)
        if tmt: return None
        if vals:
            if len(vals) == 3:
                return [((((vals[1] & 0x007f) << 8) + vals[0]) * 0.02) - 0.01 - 273.15]
            else:
                return None
        else:
            return None

    MCP5725_ADDRESS = 0x60

    def MCP4725_init(self, **kwargs):
        self.MCP5725_ADDRESS = kwargs.get('address', self.MCP5725_ADDRESS)

    def MCP4725_set(self, val):
        '''
        Set the DAC value. 0 - 4095
        '''
        self.I2CWriteBulk(self.MCP5725_ADDRESS, [0x40, (val >> 4) & 0xFF, (val & 0xF) << 4])

    ####################### HMC5883L MAGNETOMETER ###############

    HMC5883L_ADDRESS = 0x1E
    HMC_CONFA = 0x00
    HMC_CONFB = 0x01
    HMC_MODE = 0x02
    HMC_STATUS = 0x09

    # --------CONFA register bits. 0x00-----------
    HMCSamplesToAverage = 0
    HMCSamplesToAverage_choices = [1, 2, 4, 8]

    HMCDataOutputRate = 6
    HMCDataOutputRate_choices = [0.75, 1.5, 3, 7.5, 15, 30, 75]

    HMCMeasurementConf = 0

    # --------CONFB register bits. 0x01-----------
    HMCGainValue = 7  # least sensitive
    HMCGain_choices = [8, 7, 6, 5, 4, 3, 2, 1]
    HMCGainScaling = [1370., 1090., 820., 660., 440., 390., 330., 230.]

    def HMC5883L_init(self, **kwargs):
        self.HMC5883L_ADDRESS = kwargs.get('address', self.HMC5883L_ADDRESS)
        self.__writeHMCCONFA__()
        self.__writeHMCCONFB__()
        self.I2CWriteBulk(self.HMC5883L_ADDRESS, [self.HMC_MODE, 0])  # enable continuous measurement mode

    def __writeHMCCONFB__(self):
        self.I2CWriteBulk(self.HMC5883L_ADDRESS, [self.HMC_CONFB, self.HMCGainValue << 5])  # set gain

    def __writeHMCCONFA__(self):
        self.I2CWriteBulk(self.HMC5883L_ADDRESS, [self.HMC_CONFA,
                                                  (self.HMCDataOutputRate << 2) | (self.HMCSamplesToAverage << 5) | (
                                                      self.HMCMeasurementConf)])

    def HMC5883L_getVals(self, addr, bytes):
        vals = self.I2CReadBulk(self.ADDRESS, addr, bytes)
        return vals

    def HMC5883L_all(self):
        vals = self.HMC5883L_getVals(0x03, 6)
        if vals:
            if len(vals) == 6:
                return [np.int16(vals[a * 2] << 8 | vals[a * 2 + 1]) / self.HMCGainScaling[self.HMCGainValue] for a in
                        range(3)]
            else:
                return False
        else:
            return False



    ####################### QMC5883L MAGNETOMETER ###############

    QMC5883L_ADDRESS = 13
    QMC_scaling = 3000

    def QMC5883L_init(self, **kwargs):
        self.QMC5883L_ADDRESS = kwargs.get('address', self.QMC5883L_ADDRESS)
        self.I2CWriteBulk(self.QMC5883L_ADDRESS, [0x0A, 0x80])  # 0x80=reset. 0x40= rollover
        self.I2CWriteBulk(self.QMC5883L_ADDRESS, [0x0B, 0x01])  # init , set/reset period
        self.QMC_RANGE(1)

    def QMC_RANGE(self, r):  # 0=2G, 1=8G
        if r == 1:
            self.I2CWriteBulk(self.QMC5883L_ADDRESS, [0x09,
                                                      0b001 | 0b000 | 0b100 | 0b10000])  # Mode. continuous|oversampling(512) | rate 50Hz | range(8g)
            self.QMC_scaling = 3000
        elif r == 0:
            self.I2CWriteBulk(self.QMC5883L_ADDRESS, [0x09,
                                                      0b001 | 0b000 | 0b100 | 0b00000])  # Mode. continuous|oversampling(512) | rate 50Hz | range(2g)
            self.QMC_scaling = 12000

    def QMC5883L_getVals(self, addr, numbytes):
        vals, tmt = self.I2CReadBulk(self.QMC5883L_ADDRESS, addr, numbytes)
        return vals

    def QMC5883L_all(self):
        vals = self.QMC5883L_getVals(0x00, 6)
        if vals:
            if len(vals) == 6:
                v = [np.int16((vals[a * 2 + 1] << 8) | vals[a * 2]) / self.QMC_scaling for a in range(3)]
                return v
            else:
                return False
        else:
            return False


    PCA9685_address = 64

    def PCA9685_init(self, **kwargs):
        self.PCA9685_address = kwargs.get('address', self.PCA9685_address)
        prescale_val = int((25000000.0 / 4096 / 60.) - 1)  # default clock at 25MHz
        # self.I2CWriteBulk(self.PCA9685_address, [0x00,0x10]) #MODE 1 , Sleep
        print('clock set to,', prescale_val)
        self.I2CWriteBulk(self.PCA9685_address, [0xFE, prescale_val])  # PRESCALE , prescale value
        self.I2CWriteBulk(self.PCA9685_address, [0x00, 0x80])  # MODE 1 , restart
        self.I2CWriteBulk(self.PCA9685_address, [0x01, 0x04])  # MODE 2 , Totem Pole

        pass

    CH0 = 0x6  # LED0 start register
    CH0_ON_L = 0x6  # channel0 output and brightness control byte 0
    CH0_ON_H = 0x7  # channel0 output and brightness control byte 1
    CH0_OFF_L = 0x8  # channel0 output and brightness control byte 2
    CH0_OFF_H = 0x9  # channel0 output and brightness control byte 3
    CHAN_WIDTH = 4

    def PCA9685_set(self, chan, angle):
        '''
        chan: 1-16
        Set the servo angle for SG90: angle(0 - 180)
        '''
        Min = 180
        Max = 650
        val = int(((Max - Min) * (angle / 180.)) + Min)
        print(chan, angle, val)
        self.I2CWriteBulk(self.PCA9685_address, [self.CH0_ON_L + self.CHAN_WIDTH * (chan - 1), 0])  #
        self.I2CWriteBulk(self.PCA9685_address,
                          [self.CH0_ON_H + self.CHAN_WIDTH * (chan - 1), 0])  # Turn on immediately. At 0.
        self.I2CWriteBulk(self.PCA9685_address, [self.CH0_OFF_L + self.CHAN_WIDTH * (chan - 1),
                                                 val & 0xFF])  # Turn off after val width 0-4095
        self.I2CWriteBulk(self.PCA9685_address, [self.CH0_OFF_H + self.CHAN_WIDTH * (chan - 1), (val >> 8) & 0xFF])

    ## ADS1115
    REG_POINTER_MASK = 0x3
    REG_POINTER_CONVERT = 0
    REG_POINTER_CONFIG = 1
    REG_POINTER_LOWTHRESH = 2
    REG_POINTER_HITHRESH = 3

    REG_CONFIG_OS_MASK = 0x8000
    REG_CONFIG_OS_SINGLE = 0x8000
    REG_CONFIG_OS_BUSY = 0x0000
    REG_CONFIG_OS_NOTBUSY = 0x8000

    REG_CONFIG_MUX_MASK = 0x7000
    REG_CONFIG_MUX_DIFF_0_1 = 0x0000  # Differential P = AIN0, N = AIN1 =default)
    REG_CONFIG_MUX_DIFF_0_3 = 0x1000  # Differential P = AIN0, N = AIN3
    REG_CONFIG_MUX_DIFF_1_3 = 0x2000  # Differential P = AIN1, N = AIN3
    REG_CONFIG_MUX_DIFF_2_3 = 0x3000  # Differential P = AIN2, N = AIN3
    REG_CONFIG_MUX_SINGLE_0 = 0x4000  # Single-ended AIN0
    REG_CONFIG_MUX_SINGLE_1 = 0x5000  # Single-ended AIN1
    REG_CONFIG_MUX_SINGLE_2 = 0x6000  # Single-ended AIN2
    REG_CONFIG_MUX_SINGLE_3 = 0x7000  # Single-ended AIN3

    REG_CONFIG_PGA_MASK = 0x0E00  # bits 11:9
    REG_CONFIG_PGA_6_144V = (0 << 9)  # +/-6.144V range = Gain 2/3
    REG_CONFIG_PGA_4_096V = (1 << 9)  # +/-4.096V range = Gain 1
    REG_CONFIG_PGA_2_048V = (2 << 9)  # +/-2.048V range = Gain 2 =default)
    REG_CONFIG_PGA_1_024V = (3 << 9)  # +/-1.024V range = Gain 4
    REG_CONFIG_PGA_0_512V = (4 << 9)  # +/-0.512V range = Gain 8
    REG_CONFIG_PGA_0_256V = (5 << 9)  # +/-0.256V range = Gain 16

    REG_CONFIG_MODE_MASK = 0x0100  # bit 8
    REG_CONFIG_MODE_CONTIN = (0 << 8)  # Continuous conversion mode
    REG_CONFIG_MODE_SINGLE = (1 << 8)  # Power-down single-shot mode =default)

    REG_CONFIG_DR_MASK = 0x00E0
    REG_CONFIG_DR_8SPS = (0 << 5)  # 8 SPS
    REG_CONFIG_DR_16SPS = (1 << 5)  # 16 SPS
    REG_CONFIG_DR_32SPS = (2 << 5)  # 32 SPS
    REG_CONFIG_DR_64SPS = (3 << 5)  # 64 SPS
    REG_CONFIG_DR_128SPS = (4 << 5)  # 128 SPS
    REG_CONFIG_DR_250SPS = (5 << 5)  # 260 SPS
    REG_CONFIG_DR_475SPS = (6 << 5)  # 475 SPS
    REG_CONFIG_DR_860SPS = (7 << 5)  # 860 SPS

    REG_CONFIG_CMODE_MASK = 0x0010
    REG_CONFIG_CMODE_TRAD = 0x0000
    REG_CONFIG_CMODE_WINDOW = 0x0010

    REG_CONFIG_CPOL_MASK = 0x0008
    REG_CONFIG_CPOL_ACTVLOW = 0x0000
    REG_CONFIG_CPOL_ACTVHI = 0x0008

    REG_CONFIG_CLAT_MASK = 0x0004
    REG_CONFIG_CLAT_NONLAT = 0x0000
    REG_CONFIG_CLAT_LATCH = 0x0004

    REG_CONFIG_CQUE_MASK = 0x0003
    REG_CONFIG_CQUE_1CONV = 0x0000
    REG_CONFIG_CQUE_2CONV = 0x0001
    REG_CONFIG_CQUE_4CONV = 0x0002
    REG_CONFIG_CQUE_NONE = 0x0003

    ADS1115_gains = OrderedDict([('GAIN_TWOTHIRDS', REG_CONFIG_PGA_6_144V), ('GAIN_ONE', REG_CONFIG_PGA_4_096V),
                                 ('GAIN_TWO', REG_CONFIG_PGA_2_048V), ('GAIN_FOUR', REG_CONFIG_PGA_1_024V),
                                 ('GAIN_EIGHT', REG_CONFIG_PGA_0_512V), ('GAIN_SIXTEEN', REG_CONFIG_PGA_0_256V)])
    ADS1115_gain_scaling = OrderedDict(
        [('GAIN_TWOTHIRDS', 0.1875), ('GAIN_ONE', 0.125), ('GAIN_TWO', 0.0625), ('GAIN_FOUR', 0.03125),
         ('GAIN_EIGHT', 0.015625), ('GAIN_SIXTEEN', 0.0078125)])
    ADS1115_scaling = 0.125
    ADS1115_channels = OrderedDict(
        [('UNI_0', 0), ('UNI_1', 1), ('UNI_2', 2), ('UNI_3', 3), ('DIFF_01', '01'), ('DIFF_23', '23')])
    ADS1115_rates = OrderedDict(
        [(8, REG_CONFIG_DR_8SPS), (16, REG_CONFIG_DR_16SPS), (32, REG_CONFIG_DR_32SPS), (64, REG_CONFIG_DR_64SPS),
         (128, REG_CONFIG_DR_128SPS), (250, REG_CONFIG_DR_250SPS), (475, REG_CONFIG_DR_475SPS),
         (860, REG_CONFIG_DR_860SPS)])  # sampling data rate
    ADS1115_DATARATE = 250  # 250SPS [ 8, 16, 32, 64, 128, 250, 475, 860 ]
    ADS1115_GAIN = REG_CONFIG_PGA_4_096V  # +/-4.096V range = Gain 1 . [+-6, +-4, +-2, +-1, +-0.5, +- 0.25]
    ADS1115_CHANNEL = 0  # ref: type_selection
    ADS1115_ADDRESS = 0x48

    def ADS1115_init(self, **kwargs):
        self.ADS1115_ADDRESS = kwargs.get('address', self.ADS1115_ADDRESS)
        self.I2CWriteBulk(self.ADS1115_ADDRESS, [0x80, 0x03])  # poweron

    def ADS1115_gain(self, gain):
        '''
        options : 'GAIN_TWOTHIRDS','GAIN_ONE','GAIN_TWO','GAIN_FOUR','GAIN_EIGHT','GAIN_SIXTEEN'
        '''
        print('setting gain:', str(gain))
        if (type(gain) == int):  # From the UI selectors which return index
            self.ADS1115_GAIN = list(self.ADS1115_gains.items())[gain][1]
            print('set gain with index selection:', self.ADS1115_GAIN)
            self.ADS1115_scaling = list(self.ADS1115_gain_scaling.items())[gain][1]
            print('Scaling factor:', self.ADS1115_scaling)
        else:
            self.ADS1115_GAIN = self.ADS1115_gains.get(gain, self.REG_CONFIG_PGA_4_096V)
            self.ADS1115_scaling = self.ADS1115_gain_scaling.get(gain)
            print('set gain type B:', str(gain), self.ADS1115_GAIN, self.ADS1115_scaling)

    def ADS1115_channel(self, channel):
        '''
        options 'UNI_0','UNI_1','UNI_2','UNI_3','DIFF_01','DIFF_23'
        '''
        self.ADS1115_CHANNEL = int(channel)
        print('channel', channel, self.ADS1115_CHANNEL)

    def ADS1115_rate(self, rate):
        '''
        data rate options 8,16,32,64,128,250,475,860 SPS . string.
        '''
        opts = [8, 16, 32, 64, 128, 250, 475, 860]
        rate = int(rate)
        if rate < len(opts):
            self.ADS1115_DATARATE = opts[rate]

        print('rate:', rate, self.ADS1115_DATARATE)

    def ADS1115_read(self):
        '''
        returns a voltage from ADS1115 channel selected using ADS1115_channel. default UNI_0 (Unipolar from channel 0)
        '''
        if self.ADS1115_CHANNEL in [0, 1, 2, 3]:
            config = (self.REG_CONFIG_CQUE_NONE  # Disable the comparator (default val)
                      | self.REG_CONFIG_CLAT_NONLAT  # Non-latching (default val)
                      | self.REG_CONFIG_CPOL_ACTVLOW  # Alert/Rdy active low   (default val)
                      | self.REG_CONFIG_CMODE_TRAD  # Traditional comparator (default val)
                      | (self.ADS1115_rates.get(self.ADS1115_DATARATE,
                                                self.REG_CONFIG_DR_250SPS))  # 250 samples per second (default)
                      | (self.REG_CONFIG_MODE_SINGLE)  # Single-shot mode (default)
                      | self.ADS1115_GAIN)
            if self.ADS1115_CHANNEL == 0:
                config |= self.REG_CONFIG_MUX_SINGLE_0
            elif self.ADS1115_CHANNEL == 1:
                config |= self.REG_CONFIG_MUX_SINGLE_1
            elif self.ADS1115_CHANNEL == 2:
                config |= self.REG_CONFIG_MUX_SINGLE_2
            elif self.ADS1115_CHANNEL == 3:
                config |= self.REG_CONFIG_MUX_SINGLE_3
            # Set 'start single-conversion' bit
            config |= self.REG_CONFIG_OS_SINGLE
            self.I2CWriteBulk(self.ADS1115_ADDRESS, [self.REG_POINTER_CONFIG, (config >> 8) & 0xFF, config & 0xFF])
            time.sleep(1. / self.ADS1115_DATARATE + .002)  # convert to mS to S

            b, tmt = self.I2CReadBulk(self.ADS1115_ADDRESS, self.REG_POINTER_CONVERT, 2)
            if tmt: return None
            if b is not None:
                x = ((b[0] << 8) | b[1]) * self.ADS1115_scaling * 1e-3
                return [((b[0] << 8) | b[1]) * self.ADS1115_scaling * 1e-3]  # scale and convert to volts

        elif self.ADS1115_CHANNEL in ['01', '23']:
            return [0]

    def VL53L0X_decode_vcsel_period(self, vcsel_period_reg):
        vcsel_period_pclks = (vcsel_period_reg + 1) << 1;
        return vcsel_period_pclks

    VL53L0X_REG_IDENTIFICATION_MODEL_ID = 0x00c0
    VL53L0X_REG_IDENTIFICATION_REVISION_ID = 0x00c2
    VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD = 0x0050
    VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD = 0x0070
    VL53L0X_REG_SYSRANGE_START = 0x000

    VL53L0X_REG_RESULT_INTERRUPT_STATUS = 0x0013
    VL53L0X_REG_RESULT_RANGE_STATUS = 0x0014

    VL53L0X_ADDRESS = 0x29  # 41

    def makeuint16(self,lsb, msb):
        return ((msb & 0xFF) << 8) | (lsb & 0xFF)

    def VL53L0X_init(self, **kwargs):
        self.VL53L0X_ADDRESS = kwargs.get('address', self.VL53L0X_ADDRESS)
        val1,tmt = self.I2CReadBulk(self.VL53L0X_ADDRESS, self.VL53L0X_REG_IDENTIFICATION_MODEL_ID, 1)
        print("Device ID: " + hex(val1[0]))
        val1,tmt = self.I2CReadBulk(self.VL53L0X_ADDRESS, self.VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD, 1)
        print("PRE_RANGE_CONFIG_VCSEL_PERIOD=" + hex(val1[0]) + " decode: " + str(self.VL53L0X_decode_vcsel_period(val1[0])))
        val1,tmt = self.I2CReadBulk(self.VL53L0X_ADDRESS, self.VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD, 1)
        print(
            "FINAL_RANGE_CONFIG_VCSEL_PERIOD=" + hex(val1[0]) + " decode: " + str(self.VL53L0X_decode_vcsel_period(val1[0])))
        val1,tmt = self.I2CReadBulk(self.VL53L0X_ADDRESS, self.VL53L0X_REG_IDENTIFICATION_REVISION_ID, 1)
        print("Revision ID: " + hex(val1[0]))
        if val1[0] == 0x00 or val1[0] == 0xFF:  # No device
            return False
        return True

    def VL53L0X_all(self):
        val1 = self.I2CWriteBulk(self.VL53L0X_ADDRESS, [self.VL53L0X_REG_SYSRANGE_START, 0x01])
        cnt = 0
        while (cnt < 50):  # 1 second waiting time max
            time.sleep(0.005)
            val, tmt = self.I2CReadBulk(self.VL53L0X_ADDRESS, self.VL53L0X_REG_RESULT_RANGE_STATUS, 1)
            if (val[0] & 0x01):
                break
            cnt += 1
        if (cnt == 100):  # timeout
            return None
        if not (val[0] & 0x01):  # Not ready.
            return None

        data, tmt = self.I2CReadBulk(self.VL53L0X_ADDRESS, 0x14, 12)
        # print ("ambient count " + str(makeuint16(data[7], data[6])))
        # print ("signal count " + str(makeuint16(data[9], data[8])))
        d = self.makeuint16(data[11], data[10])
        DeviceRangeStatusInternal = ((data[0] & 0x78) >> 3)
        # print (data,d,DeviceRangeStatusInternal)
        if DeviceRangeStatusInternal != 11:
            d = None

        return [d]

    ######### MPR121 capacitive touch
    MPR121_TOUCH_THRESHOLD_MAX = 0XF0
    MPR121_CHANNEL_NUM = 12
    MPR121_TOUCH_STATUS_REG_ADDR_L = 0X00
    MPR121_TOUCH_STATUS_REG_ADDR_H = 0X01
    MPR121_FILTERED_DATA_REG_START_ADDR_L = 0X04
    MPR121_FILTERED_DATA_REG_START_ADDR_H = 0X05
    MPR121_BASELINE_VALUE_REG_START_ADDR = 0X1E
    MPR121_BASELINE_FILTERING_CONTROL_REG_START_ADDR = 0X2B
    MPR121_THRESHOLD_REG_START_ADDR = 0X41
    MPR121_DEBOUNCE_REG_ADDR = 0X5B

    MPR121_FILTER_AND_GLOBAL_CDC_CFG_ADDR = 0X5C
    MPR121_FILTER_AND_GLOBAL_CDT_CFG_ADDR = 0X5D

    MPR121_ELEC_CHARGE_CURRENT_REG_START_ADDR = 0X5F
    MPR121_ELEC_CHARGE_TIME_REG_START_ADDR = 0X6C

    MPR121_ELEC_CFG_REG_ADDR = 0X5E

    MPR121_ADDRESS = 0x5B

    def MPR121_init(self, **kwargs):
        self.MPR121_ADDRESS = kwargs.get('address', self.MPR121_ADDRESS)
        self.I2CWriteBulk(self.MPR121_ADDRESS, [self.MPR121_FILTER_AND_GLOBAL_CDC_CFG_ADDR, 0x10])  #
        self.I2CWriteBulk(self.MPR121_ADDRESS, [self.MPR121_FILTER_AND_GLOBAL_CDT_CFG_ADDR, 0x23])  #
        self.I2CWriteBulk(self.MPR121_ADDRESS, [self.MPR121_DEBOUNCE_REG_ADDR, 0x22])  # debounce value
        for a in range(self.MPR121_CHANNEL_NUM):
            self.I2CWriteBulk(self.MPR121_ADDRESS, [self.MPR121_THRESHOLD_REG_START_ADDR + 2 * a, 0x08])  # touch
            self.I2CWriteBulk(self.MPR121_ADDRESS,
                              [self.MPR121_THRESHOLD_REG_START_ADDR + 2 * a + 1, 0x08])  # release threshold

        self.I2CWriteBulk(self.MPR121_ADDRESS, [self.MPR121_ELEC_CFG_REG_ADDR, 0x3c])  # start proximity disable mode

    def MPR121_all(self):
        vals, tmt = self.I2CReadBulk(self.MPR121_ADDRESS, self.MPR121_FILTERED_DATA_REG_START_ADDR_L, 26)
        vals = struct.unpack('<hhhhhhhhhhhhh', bytes(vals))
        return vals


    # I2C LCD display
    # commands
    PCF_LCD_ADDRESS = 39
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    # flags for backlight control
    LCD_BACKLIGHT = 0x08
    LCD_NOBACKLIGHT = 0x00

    PCF_En = 0b00000100  # Enable bit
    PCF_Rw = 0b00000010  # Read/Write bit
    PCF_Rs = 0b00000001  # Register select bit

    PCF_row = 1

    def PCF_LCD_init(self):
        self.pcf_lcd_write(0x03)
        self.pcf_lcd_write(0x03)
        self.pcf_lcd_write(0x03)
        self.pcf_lcd_write(0x02)

        self.pcf_lcd_write(self.LCD_FUNCTIONSET | self.LCD_2LINE | self.LCD_5x8DOTS | self.LCD_4BITMODE)
        self.pcf_lcd_write(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYON)
        self.pcf_lcd_write(self.LCD_CLEARDISPLAY)
        self.pcf_lcd_write(self.LCD_ENTRYMODESET | self.LCD_ENTRYLEFT)
        time.sleep(0.2)

    def PCF_LCD_all(self):
        return [0.5]

    def PCF_LCD_text(self,v):
        self.pcf_lcd_display_string("        ",self.PCF_row)
        self.pcf_lcd_display_string(self.PCF_text_options[v],self.PCF_row)
    def PCF_LCD_row(self,r):
        self.PCF_row=r+1


    # clocks EN to latch command
    def pcf_lcd_strobe(self, data):
        self.I2CWriteBulk(self.PCF_LCD_ADDRESS, [data | self.PCF_En | self.LCD_BACKLIGHT])
        time.sleep(.0005)
        self.I2CWriteBulk(self.PCF_LCD_ADDRESS,[(data & ~self.PCF_En) | self.LCD_BACKLIGHT])
        time.sleep(.0001)


    def pcf_lcd_write_four_bits(self, data):
        self.I2CWriteBulk(self.PCF_LCD_ADDRESS,[data | self.LCD_BACKLIGHT])
        self.pcf_lcd_strobe(data)


    # write a command to lcd
    def pcf_lcd_write(self, cmd, mode=0):
        self.pcf_lcd_write_four_bits(mode | (cmd & 0xF0))
        self.pcf_lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))


    # turn on/off the lcd backlight
    def PCF_LCD_backlight(self, state):
        if state in ("on", "On", "ON",1):
            self.I2CWriteBulk(self.PCF_LCD_ADDRESS,[self.LCD_BACKLIGHT])
        elif state in ("off", "Off", "OFF",0):
            self.I2CWriteBulk(self.PCF_LCD_ADDRESS, [self.LCD_NOBACKLIGHT])
        else:
            print("Unknown State!")


    # put string function
    def pcf_lcd_display_string(self, string, line):
        if line == 1:
            self.pcf_lcd_write(0x80)
        if line == 2:
            self.pcf_lcd_write(0xC0)
        if line == 3:
            self.pcf_lcd_write(0x94)
        if line == 4:
            self.pcf_lcd_write(0xD4)

        for char in string:
            self.pcf_lcd_write(ord(char), self.PCF_Rs)


    # clear lcd and set to home
    def pcf_lcd_clear(self):
        self.pcf_lcd_write(self.LCD_CLEARDISPLAY)
        self.pcf_lcd_write(self.LCD_RETURNHOME)



if __name__ == '__main__':
    a = connect(autoscan=True)
    print('version', a.version)
    print('------------')
    if not a.connected:
        sys.exit(1)
    time.sleep(0.01)
    a.setReg('DDRC', 3)
    a.setReg('PORTC', 2)
    time.sleep(1)
    a.setReg('PORTC', 3)
    a.setReg('DDRC', 0)
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
