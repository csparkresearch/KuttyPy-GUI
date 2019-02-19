def genlist(**kwargs):
	return kwargs

ATMEGA32_REGISTERS = genlist(
UBRRL	= 0X29,
UCSRB	= 0X2A,
UCSRA	= 0X2B,
UDR	= 0X2C,
SPCR	= 0X2D,
SPSR	= 0X2E,
SPDR	= 0X2F,
PIND	= 0x30,       # Port D input
DDRD	= 0x31,	# Port D direction
PORTD	= 0x32,		# Port D output
PINC	= 0x33,
DDRC	= 0x34,
PORTC	= 0x35,
PINB	= 0x36,
DDRB	= 0x37,
PORTB	= 0x38,
PINA	= 0x39,
DDRA	= 0x3A,
PORTA	= 0x3B,
EECR	= 0X3C,
EEDR	= 0X3D,
EEARL	= 0X3E,
EEARH	= 0X3F,

TWBR    = 0X20,
TWSR    = 0X21,
TWAR    = 0X22,
TWDR    = 0X23,

ADCL	= 0X24,       # ADC data
ADCH	= 0X25,
ADCSRA	= 0X26,	# ADC status/control
ADMUX	= 0X27,    # ADC channel, reference
ACSR	= 0X28,



OCR2	= 0X43,		# Timer/Counter 2  Output Compare  Reg
TCNT2	= 0X44	,	# Counter2 
TCCR2	= 0x45,		# Timer/Counter 2 control reg
ICR1L	= 0X46,
ICR1H	= 0X47,
OCR1BL	= 0X48,
OCR1BH	= 0X49,
OCR1AL	= 0X4A,
OCR1AH	= 0X4B,
TCNT1L	= 0X4C,
TCNT1H	= 0X4D,
TCCR1B	= 0X4E,
TCCR1A	= 0x4F,
SFIOR	= 0X50,

TCNT0	= 0x52	,	# Timer/ Counter 0
TCCR0	= 0x53,
MCUCSR	= 0X54,
MCUCR	= 0X55,
TWCR	= 0X56,
SPMCR	= 0X57,
TIFR	= 0X58,
TIMSK	= 0X59,
GIFR	= 0X5A,
GICR	= 0X5B,
OCR0	= 0x5C,
SPL		= 0X5D,
SPH		= 0x5E,
SREG	= 0X5F,
)


ATMEGA32_SPECIALS = genlist(
PD5 = 'OC1A',
PD7 = 'OC2',
PB3 = 'OC0',
PB1 = 'T1',
PA0 = 'ADC0',
PA1 = 'ADC1',
PA2 = 'ADC2',
PA3 = 'ADC3',
PA4 = 'ADC4',
PA5 = 'ADC5',
PA6 = 'ADC6',
PA7 = 'ADC7',
)
################################
VERSION_ATMEGA32 = 99
VERSIONS = {}
VERSIONS[99] = {
'REGISTERS':ATMEGA32_REGISTERS,
'SPECIALS':ATMEGA32_SPECIALS,
'examples directory':'atmega32',
'RESTRICTED_REGISTERS':['UBRRL']
}




