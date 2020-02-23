#################  Arduino Uno R3 ##########

def genlist(**kwargs):
	return kwargs

VERSIONS = {}

########### 328 PU . Arduino Uno R3

REGISTERS = genlist(
TWAMR	= 0xBD,
TWCR	= 0xBC,
TWDR	= 0xBB,
TWAR	= 0xBA,
TWSR	= 0xB9,
TWBR	= 0xB8,
ASSR	= 0xB6,
OCR2B	= 0xB4,
OCR2A	= 0xB3,
TCNT2	= 0xB2,
TCCR2B	= 0xB1,
TCCR2A	= 0xB0,
OCR1BH	= 0x8B,
OCR1BL	= 0x8A,
OCR1AH	= 0x89,
OCR1AL	= 0x88,
ICR1H	= 0x87,
ICR1L	= 0x86,
TCNT1H	= 0x85,
TCNT1L	= 0x84,
TCCR1C	= 0x82,
TCCR1B	= 0x81,
TCCR1A	= 0x80,
DIDR1	= 0x7F,
DIDR0	= 0x7E,
ADMUX	= 0x7C,
ADCSRB	= 0x7B,
ADCSRA	= 0x7A,
ADCH	= 0x79,
ADCL	= 0x78,
TIMSK2	= 0x70,
TIMSK1	= 0x6F,
TIMSK0	= 0x6E,
OCR0B	= 0x48,
OCR0A	= 0x47,
TCNT0	= 0x46,
TCCR0B	= 0x45,
TCCR0A	= 0x44,
GTCCR	= 0x43,
EEARH	= 0x42,
EEARL	= 0x41,
EEDR	= 0x40,
EECR	= 0x3F,
GPIOR0	= 0x3E,
EIMSK	= 0x3D,
EIFR	= 0x3C,
TIFR2	= 0x37,
TIFR1	= 0x36,
TIFR0	= 0x35,
PORTD	= 0x2B,
DDRD	= 0x2A,
PIND	= 0x29,
PORTC	= 0x28,
DDRC	= 0x27,
PINC	= 0x26,
PORTB	= 0x25,
DDRB	= 0x24,
PINB	= 0x23,

)


SPECIALS = genlist(
PB1 = 'OC1A',
PB2 = 'OC1B',
PB3 = 'OC2',
PD4 = 'T0',
PD5 = 'T1',
PC0 = 'ADC0',
PC1 = 'ADC1',
PC2 = 'ADC2',
PC3 = 'ADC3',
)
for a in ['GND','VCC','RESET','5V','3V3','SCL','SDA','AREF','ADC6','ADC7','VIN']:
	SPECIALS[a] = 'FIXED'
################################
VERSIONNUM = 100
ADC = ['PC0','PC1','PC2','PC3','PC4','PC5']
EXAMPLES = 'atmega328p'
RESTRICTED = ['UBRRL']






