/*
 * SHT71.c
 *
 * Created: 12/29/2016 11:56:57 PM
 *  Author: Will Choi
 */ 

 #include "SHT71.h"
 #include <avr/io.h>

 #define F_CPU 8000000UL
 #include <util/delay.h>

#define SCKPORT 4
#define VDDPORT 5
#define GNDPORT 6
#define DATAPORT 7
#define COMMAND_READ_TEMPTERATURE 0b00000011
#define COMMAND_READ_HUMIDITY 0b00000101

unsigned char crc_ = 0;

void InitializeSensor() {
	// Set ports 0 and 3 (SCK, and DATA respectively) as "output".
	DDRB = _BV(SCKPORT) | _BV(VDDPORT) | _BV(GNDPORT) | _BV(DATAPORT);
		
	// DATA line starts HIGH.
	PORTB |= _BV(DATAPORT);

	// Supply voltage to Vdd.
	PORTB |= _BV(VDDPORT);

	// Wait for the sensor to set up.
	delay_ms(20);
}

static void ClockUp() {
	// Source current in port E0.
	PORTB |= _BV(SCKPORT);
	asm("nop");
	asm("nop");
	asm("nop");
}

static void ClockDown() {
	// Sink current in port E0.
	PORTB &= ~_BV(SCKPORT);
	asm("nop");
	asm("nop");
	asm("nop");
}

static void DataUp() {
	PORTB |= _BV(DATAPORT);
	asm("nop");
	asm("nop");
	asm("nop");
}

static void DataDown() {
	PORTB &= ~_BV(DATAPORT);
	asm("nop");
	asm("nop");
	asm("nop");
}

static void IssueTransmitStart() {
	ClockUp();
	DataDown();
	ClockDown();
	ClockUp();
	DataUp();
	ClockDown();
	DataDown();
}

static void StartCRC() {
	crc_ = 0b00001111 & 0; /* TODO status register */
}

static unsigned char EndCRC() {
	unsigned char temp = 0;
	temp |= (crc_ << 7) & (1 << 7);
	temp |= (crc_ << 5) & (1 << 6);
	temp |= (crc_ << 3) & (1 << 5);
	temp |= (crc_ << 1) & (1 << 4);
	temp |= (crc_ >> 1) & (1 << 3);
	temp |= (crc_ >> 3) & (1 << 2);
	temp |= (crc_ >> 5) & (1 << 1);
	temp |= (crc_ >> 7) & (1);
	return temp;
}

static void CalcCRCBitOne() {
	// If bit 7 isn't set,
	if((crc_ & 0b10000000) == 0) {
		crc_ <<= 1;

		// Invert bits 4 and 5.
		crc_ ^= 1 << 4;
		crc_ ^= 1 << 5;

		// Set bit 0 to 1.
		crc_ |= 1;
	} else {
		crc_ <<= 1;
		crc_ &= ~0b00000001;
	}
}

static void CalcCRCBitZero() {
	// If bit 7 is set,
	if(crc_ & 0b10000000) {
		crc_ <<= 1;

		// Invert bits 4 and 5.
		crc_ ^= 1 << 4;
		crc_ ^= 1 << 5;

		// Set bit 0 to 1.
		crc_ |= 1;
	} else {
		crc_ <<= 1;
		crc_ &= ~0b00000001;
	}
}

unsigned char IssueCommand(const unsigned char command) {
	for(unsigned char i = 0; i < 8; ++i) {
		if(command & (1 << (7-i))) {
			DataUp();
			ClockUp();
			ClockDown();
			if(i != 7) {
				DataDown();
			}
			CalcCRCBitOne();
		}
		else {
			ClockUp();
			ClockDown();
			CalcCRCBitZero();
		}
	}

	// Read ACK bit.
	PORTB &= ~_BV(DATAPORT);
	DDRB &= ~_BV(DATAPORT);
	ClockUp();
	if(PINB & _BV(PINB3)) {
		// ACK not received
		PORTB |= _BV(DATAPORT);
		DDRB |= _BV(DATAPORT);
		ClockDown();
		return 1;
	}
	ClockDown();
	return 0;
}

static unsigned char ReadSensor(double* value, unsigned char command) {
	PORTD = 160;	
	IssueTransmitStart();
	StartCRC();
	if(IssueCommand(command)) {
		return 1;
	}
	PORTD = 128;	
	// Loop until sensor pulls DATA low.
	loop_until_bit_is_clear(PINB, PINB3);
	
	unsigned char high = 0, low = 0, crc = 0;
	for(char i = 0; i < 8; ++i) {
		ClockUp();
		if(PINB & _BV(PINB3)) {
			high |= 1 << (7-i);
			CalcCRCBitOne();
		}
		else {
			CalcCRCBitZero();
		}
		ClockDown();
	}
	
	// Send ACK.
	DDRB |= _BV(DATAPORT);
	ClockUp();
	ClockDown();
	
	DDRB &= ~_BV(DATAPORT);
	for(char i = 0; i < 8; ++i) {
		ClockUp();
		if(PINB & _BV(PINB3)) {
			low |= 1 << (7-i);
			CalcCRCBitOne();
		}
		else {
			CalcCRCBitZero();
		}
		ClockDown();
	}

	// Send ACK.
	DDRB |= _BV(DATAPORT);
	ClockUp();
	ClockDown();

	DDRB &= ~_BV(DATAPORT);
	for(char i = 0; i < 8; ++i) {
		ClockUp();
		if(PINB & _BV(PINB3)) {
			crc |= 1 << (7-i);
		}
		ClockDown();
	}

	// Send ACK.
	DDRB |= _BV(DATAPORT);
	DataUp();
	ClockUp();
	ClockDown();

	uint16_t raw_value = 0;
	raw_value |= low;
	raw_value |= high << 8;
	*value = (double)raw_value;

	PORTD = 0;	

	return 0;
}

unsigned char ReadTemperature(double* temperature) {
	double raw_value;
	unsigned char return_val = ReadSensor(&raw_value, COMMAND_READ_TEMPTERATURE);
	if(!return_val) {
		*temperature = -40.1 + 0.01 * raw_value;
	}
	return return_val;
}

unsigned char ReadHumidity(double* humidity, double temperature) {
	double raw_value;
	unsigned char return_val = ReadSensor(&raw_value, COMMAND_READ_HUMIDITY);
	if(!return_val) {
		double rh_linear = -2.0468 + 0.0367 * raw_value + -1.5955E-6 * raw_value * raw_value;
		*humidity = (temperature - 25.0) * (0.01 + 0.00008 * raw_value) + rh_linear;
	}
	return return_val;
}
