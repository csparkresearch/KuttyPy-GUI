#!/usr/bin/python3
'''
A record (line of text) consists of six fields (parts) that appear in order from left to right:

Start code, one character, an ASCII colon ':'.
Byte count, two hex digits, indicating the number of bytes (hex digit pairs) in the data field. The maximum byte count is 255 (0xFF). 16 (0x10) and 32 (0x20) are commonly used byte counts.
Address, four hex digits, representing the 16-bit beginning memory address offset of the data. The physical address of the data is computed by adding this offset to a previously established base address, thus allowing memory addressing beyond the 64 kilobyte limit of 16-bit addresses. The base address, which defaults to zero, can be changed by various types of records. Base addresses and address offsets are always expressed as big endian values.
Record type (see record types below), two hex digits, 00 to 05, defining the meaning of the data field.
Data, a sequence of n bytes of data, represented by 2n hex digits. Some records omit this field (n equals zero). The meaning and interpretation of data bytes depends on the application.
Checksum, two hex digits, a computed value that can be used to verify the record has no errors.
'''
import time
import serial,struct
Byte =     struct.Struct("B") # size 1


class Uploader(object):
	STK_OK = 0x10
	STK_INSYNC = 0x14  # ' '
	CRC_EOP = 0x20  # 'SPACE'
	STK_GET_SYNC = 0x30  # '0'
	STK_SET_PARAMETER = 0x40  # '@'
	STK_GET_PARAMETER = 0x41  # 'A'
	STK_SET_DEVICE = 0x42  # 'B'
	FLASH_MEMORY = 0x46  #'F'
	STK_ENTER_PROGMODE = 0x50  # 'P'
	STK_LEAVE_PROGMODE = 0x51  # 'Q'
	STK_CHIP_ERASE = 0x52  # 'R'
	STK_LOAD_ADDRESS = 0x55  # 'U'
	STK_PROG_FLASH = 0x60  # '`'
	STK_PROG_DATA = 0x61  # 'a'
	STK_PROG_FUSE = 0x62  # 'b'
	STK_PROG_LOCK = 0x63  # 'c'
	STK_PROG_PAGE = 0x64  # 'd'
	STK_PROG_FUSE_EXT = 0x65  # 'e'
	STK_READ_FLASH = 0x70  # 'p'
	STK_READ_DATA = 0x71  # 'q'
	STK_READ_FUSE = 0x72  # 'r'
	STK_READ_LOCK = 0x73  # 's'
	STK_READ_PAGE = 0x74  # 't'
	STK_READ_SIGN = 0x75  # 'u'
	STK_READ_OSCCAL = 0x76  # 'v'
	STK_READ_FUSE_EXT = 0x77  # 'w'
	STK_READ_OSCCAL_EXT = 0x78  # 'x'


	SYNC = [STK_GET_SYNC, CRC_EOP]
	CHIP_ERASE = [STK_CHIP_ERASE, CRC_EOP]
	ENTER_PROG_MODE = [STK_ENTER_PROGMODE, CRC_EOP]
	EXIT_PROG_MODE = [STK_LEAVE_PROGMODE, CRC_EOP]
	INSYNC = [STK_INSYNC, STK_OK]
	def __init__(self, sock, retry=3, hexfile="",logger=None):
		self.sock = sock
		self.hexfile = hexfile
		self.retry = retry
		if logger:
			self.log = logger.emit
		else:
			self.log = print

	def spi_transaction(self, codes, bytesreply=0):
		n = 0
		retry = True
		tx_complete = len(codes) * 0.25 + 1
		while retry:
			self.sock.write(codes)
			time.sleep(tx_complete/1000.0)
			reply = list(self.sock.read(size=bytesreply + 2)) #bytesreply + INSYNC + OK
			#print('reply', len(reply), reply)
			if not reply or ([reply[0], reply[-1]] != self.INSYNC):
				if n < self.retry:
					n += 1
					self.log('retrying...%s'%reply)
					continue
				else:
					raise Exception("SPI","Not in sync")
					return
			if len(reply) == 3:
				return reply[1]
			elif len(reply) > 3:
				return reply[1:-1]
			return
	
	def sync(self):
		self.sock.write(b'0 ')#\x30\x20')
		x = self.sock.read(2)
		print('sync',x)

	
	def program(self):
		st = time.time()
		print('start programming. flush:',self.sock.read(1))
		#self.sync()
		print('synced',(time.time()-st)*1000)
		# print("erasing...")
		# self.spi_transaction(CHIP_ERASE)

		self.log("Entering programming mode")
		self.spi_transaction(self.ENTER_PROG_MODE)

		# start with page address 0
		address = 0
		prg_length = 0
		data = list()
		print('entered program mode',(time.time()-st)*1000)

		# open the hex file
		with open(self.hexfile, "rb") as hexfile:
			while True:
				row = hexfile.readline()
				# check EOF
				# Include only program data
				if row[7:9] != b'01':
					hexrow = row[9:][:-4]
					data.extend([int(hexrow[b:b + 2], 16) for b in range(len(hexrow))[::2]])
				if not data:
					self.log("End program")
					break
				if len(data) >= 128 or row[7:9] == b'01':
					size = len(data[:128])
					prg_length += size
					#print('writing', len(data), (time.time() - st) * 1000)

					self.spi_transaction([self.STK_LOAD_ADDRESS, address % 256, int(address / 256), self.CRC_EOP])
					self.log("Writing @ %s:%s, block size:%s"%( int(address / 256), address % 256, size ))
					address += 64
					packet = [self.STK_PROG_PAGE, 0, size, self.FLASH_MEMORY] + data[:128] + [self.CRC_EOP]
					self.spi_transaction(packet)
					#print ('writing', len(packet), packet)
					data = data[128:]

		self.spi_transaction(self.EXIT_PROG_MODE)
		self.sync()
		#print("Finished. Program size %s bytes in %.1f mS"%(prg_length,(time.time()-st)*1000))
		self.log("Finished. Program size %s bytes in %.1f mS"%(prg_length,(time.time()-st)*1000))

	def verify(self):
		print('entered verify mode')
		self.sync()
		self.spi_transaction(self.ENTER_PROG_MODE)
		address = 0
		with open(self.hexfile, "rb") as hexfile:
			while True:
				self.spi_transaction([self.STK_LOAD_ADDRESS, address % 256, int(address / 256), self.CRC_EOP])
	
				data = list()
				for i in range(8):
					hexrow = hexfile.readline()[9:][:-4]
					data.extend([int(hexrow[b:b + 2], 16) for b in range(len(hexrow))[::2]])
	
				size = len(data)
				self.log("Reading program page( 128 bytes / 64 words ) Starts at:%s:%s"%(int(address / 256), address % 256))
				page = self.spi_transaction([self.STK_READ_PAGE, 0, 0x80, self.FLASH_MEMORY, self.CRC_EOP], 0x80)
				if data != page[:size]:
					self.log("Error! Differs from Hex file")
					self.spi_transaction(self.EXIT_PROG_MODE)
					return False

				if size != 0x80:
					self.log("Program check OK.")
					self.spi_transaction(self.EXIT_PROG_MODE)
					return True
				address += 64


if __name__ == '__main__':
	ser = serial.Serial('/dev/ttyUSB0', baudrate=38400, timeout=.5)
	ser.setRTS(0)
	ser.setRTS(1)
	time.sleep(0.02)
	dude = Uploader(ser, hexfile="./blink.hex")
	dude.program()
	dude.verify()
	ser.setRTS(0)
	ser.setRTS(1)
	time.sleep(0.02)
